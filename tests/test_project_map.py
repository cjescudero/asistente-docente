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
        initialize_project(self.root, include=["alumnado/materiales", "docente/evaluaciones"])
        self.guide = self.root / "docente/mapa-docente"
        self.exam = self.root / "docente/evaluaciones/examen.md"
        self.exam.write_text("SOLUCIÓN_RESERVADA", encoding="utf-8")
        self.material = self.root / "alumnado/materiales/teoría.md"
        self.material.write_text("Teoría", encoding="utf-8")
        self.data = dict(schema_version=2, title="Curso sintético", course=None,
                         source_roots={"teoria": "../../alumnado/materiales",
                                       "examenes": "../evaluaciones"}, sources=[], pages=[])
        for identifier, root_id, source, page, access in (
            ("teoria", "teoria", self.material, "contenidos/teoria.md", "estudiante"),
            ("examen", "examenes", self.exam, "reservado/examen.md", "docente"),
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
        (self.guide / "fuentes.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_selected_private_exam_is_valid_but_not_in_student_graph(self):
        self.assertEqual(validate_library(self.guide)["status"], "ok")
        student = self.root / "alumnado/grafo.html"
        build_graph(self.guide, student, audience="estudiante")
        html = student.read_text(encoding="utf-8")
        self.assertNotIn("reservado/examen", html)
        self.assertNotIn("SOLUCIÓN_RESERVADA", html)
        teacher = self.root / "docente/grafo.html"
        build_graph(self.guide, teacher)
        self.assertIn("reservado/examen", teacher.read_text(encoding="utf-8"))

    def test_excluded_source_is_never_opened_and_dependencies_are_transitive(self):
        page = self.guide / "contenidos/teoria.md"
        page.write_text("[Otra página](../reservado/examen.md)", encoding="utf-8")
        (self.guide / "index.md").write_text("[Teoría](contenidos/teoria.md)", encoding="utf-8")
        initialize_project(self.root, exclude=["docente/evaluaciones/examen.md"])
        original_open = Path.open

        def guarded(path, *args, **kwargs):
            if path.resolve() == self.exam:
                raise AssertionError("Se ha intentado leer una fuente excluida")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded):
            result = validate_library(self.guide)
        self.assertEqual(result["status"], "invalid")
        policy = result["project_policy"]
        self.assertEqual(policy["excluded_source_ids"], ["examen"])
        self.assertEqual(policy["affected_pages"], ["contenidos/teoria.md", "index.md", "reservado/examen.md"])
        self.assertIn("source_ids", (self.guide / "fuentes.json").read_text(encoding="utf-8"))
        self.assertNotIn("review_pending", (self.guide / "fuentes.json").read_text(encoding="utf-8"))

    def test_unregistered_secondary_link_cannot_include_results_or_excluded_file(self):
        for target in ("../../../docente/resultados/notas.csv",
                       "../../../docente/evaluaciones/examen.md"):
            with self.subTest(target=target):
                initialize_project(self.root, exclude=["docente/evaluaciones"])
                self.data["sources"] = self.data["sources"][:1]
                self.data["pages"] = self.data["pages"][:1]
                (self.guide / "reservado/examen.md").unlink(missing_ok=True)
                self.save()
                (self.guide / "contenidos/teoria.md").write_text(f"[Vínculo]({target})", encoding="utf-8")
                result = validate_library(self.guide)
                self.assertEqual(result["status"], "invalid")
                self.assertIn("contenidos/teoria.md", result["project_policy"]["affected_pages"])

    def test_pending_or_empty_selection_prevents_map_reuse(self):
        config_path = self.root / "proyecto-docente.json"
        for selected in (False, True):
            config = load_project(self.root)
            config["sources"] = dict(selected=selected, include=[], exclude=[])
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(validate_library(self.guide)["status"], "invalid")

    def test_root_override_does_not_bypass_project_policy(self):
        initialize_project(self.root, exclude=["docente/evaluaciones"])
        result = validate_library(self.guide, source_roots={"teoria": self.exam.parent})
        self.assertEqual(result["status"], "invalid")
        self.assertIn("teoria", result["project_policy"]["excluded_source_ids"])

    def test_symlink_source_cannot_bypass_exclusion(self):
        alias = self.root / "alumnado/materiales/alias.md"
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
        initialize_project(self.root, exclude=["docente/evaluaciones"])
        with self.assertRaises(ValueError):
            build_wiki(self.guide, output)
        self.assertEqual(output.read_bytes(), previous)
        with self.assertRaises(GraphError):
            build_graph(self.guide, self.guide / "grafo.html")

    def test_register_real_map_preserves_agents_selection_and_registry(self):
        agents = (self.root / "AGENTS.md").read_bytes()
        registry = (self.guide / "fuentes.json").read_bytes()
        preview = register_map(self.root, "docente/mapa-docente", dry_run=True)
        self.assertEqual(preview["status"], "dry_run")
        self.assertIsNone(load_project(self.root)["map"])
        register_map(self.root, "docente/mapa-docente")
        config = load_project(self.root)
        self.assertEqual(config["map"], "docente/mapa-docente")
        self.assertEqual(config["sources"]["include"], ["alumnado/materiales", "docente/evaluaciones"])
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), agents)
        self.assertEqual((self.guide / "fuentes.json").read_bytes(), registry)

    def test_register_rejects_empty_and_outside_map(self):
        for path in ("docente/borradores", "../otro"):
            with self.assertRaises(ValueError):
                register_map(self.root, path)

    def test_policy_applies_when_cli_runs_elsewhere(self):
        initialize_project(self.root, exclude=["docente/evaluaciones"])
        script = Path(__file__).resolve().parents[1] / "scripts/validate_library.py"
        result = subprocess.run([sys.executable, str(script), str(self.guide)],
                                cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["project_policy"]["excluded_source_ids"], ["examen"])
