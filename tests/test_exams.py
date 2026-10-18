"""End-to-end exam invariants with entirely synthetic, interdisciplinary data."""

from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from docencia.exams import build_exams, obfuscated_gift, prepare, render_model
from docencia.gift import escape_gift, parse_gift
from docencia.render import PACKAGE_ROOT


PRIVATE_FEEDBACK = "EXPLICACIÓN PRIVADA SOLO PARA EL DOCENTE"
PRECISE_VALUE = 1.23456789012345
PRECISE_TOLERANCE = 0.000000000012345678901


def synthetic_bank() -> str:
    return (
        "$CATEGORY: Literatura/Comprensión\n"
        "::literatura-ñ::[plain]¿Qué opción conserva el signo #? {"
        "~Un signo distinto =" + escape_gift("La opción # con {llaves} y ñ")
        + "#" + PRIVATE_FEEDBACK + " ~%33.3333333333333%Respuesta parcial"
        "####" + PRIVATE_FEEDBACK + "}\n\n"
        "$CATEGORY: Biología/Clasificación\n"
        "::biología::[html]<p>Seleccione los <strong>tres</strong> grupos.</p> {"
        "~%33.33333%Grupo uno ~%33.33333%Grupo dos"
        " ~%33.33334%Grupo tres ~%-100%Otro grupo}\n\n"
        "$CATEGORY: Historia/Contexto\n"
        "::historia::[plain]La afirmación del ejemplo es verdadera. {"
        "FALSE#" + PRIVATE_FEEDBACK + "#" + PRIVATE_FEEDBACK + "}\n\n"
        "$CATEGORY: Física/Medición\n"
        "::física::[plain]¿Cuál es el valor medido? {#"
        f"={PRECISE_VALUE}:{PRECISE_TOLERANCE}#{PRIVATE_FEEDBACK}"
        " =%50%1.23456788000001..1.23456789999999}\n\n"
        "$CATEGORY: Geografía/Relaciones\n"
        "::geografía::Relacione países y capitales. {"
        "=España->Madrid=Italia->Roma=Japón->Tokio}\n"
    )


class ExamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="asistente-exams-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bank = self.root / "banco-ñ.gift"
        self.bank.write_text(synthetic_bank(), encoding="utf-8")

    def build(self, output="output", **options):
        defaults = {"models": 2, "questions": 4, "seed": 49, "html_only": True}
        defaults.update(options)
        return build_exams(self.bank, self.root / output, **defaults)

    def test_all_offline_types_and_matching_exclusion_are_explicit(self):
        manifest = self.build()
        self.assertEqual(manifest["excluded_question_ids"], ["geografía"])
        for model in manifest["models"]:
            self.assertEqual({q["type"] for q in model["questions"]},
                             {"single", "multiple", "truefalse", "numerical"})
            self.assertEqual([q["number"] for q in model["questions"]], [1, 2, 3, 4])
            self.assertEqual(len({q["source_id"] for q in model["questions"]}), 4)
            self.assertEqual(model["pdf_status"], {"student": "not_requested", "teacher": "not_requested"})
            self.assertNotIn("student_pdf", model["files"])
            self.assertNotIn("teacher_pdf", model["files"])

    def test_snapshot_and_input_are_byte_exact_and_not_modified(self):
        original = b"\xef\xbb\xbf" + self.bank.read_bytes()
        self.bank.write_bytes(original)
        before = self.bank.stat().st_mtime_ns
        manifest = self.build()
        self.assertEqual(self.bank.read_bytes(), original)
        self.assertEqual(self.bank.stat().st_mtime_ns, before)
        self.assertEqual(manifest["bank_sha256"], hashlib.sha256(original).hexdigest())
        snapshot = self.root / "output" / manifest["bank_snapshot"]
        self.assertEqual(snapshot.read_bytes(), original)
        self.assertIn("geografía", snapshot.read_text(encoding="utf-8-sig"))
        self.bank.write_text("::cambiada::Otro banco{T}", encoding="utf-8")
        self.assertEqual(snapshot.read_bytes(), original)

    def test_manifest_roundtrip_and_paths_are_relative_existing_files(self):
        manifest = self.build(title="Evaluación: ciencia y humanidades · ñ")
        output = self.root / "output"
        self.assertEqual(json.loads((output / "manifest.json").read_text(encoding="utf-8")), manifest)
        for model in manifest["models"]:
            for value in model["files"].values():
                self.assertFalse(Path(value).is_absolute())
                self.assertTrue((output / value).is_file())
        self.assertFalse(list(output.glob("*.pdf")))

    def test_seed_reproduces_selection_order_options_and_manifest(self):
        first = self.build(output="first", models=4, questions=3)
        second = self.build(output="second", models=4, questions=3)
        self.assertEqual(first, second)
        for a, b in zip(first["models"], second["models"]):
            self.assertEqual((self.root / "first" / a["files"]["gift"]).read_bytes(),
                             (self.root / "second" / b["files"]["gift"]).read_bytes())
        third = self.build(output="third", models=4, questions=3, seed=123)
        self.assertNotEqual(first["models"], third["models"])

    def test_questions_are_exhausted_before_reuse(self):
        self.bank.write_text("\n".join(f"::q{i}::¿Pregunta {i}?{{=Uno~Dos}}" for i in range(8)), encoding="utf-8")
        manifest = self.build(models=5, questions=2)
        all_ids = [q["source_id"] for m in manifest["models"] for q in m["questions"]]
        self.assertEqual(len(set(all_ids[:8])), 8)
        self.assertTrue(all(count <= 2 for count in Counter(all_ids).values()))

    def test_free_categories_and_quotas_across_models(self):
        self.bank.write_text("\n".join(
            f"$CATEGORY: {category}\n" + "\n".join(
                f"::{prefix}-{i}::¿Caso {i}?{{T}}" for i in range(4)
            )
            for category, prefix in (("Filosofía/Ética", "fil"), ("Química/Materia", "qui"))
        ), encoding="utf-8")
        manifest = self.build(models=4, questions=2,
                              per_category={"Filosofía/Ética": 1, "Química/Materia": 1})
        for model in manifest["models"]:
            self.assertEqual(Counter(q["source_category"] for q in model["questions"]),
                             {"Filosofía/Ética": 1, "Química/Materia": 1})
        self.assertEqual(len({q["source_id"] for m in manifest["models"] for q in m["questions"]}), 8)

    def test_obfuscated_gift_preserves_every_label_weight_and_numeric_value(self):
        manifest = self.build(models=6)
        for model in manifest["models"]:
            gift = (self.root / "output" / model["files"]["gift"]).read_text(encoding="utf-8")
            parsed = parse_gift(gift)
            self.assertEqual(len(parsed), len(model["questions"]))
            for source, obfuscated in zip(model["questions"], parsed):
                self.assertEqual(obfuscated["prompt"], f"Pregunta {source['number']:02d}")
                if source["type"] == "numerical":
                    for before, after in zip(source["numerical"], obfuscated["numerical"]):
                        self.assertEqual({k: v for k, v in before.items() if k != "feedback"},
                                         {k: v for k, v in after.items() if k != "feedback"})
                        self.assertEqual(after["feedback"], "")
                else:
                    self.assertEqual(obfuscated["type"], "single" if source["type"] == "truefalse" else source["type"])
                    self.assertEqual([o["text"] for o in obfuscated["options"]],
                                     [f"Respuesta {o['label']}" for o in source["options"]])
                    self.assertEqual([o["weight"] for o in obfuscated["options"]],
                                     [o["weight"] for o in source["options"]])

    def test_paper_and_gift_share_question_and_option_order(self):
        manifest = self.build()
        for model in manifest["models"]:
            paper = (self.root / "output" / model["files"]["student_html"]).read_text(encoding="utf-8")
            positions = [paper.index(f"Pregunta {q['number']:02d}</h2>") for q in model["questions"]]
            self.assertEqual(positions, sorted(positions))
            for q in model["questions"]:
                if "options" not in q:
                    continue
                start = paper.index(f"Pregunta {q['number']:02d}</h2>")
                end = paper.index("</section>", start)
                fragment = paper[start:end]
                label_positions = [fragment.index(f"{o['label']}.</span>") for o in q["options"]]
                self.assertEqual(label_positions, sorted(label_positions))

    def test_obfuscation_excludes_enunciados_original_options_and_feedback(self):
        manifest = self.build()
        for model in manifest["models"]:
            gift = (self.root / "output" / model["files"]["gift"]).read_text(encoding="utf-8")
            student = (self.root / "output" / model["files"]["student_html"]).read_text(encoding="utf-8")
            for forbidden in ("¿Qué opción", "Grupo uno", "La afirmación", "¿Cuál", PRIVATE_FEEDBACK, "Verdadero", "Falso"):
                self.assertNotIn(forbidden, gift)
            self.assertNotIn(PRIVATE_FEEDBACK, student)
            self.assertNotIn(str(PRECISE_VALUE), student)
            self.assertNotIn("Crédito:", student)

    def test_truefalse_with_correct_b_does_not_move_the_correct_option(self):
        for token in ("TRUE", "TRUE#Fallo#Acierto", "FALSE", "FALSE#Fallo#Acierto"):
            source = parse_gift(f"::tf::Una afirmación.{{{token}}}")[0]
            prepared = None
            for seed in range(20):
                candidate = prepare(source, 1, random.Random(seed), {})
                if candidate["options"][1]["weight"] == 100:
                    prepared = candidate
                    break
            self.assertIsNotNone(prepared)
            result = parse_gift(obfuscated_gift({"id": "A", "questions": [prepared]}))[0]
            self.assertEqual([o["text"] for o in result["options"]], ["Respuesta A", "Respuesta B"])
            self.assertEqual([o["weight"] for o in result["options"]], [0, 100])

    def test_unicode_and_escaped_content_survive_printable_html(self):
        manifest = self.build()
        model = manifest["models"][0]
        student = (self.root / "output" / model["files"]["student_html"]).read_text(encoding="utf-8")
        self.assertIn("La opción # con {llaves} y ñ", student)
        self.assertIn("¿Cuál es el valor medido?", student)

    def test_teacher_numeric_solution_is_readable_not_gift_source(self):
        source = parse_gift(f"::n::¿Valor?{{#{PRECISE_VALUE}:{PRECISE_TOLERANCE}}}")[0]
        question = prepare(source, 1, random.Random(0), {})
        teacher = render_model({"id": "A", "questions": [question]}, "Soluciones", teacher=True)
        self.assertIn(str(PRECISE_VALUE), teacher)
        self.assertIn(str(PRECISE_TOLERANCE), teacher)
        self.assertNotIn("=%", teacher)
        self.assertNotIn("#\n", teacher)

    def test_metadata_maps_concepts_without_invention(self):
        metadata = {"schema_version": 1, "questions": {"física": {"concepts": ["medición"]}},
                    "concepts": {"medición": {"label": "Medición y tolerancia", "guidance": "Compara valor y tolerancia."}}}
        metadata_path = self.root / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        manifest = self.build(metadata_path=metadata_path)
        self.assertEqual(manifest["metadata"], metadata)
        for q in manifest["models"][0]["questions"]:
            self.assertEqual(q["concepts"], ["medición"] if q["source_id"] == "física" else [])

    def test_invalid_quotas_and_insufficient_pool_fail_before_output(self):
        cases = [{"Inexistente": 4}, {"Literatura/Comprensión": 2, "Física/Medición": 2},
                 {"Literatura/Comprensión": 1}, {"Literatura/Comprensión": -1},
                 {"Literatura/Comprensión": True}]
        for index, quotas in enumerate(cases):
            with self.subTest(quotas=quotas), self.assertRaises(ValueError):
                self.build(output=f"bad-{index}", per_category=quotas)
            self.assertFalse((self.root / f"bad-{index}").exists())
        with self.assertRaises(ValueError):
            self.build(output="insufficient", questions=5)
        self.assertFalse((self.root / "insufficient").exists())

    def test_invalid_metadata_is_rejected_before_output(self):
        for index, metadata in enumerate([
            {"schema_version": 2},
            {"schema_version": 1, "questions": {"unknown": {}}},
            {"schema_version": 1, "questions": {"física": {"concepts": ["not-declared"]}}},
        ]):
            path = self.root / f"bad-metadata-{index}.json"
            path.write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.build(output=f"metadata-output-{index}", metadata_path=path)
            self.assertFalse((self.root / f"metadata-output-{index}").exists())

    def test_semantically_damaged_gift_fails_before_output(self):
        original = obfuscated_gift

        def change_label(model):
            return original(model).replace("Respuesta A", "Respuesta Z")

        with patch("docencia.exams.obfuscated_gift", side_effect=change_label):
            with self.assertRaises(ValueError):
                self.build(output="invalid-serialization")
        self.assertFalse((self.root / "invalid-serialization").exists())

    def test_refuses_plugin_output_and_existing_output_without_overwrite(self):
        forbidden = PACKAGE_ROOT / "should-never-be-created-by-tests"
        with self.assertRaises(ValueError):
            build_exams(self.bank, forbidden, questions=4, html_only=True)
        self.assertFalse(forbidden.exists())
        output = self.root / "occupied"
        output.mkdir()
        sentinel = output / "important.txt"
        sentinel.write_text("Conservar", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.build(output="occupied")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "Conservar")

    def test_cli_works_from_an_unrelated_directory(self):
        output = self.root / "cli-output"
        result = subprocess.run(
            [sys.executable, str(PACKAGE_ROOT / "scripts/docencia.py"), "build-exams", str(self.bank),
             "--output", str(output), "--questions", "4", "--models", "1", "--html-only"],
            cwd=self.root, capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result_json = json.loads(result.stdout)
        self.assertEqual(result_json["status"], "ok")
        self.assertTrue(Path(result_json["manifest"]).is_file())


if __name__ == "__main__":
    unittest.main()
