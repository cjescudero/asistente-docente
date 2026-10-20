"""Synthetic assignments and Moodle CSVs; student code is never executed."""

import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

from docencia.grading import GradingError, _PACKAGE_ROOT, export_grades


class GradingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="docencia-grading-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.out = self.root / "revision"
        self.input_path = self.root / "moodle.csv"
        self.eval_path = self.root / "evaluacion.json"
        self.config_path = self.root / "perfil.json"
        self.config = {
            "schema_version": 1, "profile": "worksheet", "advanced_grading": False,
            "activity_id": "fuentes-historicas", "attempt_id": "2026-ordinaria",
            "identifier_column": "Identificador", "grade_column": "Calificación",
            "feedback_column": "Comentarios", "grade_max": 10, "decimals": 2,
            "rounding": "half_up", "decimal_separator": ","}
        self.evaluation = {
            "schema_version": 1, "activity_id": "fuentes-historicas", "attempt_id": "2026-ordinaria",
            "activity_version": "1", "sources": ["rubrica.md", "enunciado.md"],
            "rubric": [{"id": "evidencia", "max_score": 4, "weight": 60},
                       {"id": "argumentacion", "max_score": 5, "weight": 40}],
            "evaluations": [{"student_id": "Participante 001", "status": "evaluated",
                "criteria": [{"id": "evidencia", "score": 3, "evidence": ["Informe, página 2: contrasta dos fuentes."]},
                             {"id": "argumentacion", "score": 4, "evidence": ["Informe, conclusión: delimita la tesis."]}],
                "total_points": 7, "feedback": "Explica la fiabilidad de cada fuente.",
                "justification": "La rúbrica exige contrastar autoría y contexto; falta contextualizar una fuente."}]}
        self.header = ["Identificador", "Nombre", "Calificación", "Comentarios", "Otra tarea", "Última modificación"]
        self.rows = [
            ["Participante 002", "Estudiante sintético", "", "Pendiente", "8,25", "2026-10-01"],
            ["Participante 001", "Estudiante sintética", "5,00", "Revisión anterior", "9,50", "2026-10-02"]]

    def save(self, delimiter=";"):
        self.eval_path.write_text(json.dumps(self.evaluation, ensure_ascii=False), encoding="utf-8")
        self.config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
        with self.input_path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, delimiter=delimiter, lineterminator="\r\n")
            writer.writerow(self.header)
            writer.writerows(self.rows)

    def run_export(self, **kwargs):
        self.save(**kwargs)
        return export_grades(self.eval_path, self.input_path, self.config_path, self.out)

    def output_rows(self, report, delimiter=";"):
        with Path(report["outputs"][0]).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.reader(stream, delimiter=delimiter))

    def assert_blocked(self, report, code=None):
        self.assertEqual(report["status"], "blocked", report)
        self.assertEqual(report["outputs"], [])
        self.assertFalse(list(self.out.glob("*.csv")))
        self.assertTrue(list(self.out.glob("grading-report*.json")))
        if code:
            self.assertIn(code, [item["code"] for item in report["incidents"]])

    def test_worksheet_computes_weighted_grade_and_preserves_original_cells(self):
        self.save()
        originals = [path.read_bytes() for path in (self.eval_path, self.input_path, self.config_path)]
        report = export_grades(self.eval_path, self.input_path, self.config_path, self.out)
        self.assertEqual(report["status"], "ok", report)
        result = self.output_rows(report)
        self.assertEqual(result[0], self.header)
        self.assertEqual(result[1], self.rows[0])
        self.assertEqual(result[2][2:4], ["7,70", self.evaluation["evaluations"][0]["feedback"]])
        self.assertEqual(result[2][:2], self.rows[1][:2])
        self.assertEqual(result[2][4:], self.rows[1][4:])
        self.assertEqual(report["audit"][0]["before"]["grade"], "5,00")
        self.assertEqual(report["audit"][0]["after"]["grade"], "7,70")
        self.assertEqual(report["updated"], 1)
        self.assertEqual(originals, [path.read_bytes() for path in (self.eval_path, self.input_path, self.config_path)])

    def test_gradebook_profile_and_quoted_multiline_fields(self):
        self.config["profile"] = "gradebook"
        self.config.pop("advanced_grading")
        self.config["decimal_separator"] = "."
        self.config["delimiter"] = "\t"
        self.rows[0][1] = 'Nombre "sintético"\nsegunda línea'
        report = self.run_export(delimiter="\t")
        self.assertEqual(report["status"], "ok", report)
        result = self.output_rows(report, delimiter="\t")
        self.assertEqual(result[1], self.rows[0])
        self.assertEqual(result[2][2], "7.70")

    def test_explicit_group_applies_same_assessment_to_each_member(self):
        entry = self.evaluation["evaluations"][0]
        entry.pop("student_id")
        entry.update(group_id="grupo-01", members=["Participante 001", "Participante 002"])
        report = self.run_export()
        self.assertEqual(report["status"], "ok", report)
        self.assertEqual([row[2] for row in self.output_rows(report)[1:]], ["7,70", "7,70"])
        self.assertEqual([row["identifier"] for row in report["audit"]], ["Participante 002", "Participante 001"])
        self.assertTrue(all(row["group_id"] == "grupo-01" for row in report["audit"]))

    def test_missing_group_member_blocks_batch_without_partial_grades(self):
        entry = self.evaluation["evaluations"][0]
        entry.pop("student_id")
        entry.update(group_id="grupo-01", members=["Participante 001", "No existe"])
        self.assert_blocked(self.run_export(), "UNMATCHED_ASSESSMENT")

    def test_duplicate_group_member_is_ambiguous(self):
        entry = self.evaluation["evaluations"][0]
        entry.pop("student_id")
        entry.update(group_id="grupo-01", members=["Participante 001", "Participante 001"])
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_individual_and_group_cannot_both_grade_same_member(self):
        group = copy.deepcopy(self.evaluation["evaluations"][0])
        group.pop("student_id")
        group.update(group_id="grupo-01", members=["Participante 001", "Participante 002"])
        self.evaluation["evaluations"].append(group)
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_duplicate_group_assessments_block(self):
        first = self.evaluation["evaluations"][0]
        first.pop("student_id")
        first.update(group_id="grupo-01", members=["Participante 001"])
        second = copy.deepcopy(first)
        second["members"] = ["Participante 002"]
        self.evaluation["evaluations"].append(second)
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_unresolved_delivery_preserves_grade_and_comment(self):
        for status in ("absent", "unreadable", "pending"):
            with self.subTest(status=status):
                self.out = self.root / status
                self.evaluation["evaluations"] = [{"student_id": "Participante 001",
                    "status": status, "justification": "Falta una entrega legible para revisar."}]
                report = self.run_export()
                self.assertEqual(report["status"], "ok", report)
                self.assertEqual(self.output_rows(report)[1:], self.rows)
                self.assertEqual(report["updated"], 0)
                self.assertIn("UNRESOLVED_SUBMISSION", [item["code"] for item in report["incidents"]])

    def test_pending_delivery_cannot_disguise_a_zero_score(self):
        self.evaluation["evaluations"][0]["status"] = "pending"
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_unknown_or_missing_identity_is_not_matched_by_name(self):
        self.evaluation["evaluations"][0]["student_id"] = "Estudiante sintética"
        self.assert_blocked(self.run_export(), "UNMATCHED_ASSESSMENT")

    def test_duplicate_csv_id_blocks(self):
        self.rows.append(self.rows[1].copy())
        self.assert_blocked(self.run_export(), "DUPLICATE_IDENTIFIER")

    def test_blank_id_blocks_even_without_an_assessment(self):
        self.rows[0][0] = ""
        self.assert_blocked(self.run_export(), "MISSING_IDENTIFIER")

    def test_activity_and_attempt_bind_the_whole_batch(self):
        self.config["attempt_id"] = "otra-convocatoria"
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_explicit_activity_attempt_columns_preserve_other_attempts(self):
        self.config.update(activity_column="Actividad", attempt_column="Intento")
        self.header.extend(["Actividad", "Intento"])
        for row in self.rows:
            row.extend(["fuentes-historicas", "2026-ordinaria"])
        previous = self.rows[1].copy()
        previous[-1] = "2025-ordinaria"
        self.rows.insert(0, previous)
        report = self.run_export()
        self.assertEqual(report["status"], "ok", report)
        result = self.output_rows(report)
        self.assertEqual(result[1], previous)
        self.assertEqual(result[3][2], "7,70")

    def test_advanced_moodle_rubric_blocks_worksheet_but_keeps_evidence(self):
        self.config["advanced_grading"] = True
        report = self.run_export()
        self.assert_blocked(report, "ADVANCED_GRADING_UNSUPPORTED")
        self.assertEqual(report["evaluation"], self.evaluation)
        self.assertTrue(report["audit"])
        self.assertEqual(report["updated"], 0)

    def test_worksheet_must_explicitly_declare_advanced_grading(self):
        self.config.pop("advanced_grading")
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_weights_must_sum_to_one_hundred(self):
        self.evaluation["rubric"][0]["weight"] = 50
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_missing_criterion_or_evidence_blocks(self):
        self.evaluation["evaluations"][0]["criteria"][0]["evidence"] = []
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_wrong_sum_blocks(self):
        self.evaluation["evaluations"][0]["total_points"] = 8
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_nonfinite_negative_and_excessive_criterion_scores_block(self):
        for score in ("NaN", -1, 5):
            with self.subTest(score=score):
                self.out = self.root / ("bad-score-" + str(score))
                self.evaluation["evaluations"][0]["criteria"][0]["score"] = score
                self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_declared_rounding_is_used(self):
        self.evaluation["rubric"] = [{"id": "medida", "max_score": 100, "weight": 100}]
        entry = self.evaluation["evaluations"][0]
        entry["criteria"] = [{"id": "medida", "score": "42.5", "evidence": ["Registro experimental, filas 1-5."]}]
        entry.pop("total_points")
        self.config["decimals"] = 1
        for rounding, expected in (("half_up", "4,3"), ("half_even", "4,2"), ("down", "4,2")):
            with self.subTest(rounding=rounding):
                self.out = self.root / rounding
                self.config["rounding"] = rounding
                report = self.run_export()
                self.assertEqual(report["status"], "ok", report)
                self.assertEqual(self.output_rows(report)[2][2], expected)

    def test_nonrepresentable_scale_never_exports_a_grade_above_maximum(self):
        self.config.update(grade_max="2.5", decimals=0, rounding="half_up")
        entry = self.evaluation["evaluations"][0]
        entry["criteria"][0]["score"] = 4
        entry["criteria"][1]["score"] = 5
        entry["total_points"] = 9
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_fractional_scale_with_sufficient_precision_preserves_maximum(self):
        self.config.update(grade_max="2.5", decimals=1, rounding="half_up")
        entry = self.evaluation["evaluations"][0]
        entry["criteria"][0]["score"] = 4
        entry["criteria"][1]["score"] = 5
        entry["total_points"] = 9
        result = self.run_export()
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.output_rows(result)[2][2], "2,5")

    def test_unknown_config_fields_do_not_silently_change_grading(self):
        self.config["grade_mx"] = 100
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_unknown_criteria_and_duplicate_criteria_block(self):
        self.evaluation["evaluations"][0]["criteria"][0]["id"] = "inventado"
        self.assert_blocked(self.run_export(), "INVALID_ASSESSMENT")

    def test_existing_output_is_preserved(self):
        first = self.run_export()
        target = Path(first["outputs"][0])
        before = target.read_bytes()
        second = self.run_export()
        self.assertEqual(second["status"], "blocked")
        self.assertEqual(target.read_bytes(), before)
        self.assertTrue((self.out / "grading-report-2.json").exists())

    def test_cannot_write_to_plugin_installation(self):
        with self.assertRaises(GradingError):
            export_grades("unused.json", "unused.csv", "unused.json", _PACKAGE_ROOT / "grading-results")
        self.assertFalse((_PACKAGE_ROOT / "grading-results").exists())

    def test_export_does_not_open_or_execute_student_files(self):
        sentinel = self.root / "executed"
        code = self.root / "student.py"
        code.write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n",
                        encoding="utf-8")
        self.evaluation["evaluations"][0]["criteria"][0]["evidence"] = ["student.py:1; análisis estático del fichero."]
        report = self.run_export()
        self.assertEqual(report["status"], "ok", report)
        self.assertFalse(sentinel.exists())

    def activity_record(self):
        activity = self.root / "actividad"
        activity.mkdir()
        (activity / "enunciado.md").write_text("# Comparar fuentes\n", encoding="utf-8")
        (activity / "rubrica.md").write_text("# Evidencia y argumentación\n", encoding="utf-8")
        registry = {"schema_version": 1, "id": "fuentes-historicas", "version": "1",
                    "files": {"statement": {"path": "enunciado.md", "audience": "estudiante"},
                              "rubric": {"path": "rubrica.md", "audience": "docente"},
                              "templates": []}}
        path = activity / "actividad.json"
        path.write_text(json.dumps(registry), encoding="utf-8")
        self.config["activity_record"] = "actividad/actividad.json"
        return path, registry

    def test_activity_record_binds_version_and_hashes_documents(self):
        self.activity_record()
        (self.root / "proyecto-docente.json").write_text('{"schema_version":1}', encoding="utf-8")
        result = self.run_export()
        self.assertEqual(result["status"], "ok", result)
        record = result["activity_record"]
        self.assertEqual(record["id"], "fuentes-historicas")
        self.assertEqual(record["version"], "1")
        self.assertTrue(record["course_boundary_checked"])
        self.assertEqual(set(record["documents"]), {"statement", "rubric"})
        self.assertEqual(len(record["documents"]["rubric"]["sha256"]), 64)

    def test_activity_record_version_mismatch_blocks(self):
        self.activity_record()
        self.evaluation["activity_version"] = "anterior"
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_activity_record_missing_document_blocks(self):
        self.activity_record()
        (self.root / "actividad" / "rubrica.md").unlink()
        self.assert_blocked(self.run_export(), "INVALID_INPUT")

    def test_activity_record_without_known_course_reports_limit(self):
        self.activity_record()
        result = self.run_export()
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("COURSE_BOUNDARY_UNVERIFIED", [item["code"] for item in result["incidents"]])

    def test_legacy_evaluations_report_unverified_document_binding(self):
        result = self.run_export()
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("ACTIVITY_RECORD_UNVERIFIED", [item["code"] for item in result["incidents"]])

    def test_activity_symlink_cannot_escape_known_course(self):
        self.activity_record()
        (self.root / "proyecto-docente.json").write_text("{}", encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="other-course-") as external:
            secret = Path(external) / "rubrica.md"
            secret.write_text("# Otra rúbrica", encoding="utf-8")
            rubric = self.root / "actividad" / "rubrica.md"
            rubric.unlink()
            try:
                rubric.symlink_to(secret)
            except (OSError, NotImplementedError):
                self.skipTest("El sistema no permite crear enlaces simbólicos.")
            self.assert_blocked(self.run_export(), "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
