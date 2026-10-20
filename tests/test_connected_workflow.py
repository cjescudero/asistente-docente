"""Recorrido público por CLI: materiales, modelos y copias Moodle."""
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "recorrido_v08", ROOT / "examples/recorrido-docente/comprobar.py")
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class ConnectedWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="docencia-recorrido-")
        cls.destination = Path(cls.temp.name) / "demostración"
        cls.summary = example.run_example(cls.destination)
        cls.manifest = json.loads((cls.destination / "examen/manifest.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def csv(self, path, delimiter):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream, delimiter=delimiter))

    def test_composed_models_cover_same_quotas_with_original_ids_and_frozen_banks(self):
        self.assertTrue(self.summary["originals_preserved"])
        self.assertFalse(self.summary["wiki_created"])
        self.assertFalse(self.summary["activity_pdf_registered"])
        self.assertTrue((self.destination / "curso/alumnado/actividades/medir-y-justificar/impresion/enunciado.html").is_file())
        first_ids = set()
        for model in self.manifest["models"]:
            self.assertEqual(model["coverage"]["difficulty"], {"basica": 3, "intermedia": 3})
            self.assertEqual(set(model["coverage"]["quotas"].values()), {1})
            ids = [question["source_id"] for question in model["questions"]]
            self.assertEqual(len(ids), len(set(ids)))
            first_ids.update(ids)
            for question in model["questions"]:
                self.assertIn(question["source_bank_id"], {"humanidades", "ciencias", "experimental"})
                self.assertIn(question["source_question_id"], {"Q01", "Q02", "Q03", "Q04"})
        self.assertEqual(len(first_ids), 12)
        self.assertEqual(len(self.manifest["source_banks"]), 3)

    def test_activity_exports_preserve_unrelated_cells_and_absence_in_both_profiles(self):
        for profile, delimiter, grade, identifier in (
            ("tarea", ",", "Calificación", "Identificador"),
            ("libro", ";", "Actividad", "Usuario"),
        ):
            folder = self.destination / f"correccion-{profile}"
            report = json.loads((folder / "grading-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["updated"], 2)
            self.assertTrue(report["activity_record"]["course_boundary_checked"])
            rows = self.csv(next(folder.glob("*.csv")), delimiter)
            self.assertEqual([r[grade] for r in rows], ["8.75", "8.75", ""] if profile == "tarea"
                             else ["8,75", "8,75", ""])
            self.assertEqual(rows[-1][identifier], "Participante 003" if profile == "tarea" else "003")
            if profile == "libro":
                self.assertEqual([r["Otra actividad"] for r in rows], ["8,50", "9,00", "6,50"])

    def test_exam_feedback_preserves_authoritative_grade_and_prioritizes_without_reserved_content(self):
        folder = self.destination / "feedback"
        expected = {"A": ("001", "3,50", "8,00"), "B": ("002", "6,25", "9,00"),
                    "C": ("003", "", "7,00")}
        for model, values in expected.items():
            row = self.csv(folder / f"modelo_{model}_CORREGIDO.csv", ";")[0]
            self.assertEqual(tuple(row[k] for k in ("Usuario", "Nota examen", "Otra nota")), values)
            if model == "C":
                self.assertEqual(row["Comentario examen"], "")
            else:
                text = row["Comentario examen"]
                self.assertIn("Dificultad acusada en Crítica de fuentes", text)
                self.assertIn("Aspecto a revisar: Magnitudes y medición", text)
                self.assertNotIn("docente/", text)
                self.assertNotIn("Respuesta correcta", text)

    def test_cli_rejects_mixed_or_incomplete_bank_inputs_before_writing(self):
        for arguments in (
            ["banco.gift", "--catalog", "catalogo.json", "--selection", "reparto.json"],
            ["--catalog", "catalogo.json"],
            ["banco.gift", "--selection", "reparto.json"],
            ["--catalog", "catalogo.json", "--selection", "reparto.json", "--metadata", "meta.json"],
        ):
            output = self.destination / "invalid"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/docencia.py"),
                                     "build-exams", *arguments, "--output", str(output)],
                                    cwd=self.destination, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
