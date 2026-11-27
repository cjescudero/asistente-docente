"""A frozen quiz can be graded and discussed in another language."""

import csv
import json
import re
import tempfile
import unittest
from pathlib import Path

from docencia.cuestionarios import build_cuestionarios, verify_obfuscated
from docencia.feedback import build_feedback


class QuizLanguagesTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.bank = self.root / "bank.gift"
        self.bank.write_text(
            "::T::Water is a compound.{TRUE#An element contains a single type of atom.#Correct.}\n\n"
            "::N::What is six squared?{#36:0.2}\n\n"
            "::S::Select the noble gas.{=Helium ~%-50%Hydrogen}\n\n"
            "::M::Select the noble gases.{~%50%Helium ~%50%Argon ~%-100%Hydrogen}\n",
            encoding="utf-8")
        self.metadata = self.root / "metadata.json"
        self.metadata.write_text(json.dumps({
            "schema_version": 1, "questions": {"T": {"concepts": ["composition"]}},
            "concepts": {"composition": {"label": "Composition", "guidance": "Review the elements."}}
        }), encoding="utf-8")

    def build(self, language):
        dest = self.root / language
        manifest = build_cuestionarios(self.bank, dest, language=language, layout="curso-v4",
                                       html_only=True, models=1, questions=4,
                                       metadata_path=self.metadata)
        return manifest["models"][0], dest / "_datos_internos"

    def test_models_keep_indices_weights_and_tolerances_across_languages(self):
        es, _ = self.build("es")
        en, internal = self.build("en")
        self.assertEqual(es["id"], en["id"])
        self.assertEqual(en["name"], "Model 01")
        self.assertEqual(en["moodle_category"], "$course$/top/OfflineQuizResponses/Quiz/Model 01")
        files = {key: internal / file for key, file in en["files"].items()}
        student = files["student_html"].read_text(encoding="utf-8")
        teacher = files["teacher_html"].read_text(encoding="utf-8")
        gift = files["gift"].read_text(encoding="utf-8")
        self.assertTrue((internal.parent / "README.md").is_file())
        self.assertIn("lang='en'", student)
        for text in ("FULL NAME", "Select all that apply", "incorrect choice: -0.5",
                     "Enter a number", "True", "False"):
            self.assertIn(text, student)
        self.assertNotIn("36.0", student)
        self.assertIn("36.0", teacher)
        for text in ("SECRET", "Helium", "Water", "Pregunta", "Respuesta", "Verdadero"):
            self.assertNotIn(text, gift)
        self.assertIn("Question 01", gift)
        self.assertIn("Answer A", gift)
        verify_obfuscated(en, gift)
        for left, right in zip(es["questions"], en["questions"]):
            for field in ("number", "source_id", "numerical"):
                self.assertEqual(left.get(field), right.get(field))
            for a, b in zip(left.get("options", []), right.get("options", [])):
                self.assertEqual((a["source_index"], a["label"], a["weight"]),
                                 (b["source_index"], b["label"], b["weight"]))
        for link in re.findall(r'\]\(([^)]+)\)', (internal.parent / "README.md").read_text(encoding="utf-8")):
            self.assertTrue((internal.parent / link).is_file(), link)

    def test_feedback_in_another_language_preserves_columns_and_frozen_model(self):
        model, internal = self.build("en")
        manifest = internal / "manifest.json"
        before = manifest.read_bytes()
        truth = next(q for q in model["questions"] if q["type"] == "truefalse")
        headers = ["Participante", "Modelo", "Estado", "Nota", "Comentario", "P1", "P2", "P3", "P4"]
        path = self.root / "resultados.csv"
        path.write_text(";".join(headers) + "\n"
                        + ";".join(["001", "A", "Completo", "7,50", "Original"]
                                   + ["0" if q is truth else "1" for q in model["questions"]]) + "\n",
                        encoding="utf-8")
        cfg = {"identifier_column": "Participante", "model_column": "Modelo",
               "feedback_column": "Comentario", "status_column": "Estado", "delimiter": ";",
               "question_columns": {str(i): f"P{i}" for i in range(1, 5)},
               "max_scores": {str(i): 1 for i in range(1, 5)},
               "translations": {"concepts": {"composition": {"label": "Composición",
                                "guidance": "Repasa los elementos."}}}}
        profile = self.root / "perfil.json"
        profile.write_text(json.dumps(cfg), encoding="utf-8")
        report = build_feedback(manifest, [path], profile, self.root / "output", language="es")
        self.assertEqual(report["status"], "ok", report)
        with Path(report["outputs"][0]).open(encoding="utf-8-sig") as stream:
            header, row = list(csv.reader(stream, delimiter=";"))
        self.assertEqual(header, headers)
        self.assertEqual(row[:4], ["001", "A", "Completo", "7,50"])
        self.assertIn("Aspecto a revisar: Composición.", row[4])
        self.assertIn("Repasa los elementos.", row[4])
        self.assertEqual(manifest.read_bytes(), before)

    def test_english_error_is_actionable(self):
        with self.assertRaisesRegex(ValueError, "Insufficient questions"):
            build_cuestionarios(self.bank, self.root / "too-many", questions=8, language="en")
