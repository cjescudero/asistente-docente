"""Una misma cita tras mover, modificar, retirar o consolidar un documento."""
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from docencia.catalog import classify, read_catalog, reconcile
from docencia.knowledge import refresh_knowledge, repair_markdown
from docencia.organization import apply_organization, plan_organization
from docencia.project import initialize_course
from docencia.project_map import register_map
from scripts.build_graph import build_graph
from scripts.validate_library import validate_library


class CourseKnowledgeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.course = Path(temp.name).resolve()
        self.config = {"sources": ["Programa", "Temas"], "generated": ["Producción"],
                       "submissions": ["Trabajos privados"]}
        initialize_course(self.course, spaces=self.config, include=["Programa", "Temas"])
        self.guide = self.course / "Producción/mapa"
        self.source = self.course / "Programa/guía.md"
        self.source.write_text("# Guía\n\nNota sobre el concepto de evidencia.", encoding="utf-8")
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.registry = {"schema_version": 2, "title": "Evidencia", "course": None,
                         "source_roots": {"programa": "../../Programa"},
                         "sources": [{"id": "guia", "title": "Guía", "path": "guía.md", "kind": "apuntes",
                                      "course": None, "currency": "vigente", "access": "docente",
                                      "reading": "completa", "reviewed_locators": ["Guía"],
                                      "sha256": self.digest, "page": "reservado/ficha.md", "root": "programa"}],
                         "pages": [{"path": "reservado/ficha.md", "title": "Ficha", "kind": "apuntes",
                                    "access": "docente", "source_ids": ["guia"]},
                                   {"path": "reservado/tema.md", "title": "Tema", "kind": "tema",
                                    "access": "docente", "source_ids": []}]}
        (self.guide / "reservado").mkdir(parents=True)
        for name in ("LEEME.md", "log.md", "incidencias.md", "index.md"):
            (self.guide / name).write_text("# Índice\n\n[Conceptos](reservado/tema.md)", encoding="utf-8")
        (self.guide / "reservado/ficha.md").write_text("# Ficha\n\n[Fuente](../../../Programa/gu%C3%ADa.md#inicio)", encoding="utf-8")
        (self.guide / "reservado/tema.md").write_text("# Tema\n\n[Referencia](ficha.md)", encoding="utf-8")
        self.file = self.guide / "fuentes.json"
        self.file.write_text(json.dumps(self.registry), encoding="utf-8")
        register_map(self.course, self.guide)
        self.mid = read_catalog(self.course)["wiki"]["sources"]["guia"]["material_id"]

    def test_manual_move_repairs_links_and_html_then_changed_content_marks_dependents(self):
        graph = self.guide / "grafo-docente.html"
        reader = self.guide / "index.html"
        build_graph(self.guide, graph, wiki_output=reader)
        target = self.course / "Temas/Nueva guía.md"
        self.source.rename(target)
        reconcile(self.course)
        report = refresh_knowledge(self.course)
        self.assertEqual(report["repaired_links_to"], ["guia"])
        self.assertEqual(report["changed_sources"], [])
        self.assertEqual(self.registry["sources"][0]["sha256"], self.digest)
        self.assertIn("Nueva%20gu%C3%ADa.md#inicio", (self.guide / "reservado/ficha.md").read_text(encoding="utf-8"))
        self.assertIn("Nueva%20gu%C3%ADa.md", reader.read_text(encoding="utf-8"))
        self.assertEqual(validate_library(self.guide)["status"], "ok")
        self.assertEqual(read_catalog(self.course)["wiki"]["sources"]["guia"]["content_version"], 1)
        self.assertEqual(refresh_knowledge(self.course)["repaired_links_to"], [])
        target.write_text("Otra explicación", encoding="utf-8")
        reconcile(self.course)
        self.assertEqual(refresh_knowledge(self.course)["affected_pages"], ["reservado/ficha.md", "reservado/tema.md"])
        self.assertEqual(read_catalog(self.course)["materials"][self.mid]["content_version"], 2)
        self.assertEqual(validate_library(self.guide)["status"], "invalid")

    def test_interrupted_wiki_repair_can_be_retried_without_rewriting_the_page(self):
        target = self.course / "Temas/nuevo.md"
        self.source.rename(target)
        reconcile(self.course)
        from docencia.knowledge import _replace_config
        def interrupted(path, text):
            if path == self.file:
                raise OSError("corte simulado")
            _replace_config(path, text)
        with patch("docencia.knowledge._replace_config", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "corte simulado"):
                refresh_knowledge(self.course)
        page = self.guide / "reservado/ficha.md"
        stat_after_write = page.stat().st_mtime_ns
        refresh_knowledge(self.course)
        self.assertEqual(stat_after_write, page.stat().st_mtime_ns)
        self.assertEqual(validate_library(self.guide)["status"], "ok")

    def test_audience_change_blocks_student_view_even_without_content_change(self):
        self.registry["sources"][0]["access"] = "estudiante"
        self.file.write_text(json.dumps(self.registry), encoding="utf-8")
        classify(self.course, self.mid, primary="Teoría", confirmed=True, evidence="Decisión docente", access="docente")
        self.assertIn("guia", refresh_knowledge(self.course)["changed_sources"])
        report = validate_library(self.guide)
        self.assertEqual(report["status"], "invalid")
        graph = self.guide / "grafo-estudiante.html"
        with self.assertRaises(ValueError):
            build_graph(self.guide, graph, audience="estudiante")
        self.assertFalse(graph.exists())

    def test_promotion_is_new_source_but_submissions_never_enter_knowledge(self):
        draft = self.course / "Producción/apuntes.md"
        draft.write_text("Una síntesis", encoding="utf-8")
        (self.course / "Trabajos privados/confidencial.md").write_text("Privado", encoding="utf-8")
        reconcile(self.course)
        mid = next(i for i,r in read_catalog(self.course)["materials"].items() if r["path"] == "Producción/apuntes.md")
        plan = plan_organization(self.course, [{"material_id": mid, "destination": "Temas/apuntes.md"}], mode="promote")
        apply_organization(self.course, plan["plan_id"], accepted="all")
        report = refresh_knowledge(self.course)
        self.assertEqual(report["new_sources"], [mid])
        self.assertEqual(json.loads(self.file.read_text(encoding="utf-8"))["sources"], self.registry["sources"])
        self.assertFalse(any("confidencial" in str(r["path"]) for r in read_catalog(self.course)["materials"].values()))

    def test_notes_stay_out_of_existing_map_student_graph_and_reader(self):
        from scripts.build_wiki import build_wiki
        initialize_course(self.course, notes="Cuaderno")
        note = self.course / "Cuaderno/idea.md"
        note.write_text("BORRADOR_DOCENTE_SINTETICO", encoding="utf-8")
        graph = self.guide / "alumnado.html"
        build_graph(self.guide, graph, audience="estudiante")
        original_graph = graph.read_bytes()
        self.assertNotIn(b"BORRADOR_DOCENTE_SINTETICO", original_graph)
        self.assertEqual(refresh_knowledge(self.course)["new_sources"], [])
        reader = self.guide / "lector.html"
        build_wiki(self.guide, reader)
        self.assertNotIn("BORRADOR_DOCENTE_SINTETICO", reader.read_text(encoding="utf-8"))
        (self.guide / "index.md").write_text("[Idea](../../Cuaderno/idea.md)", encoding="utf-8")
        original_open = Path.open

        def guard(path, *args, **kwargs):
            if path.resolve().is_relative_to(note.parent):
                raise AssertionError("Se ha abierto un archivo del cuaderno.")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guard):
            report = validate_library(self.guide)
            self.assertIn("index.md", report["project_policy"]["affected_pages"])
            with self.assertRaises(ValueError):
                build_graph(self.guide, graph, audience="estudiante")
            self.assertEqual(graph.read_bytes(), original_graph)
            self.assertEqual(validate_library(note.parent)["status"], "invalid")
            (self.guide / "index.md").write_text("# Índice", encoding="utf-8")
            self.registry["source_roots"]["notas"] = "../../Cuaderno"
            self.file.write_text(json.dumps(self.registry), encoding="utf-8")
            self.assertEqual(validate_library(self.guide)["status"], "invalid")
            self.registry["sources"][0].update(root="notas", path="idea.md", access="estudiante")
            self.file.write_text(json.dumps(self.registry), encoding="utf-8")
            self.assertIn("guia", validate_library(self.guide)["project_policy"]["excluded_source_ids"])
            with self.assertRaises(ValueError):
                build_wiki(self.guide, reader)

    def test_examples_of_links_remain_literal(self):
        content = "[A](old.md)\n\n`[A](old.md)`\n\n~~~\n[A](old.md)\n~~~\n"
        page = self.course
        new = repair_markdown(content, page, page, {page/"old.md": page/"new.md"})
        self.assertEqual(new, content.replace("[A](old.md)", "[A](new.md)", 1))
