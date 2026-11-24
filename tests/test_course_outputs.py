"""Las entradas de un curso determinan el espacio de salida antes de escribir datos."""
import tempfile
import unittest
from pathlib import Path

from docencia.course_outputs import course_output
from docencia.feedback import build_feedback
from docencia.grading import export_grades
from docencia.project import initialize_course
from docencia.render import render_markdown


class ConfiguredOutputTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve() / "curso"
        initialize_course(self.root, spaces={"sources": ["Temas"], "generated": ["Producción"],
                                             "submissions": ["Recepción"]}, include=["Temas"])
        self.private = self.root / "Recepción/original.md"
        self.private.write_text("Entrega sintética", encoding="utf-8")

    def test_private_outputs_are_rejected_before_creating_reports(self):
        output = self.root / "Temas/publicar"
        with self.assertRaises(ValueError):
            export_grades(self.private, self.private, self.private, output)
        with self.assertRaises(ValueError):
            build_feedback(self.root / "Producción/modelo.json", [self.private], self.private, output)
        self.assertFalse(output.exists())

    def test_student_document_cannot_render_into_corpus_or_generated_space(self):
        for path in ["Temas/salida", "Producción/salida"]:
            with self.assertRaises(ValueError):
                render_markdown(self.private, self.root / path, html_only=True)
            self.assertFalse((self.root / path).exists())

    def test_new_files_follow_custom_spaces_and_course_boundary(self):
        output = self.root / "Producción/materiales/unidad-1"
        self.assertEqual(course_output(output, "generated"), output)
        with self.assertRaises(ValueError):
            course_output(self.root.parent / "salida", "generated", inputs=(self.root/"Temas",))
