"""Synthetic Moodle round trips; no real student records are used."""

import copy
import csv
import hashlib
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from docencia.feedback import FeedbackError, _PACKAGE_ROOT, _conceptual, build_feedback


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="docencia-feedback-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.out = self.root / "salidas"
        self.bank = self.root / "bank.gift"
        self.bank.write_text(
            "::one::SECRET_QUESTION {=SECRET_CORRECT#Razón de la opción correcta. "
            "~SECRET_WRONG#Confunde acumulación y tasa.}\n", encoding="utf-8")
        self.manifest_path = self.root / "manifest.json"
        self.config_path = self.root / "config.json"
        self.manifest = {
            "schema_version": 1, "title": "Synthetic", "seed": 7,
            "bank_snapshot": "bank.gift",
            "bank_sha256": hashlib.sha256(self.bank.read_bytes()).hexdigest(),
            "metadata": {"schema_version": 1,
                "questions": {"one": {"concepts": ["balance"],
                    "guidance": "Relaciona las magnitudes con sus unidades"}},
                "concepts": {"balance": {"label": "Balance de cantidades",
                    "guidance": "Distingue acumulación y tasa"}}},
            "models": [{"id": "A", "questions": [{"number": 1,
                "source_id": "one", "source_category": "", "concepts": ["balance"],
                "type": "single", "prompt": "SECRET_QUESTION", "format": "plain",
                "options": [
                    {"label": "A", "text": "SECRET_WRONG", "weight": 0, "source_index": 1},
                    {"label": "B", "text": "SECRET_CORRECT", "weight": 100, "source_index": 0}
                ]}], "files": {}, "pdf_status": "not_requested"}]}
        self.config = {"schema_version": 1, "identifier_column": "Identificador",
            "model_column": "Modelo", "feedback_column": "Comentario",
            "status_column": "Estado", "absent_values": ["No presentado"],
            "blank_values": [], "question_columns": {"1": "P1"},
            "max_scores": {"1": 1}}
        self.header = ["Identificador", "Modelo", "Estado", "P1", "P2",
                       "Eleccion", "Comentario", "Nota final", "Ajena"]
        self.rows = [["sintetico-001", "A", "Finalizado", "0,50", "0", "A",
                      "Comentario antiguo", "7,25", "Conservar; ñ y \"comillas\""]]

    def save(self):
        self.manifest_path.write_text(json.dumps(self.manifest, ensure_ascii=False), encoding="utf-8")
        self.config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")

    def input(self, name="input.csv", rows=None, header=None, delimiter=";", newline="\r\n"):
        path = self.root / name
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, delimiter=delimiter, lineterminator=newline)
            writer.writerow(self.header if header is None else header)
            writer.writerows(self.rows if rows is None else rows)
        return path

    def run_feedback(self, inputs=None, **options):
        self.save()
        return build_feedback(self.manifest_path, inputs or [self.input()],
                              self.config_path, self.out, **options)

    def output_rows(self, report, index=0, delimiter=";"):
        path = Path(report["outputs"][index])
        self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.reader(stream, delimiter=delimiter))

    def assert_blocked(self, report, code=None):
        self.assertEqual(report["status"], "blocked", report)
        self.assertEqual(report["outputs"], [])
        self.assertFalse(list(self.out.glob("*.csv")))
        reports = list(self.out.glob("feedback-report*.json"))
        self.assertTrue(reports)
        self.assertEqual(json.loads(reports[-1].read_text(encoding="utf-8")), report)
        if code:
            self.assertIn(code, [item["code"] for item in report["incidents"]])

    def test_roundtrip_preserves_scores_columns_unicode_and_source(self):
        source = self.input()
        before = source.read_bytes()
        result = self.run_feedback([source])
        self.assertEqual(result["status"], "ok", result)
        data = self.output_rows(result)
        self.assertEqual(data[0], self.header)
        for index, value in enumerate(self.rows[0]):
            if self.header[index] != "Comentario":
                self.assertEqual(data[1][index], value)
        feedback = data[1][6]
        self.assertIn("Balance de cantidades", feedback)
        self.assertIn("Distingue acumulación y tasa", feedback)
        for private in ("SECRET_QUESTION", "SECRET_CORRECT", "SECRET_WRONG", "Pregunta 1", "Selección"):
            self.assertNotIn(private, feedback)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(result["manifest_sha256"], hashlib.sha256(self.manifest_path.read_bytes()).hexdigest())
        self.assertEqual(result["students"]["with_feedback"], 1)

    def test_absence_clears_feedback_without_interpreting_scores(self):
        self.rows[0][2:4] = ["No presentado", ""]
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.output_rows(result)[1][6], "")
        self.assertEqual(self.output_rows(result)[1][3], "")
        self.assertEqual(result["students"]["absent"], 1)

    def test_missing_column_blocks_even_absent(self):
        self.rows[0][2] = "No presentado"
        source = self.input(header=[name for name in self.header if name != "P1"],
                            rows=[self.rows[0][:3] + self.rows[0][4:]])
        self.assert_blocked(self.run_feedback([source]), "MISSING_COLUMN")

    def test_missing_score_is_not_zero_even_completed_attempt(self):
        self.rows[0][3] = ""
        self.assert_blocked(self.run_feedback(), "MISSING_SCORE")

    def test_dash_is_not_implicitly_blank(self):
        self.rows[0][3] = "-"
        self.assert_blocked(self.run_feedback(), "INVALID_SCORE")

    def test_explicit_blank_tokens_preserve_original_cells(self):
        self.config["blank_values"] = ["-", ""]
        self.rows[0][3] = "-"
        self.rows.append(["sintetico-002", "A", "Finalizado", "", "0", "", "", "", ""])
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        data = self.output_rows(result)
        self.assertEqual([row[3] for row in data[1:]], ["-", ""])
        self.assertTrue(all("Balance" in row[6] for row in data[1:]))

    def test_zero_score_is_valid_evidence_and_not_absence(self):
        self.rows[0][3] = "0"
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("Balance", self.output_rows(result)[1][6])
        self.assertEqual(result["students"]["absent"], 0)

    def test_negative_score_is_preserved_without_assumed_lower_bound(self):
        self.rows[0][3] = "-0,25"
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.output_rows(result)[1][3], "-0,25")

    def test_maximum_score_has_positive_comment(self):
        self.rows[0][3] = "1,00"
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("puntuación máxima", self.output_rows(result)[1][6])

    def test_duplicate_identifiers_between_files_block_whole_batch(self):
        first, second = self.input("first.csv"), self.input("second.csv")
        self.assert_blocked(self.run_feedback([first, second]), "DUPLICATE_IDENTIFIER")

    def test_duplicate_identifiers_between_models_are_not_merged(self):
        second = copy.deepcopy(self.manifest["models"][0])
        second["id"] = "B"
        self.manifest["models"].append(second)
        self.rows.append(self.rows[0].copy())
        self.rows[1][1] = "B"
        self.assert_blocked(self.run_feedback(), "DUPLICATE_IDENTIFIER")

    def test_unknown_model_blocks(self):
        self.rows[0][1] = "NoExiste"
        self.assert_blocked(self.run_feedback(), "UNKNOWN_MODEL")

    def test_empty_identifier_blocks(self):
        self.rows[0][0] = ""
        self.assert_blocked(self.run_feedback(), "MISSING_IDENTIFIER")

    def test_snapshot_edit_is_detected_before_feedback(self):
        self.bank.write_text(self.bank.read_text() + "\n// change\n", encoding="utf-8")
        self.assert_blocked(self.run_feedback(), "SNAPSHOT_HASH_MISMATCH")

    def test_snapshot_cannot_escape_manifest_directory(self):
        self.manifest["bank_snapshot"] = "../bank.gift"
        self.assert_blocked(self.run_feedback(), "INVALID_INPUT")

    def test_duplicate_manifest_models_block(self):
        self.manifest["models"].append(copy.deepcopy(self.manifest["models"][0]))
        self.assert_blocked(self.run_feedback(), "INVALID_INPUT")

    def test_missing_configured_maximum_blocks(self):
        self.config["max_scores"] = {}
        self.assert_blocked(self.run_feedback(), "INVALID_INPUT")

    def test_score_above_maximum_blocks(self):
        self.rows[0][3] = "1,5"
        self.assert_blocked(self.run_feedback(), "SCORE_EXCEEDS_MAXIMUM")

    def test_nonfinite_scores_block(self):
        self.rows[0][3] = "NaN"
        self.assert_blocked(self.run_feedback(), "INVALID_SCORE")

    def test_per_model_overrides_and_consolidation_preserve_input_order(self):
        second = copy.deepcopy(self.manifest["models"][0])
        second["id"] = "B"
        self.manifest["models"].append(second)
        self.config["models"] = {"B": {"question_columns": {"1": "P2"}, "max_scores": {"1": 2}}}
        self.rows.insert(0, ["sintetico-002", "B", "Finalizado", "IGNORAR", "2,00", "", "", "8,00", "otra"])
        result = self.run_feedback(consolidated=True)
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(len(result["outputs"]), 3)
        consolidated = self.output_rows(result, 2)
        self.assertEqual([row[0] for row in consolidated[1:]], ["sintetico-002", "sintetico-001"])
        self.assertEqual(consolidated[1][3], "IGNORAR")
        self.assertIn("puntuación máxima", consolidated[1][6])

    def test_declared_delimiter_and_quoted_multiline_cells(self):
        self.config["delimiter"] = "\t"
        self.rows[0][8] = 'Línea uno\nLínea "dos"; fin'
        source = self.input(delimiter="\t", newline="\n")
        result = self.run_feedback([source])
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.output_rows(result, delimiter="\t")[1][8], self.rows[0][8])

    def test_comma_delimiter_is_detected_despite_decimal_comma(self):
        source = self.input(delimiter=",")
        result = self.run_feedback([source])
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.output_rows(result, delimiter=",")[1][3], "0,50")

    def test_existing_output_is_not_overwritten_and_report_gets_new_name(self):
        first = self.run_feedback()
        before = Path(first["outputs"][0]).read_bytes()
        second = self.run_feedback()
        self.assertEqual(second["status"], "blocked", second)
        self.assertEqual(second["outputs"], [])
        self.assertIn("OUTPUT_EXISTS", [item["code"] for item in second["incidents"]])
        self.assertEqual(Path(first["outputs"][0]).read_bytes(), before)
        self.assertTrue((self.out / "feedback-report-2.json").exists())

    def test_output_within_package_is_rejected_before_writing(self):
        self.save()
        with self.assertRaises(FeedbackError):
            build_feedback(self.manifest_path, [self.input()], self.config_path, _PACKAGE_ROOT / "not-a-real-output")
        self.assertFalse((_PACKAGE_ROOT / "not-a-real-output").exists())

    def test_detailed_requires_explicit_answer_columns(self):
        self.assert_blocked(self.run_feedback(detailed=True), "INVALID_INPUT")

    def test_detailed_uses_original_option_index_without_regrading(self):
        self.config["answer_columns"] = {"1": "Eleccion"}
        self.rows[0][5] = "B"
        result = self.run_feedback(detailed=True)
        self.assertEqual(result["status"], "ok", result)
        row = self.output_rows(result)[1]
        self.assertIn("Pregunta 1", row[6])
        self.assertIn("Selección B: correcta", row[6])
        self.assertIn("Razón de la opción correcta", row[6])
        self.assertNotIn("Confunde acumulación", row[6])
        self.assertEqual(row[3], "0,50")
        self.assertEqual(row[7], "7,25")

    def test_detailed_missing_selection_keeps_conceptual_feedback_with_warning(self):
        self.config["answer_columns"] = {"1": "Eleccion"}
        self.rows[0][5] = ""
        result = self.run_feedback(detailed=True)
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("DETAIL_UNAVAILABLE", [item["code"] for item in result["incidents"]])
        self.assertNotIn("Selección", self.output_rows(result)[1][6])

    def test_unknown_selected_label_does_not_invent_an_answer(self):
        self.config["answer_columns"] = {"1": "Eleccion"}
        self.rows[0][5] = "XYZ"
        result = self.run_feedback(detailed=True)
        self.assertEqual(result["status"], "ok", result)
        self.assertNotIn("XYZ", self.output_rows(result)[1][6])
        self.assertTrue(result["incidents"])

    def test_missing_concepts_do_not_create_advice(self):
        self.manifest["metadata"] = {}
        self.manifest["models"][0]["questions"][0]["concepts"] = []
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("no incluyen orientaciones", self.output_rows(result)[1][6])

    def test_missing_feedback_column_blocks_instead_of_choosing_a_column(self):
        self.config["feedback_column"] = "NoExiste"
        self.assert_blocked(self.run_feedback(), "MISSING_COLUMN")

    def test_invalid_utf8_and_truncated_rows_block(self):
        path = self.root / "broken.csv"
        path.write_bytes(b"header\n\xff")
        self.assert_blocked(self.run_feedback([path]), "INVALID_CSV")

    def test_wrong_option_origin_is_rejected_before_attributing_reason(self):
        self.manifest["models"][0]["questions"][0]["options"][0]["source_index"] = 0
        self.assert_blocked(self.run_feedback(), "INVALID_INPUT")

    def test_duplicate_option_labels_block(self):
        options = self.manifest["models"][0]["questions"][0]["options"]
        options[1]["label"] = options[0]["label"]
        self.assert_blocked(self.run_feedback(), "INVALID_INPUT")

    def test_detailed_numerical_uses_documented_tolerance(self):
        from docencia.gift import parse_gift
        self.bank.write_text("::one::SECRET_NUMBER {#3.5:0.1}\n", encoding="utf-8")
        self.manifest["bank_sha256"] = hashlib.sha256(self.bank.read_bytes()).hexdigest()
        question = self.manifest["models"][0]["questions"][0]
        question["type"] = "numerical"
        question.pop("options")
        question["numerical"] = parse_gift(self.bank.read_text())[0]["numerical"]
        self.rows[0][5] = "3,55"
        self.config["answer_columns"] = {"1": "Eleccion"}
        result = self.run_feedback(detailed=True)
        self.assertEqual(result["status"], "ok", result)
        row = self.output_rows(result)[1]
        self.assertIn("Respuesta registrada: 3,55", row[6])
        self.assertIn("tolerancia 0.1", row[6])
        self.assertEqual(row[3], "0,50")

    def test_no_option_reason_is_invented_when_bank_has_no_feedback(self):
        self.bank.write_text("::one::SECRET_QUESTION {=SECRET_CORRECT ~SECRET_WRONG}\n", encoding="utf-8")
        self.manifest["bank_sha256"] = hashlib.sha256(self.bank.read_bytes()).hexdigest()
        self.config["answer_columns"] = {"1": "Eleccion"}
        result = self.run_feedback(detailed=True)
        self.assertEqual(result["status"], "ok", result)
        feedback = self.output_rows(result)[1][6]
        self.assertIn("Selección A: sin crédito", feedback)
        self.assertNotIn("Confunde", feedback)

    def test_per_model_files_can_preserve_different_delimiters(self):
        second_model = copy.deepcopy(self.manifest["models"][0])
        second_model["id"] = "B"
        self.manifest["models"].append(second_model)
        second_row = self.rows[0].copy()
        second_row[0:2] = ["sintetico-002", "B"]
        first = self.input("first.csv")
        second = self.input("second.csv", rows=[second_row], delimiter="\t")
        result = self.run_feedback([first, second])
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.output_rows(result, 1, delimiter="\t")[1][0], "sintetico-002")

    def test_consolidation_of_incompatible_dialects_blocks_whole_batch(self):
        second_model = copy.deepcopy(self.manifest["models"][0])
        second_model["id"] = "B"
        self.manifest["models"].append(second_model)
        second_row = self.rows[0].copy()
        second_row[0:2] = ["sintetico-002", "B"]
        first = self.input("first.csv")
        second = self.input("second.csv", rows=[second_row], delimiter="\t")
        self.assert_blocked(self.run_feedback([first, second], consolidated=True), "INCOMPATIBLE_CONSOLIDATION")

    def test_colliding_sanitized_model_filenames_block(self):
        self.manifest["models"][0]["id"] = "A/B"
        second_model = copy.deepcopy(self.manifest["models"][0])
        second_model["id"] = "A_B"
        self.manifest["models"].append(second_model)
        self.rows[0][1] = "A/B"
        second = self.rows[0].copy()
        second[0:2] = ["sintetico-002", "A_B"]
        self.rows.append(second)
        self.assert_blocked(self.run_feedback(), "OUTPUT_NAME_COLLISION")

    def test_truncated_csv_row_blocks_batch_with_report(self):
        self.config["delimiter"] = ";"
        source = self.input(rows=[self.rows[0][:-1]])
        self.assert_blocked(self.run_feedback([source]), "INVALID_CSV")

    def test_duplicate_header_is_not_silently_overwritten(self):
        header = self.header.copy()
        header[-1] = header[-2]
        self.assert_blocked(self.run_feedback([self.input(header=header)]), "INVALID_CSV")

    def test_single_wrong_answer_is_review_not_marked_difficulty(self):
        self.rows[0][3] = "0"
        result = self.run_feedback()
        text = self.output_rows(result)[1][6]
        self.assertIn("Aspecto a revisar", text)
        self.assertNotIn("Dificultad acusada", text)

    def test_priorities_use_all_evidence_and_limit_three_concepts(self):
        questions, scores = [], {}
        # Equal losses: the concept with more questions has higher priority.
        for concept, count, score in (("aislado", 1, "0"), ("repetido", 2, "0"),
                                      ("parcial", 2, "0.4"), ("leve", 3, "0.9")):
            for _ in range(count):
                number = len(questions) + 1
                questions.append({"number": number, "source_id": str(number), "concepts": [concept]})
                scores[str(number)] = Decimal(score), Decimal(1)
        text = _conceptual(questions, scores, {})
        self.assertLess(text.index("repetido"), text.index("aislado"))
        self.assertIn("Dificultad acusada en repetido", text)
        self.assertIn("Aspecto a revisar: aislado", text)
        self.assertIn("Dificultad acusada en parcial", text)
        self.assertNotIn("leve", text)

    def test_correct_questions_count_towards_concept_threshold(self):
        questions = [{"number": index, "source_id": str(index), "concepts": ["concepto"]}
                     for index in (1, 2)]
        scores = {"1": (Decimal(0), Decimal(1)), "2": (Decimal(1), Decimal(1))}
        text = _conceptual(questions, scores, {})
        self.assertNotIn("Dificultad acusada", text)  # Exactly 50%; threshold is strictly lower.
        self.assertIn("Aspecto a revisar", text)
        text = _conceptual(questions, scores, {}, {"marked_threshold": "0.6"})
        self.assertIn("Dificultad acusada", text)

    def test_priority_configuration_is_validated_even_for_absent_students(self):
        self.rows[0][2] = "No presentado"
        self.config["feedback_priority"] = {"max_concepts": 0}
        self.assert_blocked(self.run_feedback(), "INVALID_INPUT")

    def test_only_explicit_student_references_are_included(self):
        self.manifest["metadata"]["concepts"]["balance"]["references"] = [
            {"title": "Guía de unidades", "path": "alumnado/materiales/unidades.md", "access": "estudiante"},
            {"title": "SECRET_SOLUTION", "path": "docente/soluciones/examen.md", "access": "docente"},
            {"title": "UNCLASSIFIED", "path": "material.md"}]
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        feedback = self.output_rows(result)[1][6]
        self.assertIn("alumnado/materiales/unidades.md", feedback)
        self.assertNotIn("SECRET", feedback)
        self.assertNotIn("UNCLASSIFIED", feedback)

    def test_unsafe_or_reserved_student_reference_blocks_export(self):
        for index, path in enumerate(("javascript:alert(1)", "file:///secret",
                                      "../secreto.md", "https://usuario:clave@example.org/apuntes",
                                      "docente/soluciones/examen.md", "%2e%2e/secreto.md",
                                      r"C:\secret.md", "//example.org/apuntes")):
            with self.subTest(path=path):
                self.out = self.root / f"reference-{index}"
                self.manifest["metadata"]["concepts"]["balance"]["references"] = [
                    {"title": "Referencia", "path": path, "access": "estudiante"}]
                self.assert_blocked(self.run_feedback(), "INVALID_METADATA")

    def test_question_reference_cannot_override_reserved_material_in_additive_manifest(self):
        from docencia.gift import escape_gift
        source_id = "banco-historia::one"
        self.bank.write_text(self.bank.read_text().replace("::one::", f"::{escape_gift(source_id)}::"),
                             encoding="utf-8")
        self.manifest["bank_sha256"] = hashlib.sha256(self.bank.read_bytes()).hexdigest()
        question = self.manifest["models"][0]["questions"][0]
        question.update(source_id=source_id, source_bank_id="banco-historia", source_question_id="one")
        metadata = self.manifest["metadata"]
        metadata["questions"][source_id] = metadata["questions"].pop("one")
        metadata["materials"] = {"examen": {"path": "referencias/examen-reservado.md", "access": "docente",
                                            "title": "Material reservado"}}
        metadata["questions"][source_id]["references"] = [
            {"path": "referencias/examen-reservado.md", "access": "estudiante", "title": "SECRET_RESERVED"}]
        result = self.run_feedback()
        self.assert_blocked(result, "INVALID_METADATA")
        self.assertNotIn("SECRET_RESERVED", json.dumps(result))

    def test_reference_must_be_declared_when_material_registry_exists(self):
        metadata = self.manifest["metadata"]
        metadata["materials"] = {"guia": {"path": "alumnado/guia.md", "access": "estudiante"}}
        metadata["questions"]["one"]["references"] = [
            {"path": "alumnado/otra.md", "access": "estudiante", "title": "Otra"}]
        self.assert_blocked(self.run_feedback(), "INVALID_METADATA")

    def test_registered_student_reference_allows_fragment_and_keeps_original_grades(self):
        metadata = self.manifest["metadata"]
        metadata["materials"] = {"guia": {"path": "alumnado/guia.md", "access": "estudiante"}}
        metadata["questions"]["one"]["references"] = [
            {"path": "alumnado/guia.md#unidades", "access": "estudiante", "title": "Guía de unidades"}]
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("alumnado/guia.md#unidades", self.output_rows(result)[1][6])
        self.assertEqual(self.output_rows(result)[1][7], "7,25")

    def test_legacy_without_materials_uses_explicit_safe_student_reference(self):
        self.manifest["metadata"]["questions"]["one"]["references"] = [
            {"path": "alumnado/guia.md", "access": "estudiante", "title": "Guía"},
            {"path": "referencias/reservado.md", "access": "docente", "title": "SECRET_RESERVED"}]
        result = self.run_feedback()
        self.assertEqual(result["status"], "ok", result)
        text = self.output_rows(result)[1][6]
        self.assertIn("alumnado/guia.md", text)
        self.assertNotIn("SECRET_RESERVED", text)

    def test_conflicting_material_access_blocks_even_if_question_claims_student(self):
        metadata = self.manifest["metadata"]
        metadata["materials"] = {"uno": {"path": "alumnado/guia.md", "access": "estudiante"},
                                "dos": {"path": "alumnado/./guia.md", "access": "docente"}}
        metadata["questions"]["one"]["references"] = [
            {"path": "alumnado/guia.md", "access": "estudiante", "title": "Guía"}]
        self.assert_blocked(self.run_feedback(), "INVALID_METADATA")

    def gradebook(self, rows=None, header=None):
        self.config["gradebook"] = {"identifier_column": "ID", "feedback_column": "Feedback actividad",
                                   "grade_column": "Nota actividad", "default_model": "A"}
        header = header or ["ID", "Nota actividad", "Feedback actividad", "Ajena"]
        rows = rows or [["sintetico-002", "8,75", "Conservar sin detalle", "reserva"],
                        ["sintetico-001", "7,25", "Comentario anterior", "Conservar"]]
        return self.input("libro.csv", rows=rows, header=header)

    def test_separate_gradebook_preserves_grades_rows_and_unmatched_comments(self):
        book = self.gradebook()
        before = book.read_bytes()
        source = self.input(header=self.header[:6] + self.header[7:],
                            rows=[self.rows[0][:6] + self.rows[0][7:]])
        self.config.pop("feedback_column")
        result = self.run_feedback([source], gradebook_path=book)
        self.assertEqual(result["status"], "ok", result)
        rows = self.output_rows(result)
        self.assertEqual([row[0] for row in rows[1:]], ["sintetico-002", "sintetico-001"])
        self.assertEqual(rows[1], ["sintetico-002", "8,75", "Conservar sin detalle", "reserva"])
        self.assertEqual(rows[2][1], "7,25")
        self.assertIn("Balance", rows[2][2])
        self.assertEqual(book.read_bytes(), before)
        self.assertEqual(result["audit"][0]["grade_preserved"], "7,25")

    def test_separate_gradebook_clears_absent_feedback_but_preserves_grade(self):
        self.rows[0][2:4] = ["No presentado", ""]
        result = self.run_feedback(gradebook_path=self.gradebook())
        self.assertEqual(result["status"], "ok", result)
        row = self.output_rows(result)[2]
        self.assertEqual(row[1:3], ["7,25", ""])

    def test_separate_gradebook_requires_original_numeric_grade_column(self):
        book = self.gradebook()
        self.config["gradebook"].pop("grade_column")
        self.assert_blocked(self.run_feedback(gradebook_path=book), "INVALID_INPUT")

    def test_gradebook_ambiguity_blocks_without_changing_any_original(self):
        book = self.gradebook(rows=[["sintetico-001", "7,25", "", ""],
                                   ["sintetico-001", "7,25", "", ""]])
        before = book.read_bytes()
        self.assert_blocked(self.run_feedback(gradebook_path=book), "DUPLICATE_GRADEBOOK_IDENTIFIER")
        self.assertEqual(book.read_bytes(), before)

    def test_detail_without_gradebook_match_blocks_instead_of_dropping_it(self):
        book = self.gradebook(rows=[["sintetico-099", "4", "Anterior", ""]])
        self.assert_blocked(self.run_feedback(gradebook_path=book), "UNMATCHED_DETAIL")

    def test_gradebook_requires_explicit_model_mapping(self):
        book = self.gradebook()
        self.config["gradebook"].pop("default_model")
        self.assert_blocked(self.run_feedback(gradebook_path=book), "INVALID_INPUT")

    def test_multiple_models_join_on_explicit_id_and_model_only(self):
        second = copy.deepcopy(self.manifest["models"][0])
        second["id"] = "B"
        self.manifest["models"].append(second)
        self.rows.append(self.rows[0].copy())
        self.rows[1][1] = "B"
        self.rows[1][3] = "1"
        book = self.gradebook(
            header=["ID", "Nota actividad", "Feedback actividad", "Ajena", "Modelo papel"],
            rows=[["sintetico-001", "8,00", "B anterior", "uno", "B"],
                  ["sintetico-001", "7,25", "A anterior", "dos", "A"]])
        self.config["gradebook"].pop("default_model")
        self.config["gradebook"]["model_column"] = "Modelo papel"
        result = self.run_feedback(gradebook_path=book, consolidated=True)
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(len(result["outputs"]), 3)
        rows = self.output_rows(result, 2)
        self.assertEqual([row[4] for row in rows[1:]], ["B", "A"])
        self.assertEqual([row[1] for row in rows[1:]], ["8,00", "7,25"])
        self.assertIn("puntuación máxima", rows[1][2])
        self.assertIn("Balance", rows[2][2])

    def test_global_grade_without_question_scores_never_infers_concepts(self):
        book = self.gradebook()
        self.rows[0][3] = ""
        self.assert_blocked(self.run_feedback(gradebook_path=book), "MISSING_SCORE")


if __name__ == "__main__":
    unittest.main()
