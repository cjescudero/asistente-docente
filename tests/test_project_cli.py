"""Recorrido operativo sin dependencias instaladas y desde otra carpeta."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProjectCliTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.course = self.base / "Curso con tildes á"

    def run_cli(self, *args):
        # -S excluye site-packages: las utilidades de proyecto son stdlib.
        return subprocess.run([sys.executable, "-S", str(ROOT / "scripts/docencia.py"),
                               *map(str, args)], cwd=self.base, capture_output=True, text=True,
                              encoding="utf-8")

    def test_guided_preparation_can_use_helpers_without_renderer_dependencies(self):
        preview = self.run_cli("init-project", self.course, "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse(self.course.exists())
        created = self.run_cli("init-project", self.course)
        self.assertEqual(created.returncode, 0, created.stderr)
        config = json.loads((self.course / "proyecto-docente.json").read_text(encoding="utf-8"))
        self.assertFalse(config["sources"]["selected"])
        self.assertEqual(list((self.course / "mapa-docente").iterdir()), [])
        repeat = self.run_cli("init-project", self.course)
        self.assertEqual(json.loads(repeat.stdout)["created"], [])
        check = self.run_cli("check-project", self.course)
        self.assertEqual(check.returncode, 2)
        self.assertEqual(json.loads(check.stdout)["selection_status"], "pending")
        selected = self.run_cli("init-project", self.course, "--no-sources")
        self.assertEqual(selected.returncode, 0)
        check = self.run_cli("check-project", self.course)
        self.assertEqual(json.loads(check.stdout)["selection_status"], "none")

    def test_existing_agents_is_preserved_even_when_conflicting(self):
        self.course.mkdir()
        agents = self.course / "AGENTS.md"
        agents.write_text("Escribir siempre en francés.\n", encoding="utf-8")
        result = self.run_cli("init-project", self.course)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(agents.read_text(encoding="utf-8"), "Escribir siempre en francés.\n")
        proposal = json.loads(result.stdout)["proposals"][0]
        self.assertIn("francés", proposal["proposed_content"])
        self.assertIn("conflictos", proposal["reason"])

    def test_doctor_keeps_capabilities_and_adds_separate_project_diagnostics(self):
        self.run_cli("init-project", self.course)
        report = self.run_cli("doctor", "--project", self.course)
        self.assertEqual(report.returncode, 2, report.stderr)
        data = json.loads(report.stdout)
        self.assertFalse(data["basic_ready"])
        self.assertFalse(data["pdf_ready"])
        self.assertTrue(data["project_tools_ready"])
        self.assertEqual(data["project"]["selection_status"], "pending")

    def test_migration_preview_reports_collision_and_never_moves(self):
        self.run_cli("init-project", self.course)
        old = self.course / "antiguo.md"
        old.write_text("Material original", encoding="utf-8")
        target = self.course / "fuentes/teoria/original.md"
        target.write_text("Otro material", encoding="utf-8")
        moves = self.base / "moves.json"
        moves.write_text(json.dumps([{"from": old.name, "to": "fuentes/teoria/original.md"}]), encoding="utf-8")
        result = self.run_cli("plan-migration", self.course, "--moves", moves)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")
        self.assertEqual(old.read_text(encoding="utf-8"), "Material original")
        self.assertEqual(target.read_text(encoding="utf-8"), "Otro material")

    def test_invalid_configuration_fails_as_json_without_traceback(self):
        self.run_cli("init-project", self.course)
        (self.course / "proyecto-docente.json").write_text("{invalid", encoding="utf-8")
        result = self.run_cli("check-project", self.course)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")
        self.assertNotIn("Traceback", result.stderr)

    def test_json_streams_are_utf8_with_legacy_console_encoding(self):
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        created = subprocess.run(
            [sys.executable, "-S", str(ROOT / "scripts/docencia.py"), "init-project", str(self.course)],
            cwd=self.base, capture_output=True, env=environment)
        self.assertEqual(created.returncode, 0, created.stderr)
        data = json.loads(created.stdout.decode("utf-8"))
        self.assertEqual(Path(data["root"]), self.course)
        missing = self.course / "banco-árabe-資料.gift"
        failed = subprocess.run(
            [sys.executable, "-S", str(ROOT / "scripts/docencia.py"), "validate-bank", str(missing)],
            cwd=self.base, capture_output=True, env=environment)
        self.assertEqual(failed.returncode, 1)
        error = json.loads(failed.stderr.decode("utf-8"))
        self.assertIn(missing.name, error["message"])
        self.assertNotIn("Traceback", failed.stderr.decode("utf-8"))

    def test_distributed_example_has_explicit_selection_and_no_wiki(self):
        shutil.copytree(ROOT / "examples/proyecto-docente/curso", self.course)
        result = self.run_cli("init-project", self.course)
        self.assertEqual(result.returncode, 0, result.stderr)
        check = self.run_cli("check-project", self.course)
        self.assertEqual(check.returncode, 0, check.stderr)
        files = json.loads(check.stdout)["selected_files"]
        self.assertEqual(files, ["fuentes/evaluaciones/cuestionarios/examen-vigente.md",
                                 "fuentes/teoria/interpretar-datos.md",
                                 "fuentes/teoria/orientaciones.md"])
        self.assertEqual(list((self.course / "mapa-docente").iterdir()), [])

    def test_migration_rejects_destination_inside_another_moving_source(self):
        self.run_cli("init-project", self.course)
        (self.course / "A").mkdir()
        (self.course / "B").mkdir()
        (self.course / "A/original.md").write_text("Original", encoding="utf-8")
        moves = self.base / "moves.json"
        moves.write_text(json.dumps([{"from": "A", "to": "B/A"},
                                     {"from": "B", "to": "nuevo"}]), encoding="utf-8")
        result = self.run_cli("plan-migration", self.course, "--moves", moves)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("origen de otro movimiento", result.stdout)
