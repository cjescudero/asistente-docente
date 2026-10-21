"""El corpus elegido gobierna originales, enlaces y dependencias transitivas."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from docencia.project import initialize_project, load_project
from docencia.project_map import register_map
from scripts.validate_library import validate_library
from scripts.build_graph import build_graph, GraphError
from scripts.build_wiki import build_wiki


class ProjectMapTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve() / "curso"
        initialize_project(self.root, include=["fuentes/teoria", "fuentes/evaluaciones/cuestionarios"])
        self.guide = self.root / "mapa-docente"
        self.exam = self.root / "fuentes/evaluaciones/cuestionarios/cuestionario.md"
        self.exam.write_text("SOLUCIÓN_RESERVADA", encoding="utf-8")
        self.material = self.root / "fuentes/teoria/teoría.md"
        self.material.write_text("Teoría", encoding="utf-8")
        self.data = dict(schema_version=2, title="Curso sintético", course=None,
                         source_roots={"teoria": "../fuentes/teoria",
                                       "cuestionarios": "../fuentes/evaluaciones/cuestionarios"}, sources=[], pages=[])
        for identifier, root_id, source, page, access in (
            ("teoria", "teoria", self.material, "contenidos/teoria.md", "estudiante"),
            ("cuestionario", "cuestionarios", self.exam, "reservado/cuestionario.md", "docente"),
        ):
            path = self.guide / page
            path.parent.mkdir(exist_ok=True)
            path.write_text("# " + identifier, encoding="utf-8")
            self.data["sources"].append(dict(id=identifier, title=identifier, path=source.name,
                root=root_id, kind="apuntes", course=None, currency="vigente", access=access,
                reading="completa", reviewed_locators=["Documento completo"],
                sha256=hashlib.sha256(source.read_bytes()).hexdigest(), page=page))
            self.data["pages"].append(dict(path=page, title=identifier, kind="apuntes",
                                           access=access, source_ids=[identifier]))
        for name in ("index.md", "LEEME.md", "incidencias.md", "log.md"):
            (self.guide / name).write_text("# Mapa\n", encoding="utf-8")
        self.save()

    def save(self):
        (self.guide / "_datos_internos").mkdir(exist_ok=True)
        (self.guide / "_datos_internos/fuentes.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_v3_map_registry_in_internal_folder_keeps_reader_graph_and_registration(self):
        course = self.root.parent / "curso-v3"
        initialize_project(course, include=["fuentes/teoria"])
        source = course / "fuentes/teoria/tema.md"
        source.write_text("# Tema\n\nUna evidencia requiere contexto.\n", encoding="utf-8")
        guide = course / "mapa-docente"
        (guide / "contenidos").mkdir()
        (guide / "_datos_internos").mkdir()
        (guide / "index.md").write_text("# Índice\n\n[Tema](contenidos/tema.md)\n", encoding="utf-8")
        (guide / "contenidos/tema.md").write_text("# Tema\n\n[Fuente](../../fuentes/teoria/tema.md)\n", encoding="utf-8")
        for name in ("LEEME.md", "incidencias.md", "log.md"):
            (guide / name).write_text("# Mapa\n", encoding="utf-8")
        data = {"schema_version": 2, "title": "Tema", "course": None,
                "source_roots": {"principal": "../fuentes/teoria"},
                "sources": [{"id": "tema", "title": "Tema", "path": "tema.md", "root": "principal",
                             "kind": "apuntes", "course": None, "currency": "vigente", "access": "estudiante",
                             "reading": "completa", "reviewed_locators": ["Documento completo"],
                             "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                             "page": "contenidos/tema.md"}],
                "pages": [{"path": "contenidos/tema.md", "title": "Tema", "kind": "apuntes",
                           "access": "estudiante", "source_ids": ["tema"]}]}
        registry = guide / "_datos_internos/fuentes.json"
        registry.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(validate_library(guide)["status"], "ok")
        build_wiki(guide)
        build_graph(guide, guide / "grafo-docente.html")
        self.assertTrue((guide / "index.html").is_file())
        self.assertTrue((guide / "grafo-docente.html").is_file())
        self.assertEqual(register_map(course, guide)["status"], "ok")
        self.assertEqual(load_project(course)["map"], "mapa-docente")
        (guide / "fuentes.json").write_text(registry.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(validate_library(guide)["status"], "invalid")

    def test_selected_private_questionnaire_is_valid_but_not_in_student_graph(self):
        self.assertEqual(validate_library(self.guide)["status"], "ok")
        student = self.guide / "grafo-estudiante.html"
        build_graph(self.guide, student, audience="estudiante")
        html = student.read_text(encoding="utf-8")
        self.assertNotIn("reservado/cuestionario", html)
        self.assertNotIn("SOLUCIÓN_RESERVADA", html)
        teacher = self.guide / "grafo-docente.html"
        build_graph(self.guide, teacher)
        self.assertIn("reservado/cuestionario", teacher.read_text(encoding="utf-8"))

    def test_excluded_source_is_never_opened_and_dependencies_are_transitive(self):
        page = self.guide / "contenidos/teoria.md"
        page.write_text("[Otra página](../reservado/cuestionario.md)", encoding="utf-8")
        (self.guide / "index.md").write_text("[Teoría](contenidos/teoria.md)", encoding="utf-8")
        initialize_project(self.root, exclude=["fuentes/evaluaciones/cuestionarios/cuestionario.md"])
        original_open = Path.open

        def guarded(path, *args, **kwargs):
            if path.resolve() == self.exam:
                raise AssertionError("Se ha intentado leer una fuente excluida")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded):
            result = validate_library(self.guide)
        self.assertEqual(result["status"], "invalid")
        policy = result["project_policy"]
        self.assertEqual(policy["excluded_source_ids"], ["cuestionario"])
        self.assertEqual(policy["affected_pages"], ["contenidos/teoria.md", "index.md", "reservado/cuestionario.md"])
        self.assertIn("source_ids", (self.guide / "_datos_internos/fuentes.json").read_text(encoding="utf-8"))
        self.assertNotIn("review_pending", (self.guide / "_datos_internos/fuentes.json").read_text(encoding="utf-8"))

    def test_unregistered_secondary_link_cannot_include_results_or_excluded_file(self):
        for target in ("../../resultados/notas.csv",
                       "../../fuentes/evaluaciones/cuestionarios/cuestionario.md"):
            with self.subTest(target=target):
                initialize_project(self.root, exclude=["fuentes/evaluaciones/cuestionarios"])
                self.data["sources"] = self.data["sources"][:1]
                self.data["pages"] = self.data["pages"][:1]
                (self.guide / "reservado/cuestionario.md").unlink(missing_ok=True)
                self.save()
                (self.guide / "contenidos/teoria.md").write_text(f"[Vínculo]({target})", encoding="utf-8")
                result = validate_library(self.guide)
                self.assertEqual(result["status"], "invalid")
                self.assertIn("contenidos/teoria.md", result["project_policy"]["affected_pages"])

    def test_pending_or_empty_selection_prevents_map_reuse(self):
        config_path = self.root / "_datos_internos_proyecto/proyecto-docente.json"
        for selected in (False, True):
            config = load_project(self.root)
            config["sources"] = dict(selected=selected, include=[], exclude=[])
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(validate_library(self.guide)["status"], "invalid")

    def test_root_override_does_not_bypass_project_policy(self):
        initialize_project(self.root, exclude=["fuentes/evaluaciones/cuestionarios"])
        result = validate_library(self.guide, source_roots={"teoria": self.exam.parent})
        self.assertEqual(result["status"], "invalid")
        self.assertIn("teoria", result["project_policy"]["excluded_source_ids"])

    def test_symlink_source_cannot_bypass_exclusion(self):
        alias = self.root / "fuentes/teoria/alias.md"
        try:
            alias.symlink_to(self.exam)
        except OSError:
            self.skipTest("Este anfitrión no permite enlaces simbólicos")
        self.data["sources"][0]["path"] = alias.name
        self.save()
        result = validate_library(self.guide)
        self.assertIn("teoria", result["project_policy"]["excluded_source_ids"])

    def test_removed_source_blocks_renderers_without_overwriting_previous_html(self):
        output = self.guide / "index.html"
        build_wiki(self.guide, output)
        previous = output.read_bytes()
        initialize_project(self.root, exclude=["fuentes/evaluaciones/cuestionarios"])
        with self.assertRaises(ValueError):
            build_wiki(self.guide, output)
        self.assertEqual(output.read_bytes(), previous)
        with self.assertRaises(GraphError):
            build_graph(self.guide, self.guide / "grafo.html")

    def test_register_real_map_preserves_agents_selection_and_registry(self):
        agents = (self.root / "AGENTS.md").read_bytes()
        registry = (self.guide / "_datos_internos/fuentes.json").read_bytes()
        preview = register_map(self.root, "mapa-docente", dry_run=True)
        self.assertEqual(preview["status"], "dry_run")
        self.assertIsNone(load_project(self.root)["map"])
        register_map(self.root, "mapa-docente")
        config = load_project(self.root)
        self.assertEqual(config["map"], "mapa-docente")
        self.assertEqual(config["sources"]["include"], ["fuentes/teoria", "fuentes/evaluaciones/cuestionarios"])
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), agents)
        self.assertEqual((self.guide / "_datos_internos/fuentes.json").read_bytes(), registry)

    def test_register_rejects_empty_and_outside_map(self):
        for path in ("materiales_generados/materiales", "../otro"):
            with self.assertRaises(ValueError):
                register_map(self.root, path)

    def test_policy_applies_when_cli_runs_elsewhere(self):
        initialize_project(self.root, exclude=["fuentes/evaluaciones/cuestionarios"])
        script = Path(__file__).resolve().parents[1] / "scripts/validate_library.py"
        result = subprocess.run([sys.executable, str(script), str(self.guide)],
                                cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["project_policy"]["excluded_source_ids"], ["cuestionario"])

    def test_generated_source_reverted_to_draft_invalidates_transitive_pages(self):
        folder = self.root / "materiales_generados/actividades/lectura"
        (folder / "alumnado").mkdir(parents=True)
        statement = folder / "alumnado/enunciado.md"
        statement.write_text("Enunciado publicado para el curso", encoding="utf-8")
        (folder / "_datos_internos").mkdir()
        record = folder / "_datos_internos/material-docente.json"
        metadata = {"schema_version": 1, "id": "lectura", "type": "actividad", "status": "revisado"}
        record.write_text(json.dumps(metadata), encoding="utf-8")
        config = load_project(self.root)
        config["sources"]["include"] = ["materiales_generados/actividades/lectura/alumnado"]
        (self.root / "_datos_internos_proyecto/proyecto-docente.json").write_text(json.dumps(config), encoding="utf-8")
        self.data["source_roots"] = {"teoria": "../materiales_generados/actividades/lectura/alumnado"}
        self.data["sources"] = self.data["sources"][:1]
        self.data["pages"] = self.data["pages"][:1]
        source = self.data["sources"][0]
        source.update(path="enunciado.md", sha256=hashlib.sha256(statement.read_bytes()).hexdigest())
        (self.guide / "reservado/cuestionario.md").unlink()
        (self.guide / "index.md").write_text("[Actividad](contenidos/teoria.md)", encoding="utf-8")
        self.save()
        self.assertEqual(validate_library(self.guide)["status"], "ok")
        metadata["status"] = "borrador"
        record.write_text(json.dumps(metadata), encoding="utf-8")
        real_open = Path.open
        def guarded(path, *args, **kwargs):
            if path.resolve() == statement:
                raise AssertionError("El mapa no debe abrir una producción devuelta a borrador.")
            return real_open(path, *args, **kwargs)
        with patch.object(Path, "open", guarded):
            report = validate_library(self.guide)
        self.assertEqual(report["status"], "invalid")
        self.assertEqual(report["project_policy"]["excluded_source_ids"], ["teoria"])
        self.assertEqual(report["project_policy"]["affected_pages"], ["contenidos/teoria.md", "index.md"])
