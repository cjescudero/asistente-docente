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
        config = json.loads(created.stdout)["config"]
        self.assertFalse(config["sources"]["selected"])
        self.assertFalse((self.course / "Gestión del proyecto").exists())
        self.assertEqual(list((self.course / "Material generado por IA").iterdir()), [])
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

    def test_optional_notes_flag_creates_default_or_reuses_chosen_folder(self):
        for flag, name in (([], "Notas del curso"), (["Cuaderno personal"], "Cuaderno personal")):
            with self.subTest(name=name):
                course = self.base / ("Curso " + name)
                folder = course / name
                if flag:
                    folder.mkdir(parents=True)
                    (folder / "idea.md").write_text("Borrador", encoding="utf-8")
                initial = self.run_cli("init-project", course, "--notes", *flag, "--dry-run")
                self.assertEqual(initial.returncode, 0, initial.stderr)
                self.assertFalse((course / "AGENTS.md").exists())
                result = self.run_cli("init-project", course, "--notes", *flag)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["config"]["spaces"]["notes"], [name])
                self.assertTrue(folder.is_dir())
                self.assertIn(name, (course / "AGENTS.md").read_text(encoding="utf-8"))
                if flag:
                    self.assertFalse((course / "Notas del curso").exists())
                    self.assertEqual((folder / "idea.md").read_text(encoding="utf-8"), "Borrador")

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
        target = self.course / "Material de la asignatura/original.md"
        target.write_text("Otro material", encoding="utf-8")
        moves = self.base / "moves.json"
        moves.write_text(json.dumps([{"from": old.name, "to": "Material de la asignatura/original.md"}]), encoding="utf-8")
        result = self.run_cli("plan-migration", self.course, "--moves", moves)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")
        self.assertEqual(old.read_text(encoding="utf-8"), "Material original")
        self.assertEqual(target.read_text(encoding="utf-8"), "Otro material")

    def test_invalid_configuration_fails_as_json_without_traceback(self):
        self.run_cli("init-project", self.course, "--no-sources")
        (self.course / "Archivos de gestión del proyecto/proyecto-docente.json").write_text("{invalid", encoding="utf-8")
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
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("adopción", json.loads(result.stdout)["proposals"][0]["reason"])
        self.assertFalse((self.course / "Gestión del proyecto").exists())
        check = self.run_cli("check-project", self.course)
        self.assertEqual(check.returncode, 2, check.stderr)
        self.assertIn("mapa-docente", json.loads(check.stdout)["missing_directories"])
        files = json.loads(check.stdout)["selected_files"]
        self.assertEqual(files, ["fuentes/evaluaciones/cuestionarios/cuestionario-vigente.md",
                                 "fuentes/teoria/interpretar-datos.md",
                                 "fuentes/teoria/orientaciones.md"])
        self.assertFalse((self.course / "mapa-docente/index.md").exists())

    def test_v3_course_builds_questionnaire_with_local_selection_from_other_cwd(self):
        shutil.copytree(ROOT / "examples/curso-v3/curso", self.course)
        catalog = self.course / "materiales_generados/bancos/_datos_internos/catalogo.json"
        target = self.course / "materiales_generados/cuestionarios/nuevo"
        selection = target / "_datos_internos/seleccion.json"
        selection.parent.mkdir(parents=True)
        selection.write_bytes((self.course / "materiales_generados/cuestionarios/fuentes-y-medicion/_datos_internos/seleccion.json").read_bytes())
        result = self.run_cli("build-cuestionarios", "--catalog", catalog, "--selection", selection,
                              "--project", self.course, "--output", target,
                              "--layout", "curso-v3", "--questions", "2", "--models", "4", "--html-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(Path(data["manifest"]), (target / "_datos_internos/manifest.json").resolve())
        self.assertTrue((target / "alumnado/modelo-A-student.html").is_file())
        self.assertFalse((target.parent / "seleccion-nuevo.json").exists())

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
