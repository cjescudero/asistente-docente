"""Content-preserving rendering tests; browser checks are opt-in."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from docencia.render import PACKAGE_ROOT, document, external_output, fragment, print_pdf, render_markdown


HAS_MARKDOWN = importlib.util.find_spec("markdown_it") is not None


class TableAttributes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []

    def handle_starttag(self, tag, attrs):
        if tag in {"td", "th"}:
            self.cells.append((tag, dict(attrs)))


class RenderTests(unittest.TestCase):
    def test_moodle_format_preserves_html_entities_and_line_breaks(self):
        result = fragment("H<sub>2</sub>O &Delta;\n¿x < 3?", "moodle")
        self.assertIn("H<sub>2</sub>O Δ<br>", result)
        self.assertIn("¿x &lt; 3?", result)
        with self.assertRaises(ValueError):
            fragment("<svg>Dato esencial</svg>", "moodle")

    def test_plain_unicode_and_special_characters_are_escaped(self):
        result = fragment("¿x < 3 & y > 1?\nÑandú <script>literal</script>", "plain")
        self.assertIn("¿x &lt; 3 &amp; y &gt; 1?", result)
        self.assertIn("<br>", result)
        self.assertIn("Ñandú &lt;script&gt;literal&lt;/script&gt;", result)
        self.assertNotIn("<script>", result)

    def test_safe_html_preserves_scientific_notation_and_entities(self):
        result = fragment("<p>H<sub>2</sub>O y x<sup>2</sup>, &Delta; &le; 4.</p>", "html")
        self.assertIn("H<sub>2</sub>O", result)
        self.assertIn("x<sup>2</sup>", result)
        self.assertIn("Δ ≤ 4", result)

    def test_active_and_unrenderable_content_is_rejected_never_silently_deleted(self):
        snippets = [
            "<script>alert(1)</script>", "<style>p{color:red}</style>",
            "<iframe src='https://example.org'></iframe>", "<object>Figura</object>",
            "<embed src='figure.pdf'><p>Contenido posterior</p>",
            "<svg><text>Dato de una figura</text></svg>",
            "<math><mi>x</mi><mo>+</mo><mn>1</mn></math>",
            "<img src='data:image/png;base64,x' alt='Figura esencial'>",
        ]
        for snippet in snippets:
            with self.subTest(snippet=snippet), self.assertRaises(ValueError):
                fragment("<p>Antes</p>" + snippet + "<p>Después</p>", "html")

    def test_event_handlers_are_not_in_rendered_html(self):
        try:
            result = fragment('<p onclick="alert(1)">Contenido</p>', "html")
        except ValueError:
            return  # Explicit rejection also preserves the safety contract.
        self.assertIn("Contenido", result)
        self.assertNotIn("onclick", result)
        self.assertNotIn("alert", result)

    def test_table_spans_retain_the_relationship_between_headers_and_values(self):
        source = '<table><tr><th colspan="2">Temperatura</th></tr><tr><td rowspan="2">Fría</td><td>3</td></tr><tr><td>4</td></tr></table>'
        result = fragment(source, "html")
        parser = TableAttributes()
        parser.feed(result)
        self.assertEqual(parser.cells[0][1].get("colspan"), "2")
        self.assertEqual(parser.cells[1][1].get("rowspan"), "2")

    def test_invalid_table_spans_are_rejected(self):
        for value in ("-1", "2.5", "abc", "2 onclick=alert(1)"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fragment(f'<table><tr><td colspan="{value}">Dato</td></tr></table>', "html")

    def test_document_escapes_title_and_needs_no_script_for_plain_content(self):
        result = document("Ciencia <y> humanidades · ñ", "<p>Contenido</p>")
        self.assertIn("<title>Ciencia &lt;y&gt; humanidades · ñ</title>", result)
        self.assertIn("<meta charset='utf-8'>", result)
        self.assertNotIn("<script", result)

    def test_mathjax_is_embedded_locally_not_loaded_from_a_cdn(self):
        result = document("Fórmula", r"<p>\(x^2+1\)</p>", math=True)
        self.assertIn("window.MathJax", result)
        self.assertNotIn("<script src=", result)
        self.assertNotIn("<script async src=", result)

    def test_mathjax_missing_resource_has_an_explicit_error(self):
        with tempfile.TemporaryDirectory(prefix="asistente-render-test-") as tmp:
            with patch("docencia.render.MATHJAX", Path(tmp) / "missing.js"):
                with self.assertRaises(RuntimeError):
                    document("Fórmula", r"<p>\(x\)</p>", math=True)

    def test_output_directory_cannot_resolve_into_the_installed_plugin(self):
        for path in (PACKAGE_ROOT, PACKAGE_ROOT / "output", PACKAGE_ROOT / "docs" / ".." / "output"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                external_output(path)
        with tempfile.TemporaryDirectory(prefix="asistente-render-test-") as tmp:
            self.assertEqual(external_output(tmp), Path(tmp).resolve())

    @unittest.skipUnless(HAS_MARKDOWN, "markdown-it-py no está instalado")
    def test_markdown_preserves_math_delimiters_subscripts_and_lists(self):
        source = "# Tema: ñ\n\nValor \\(x_{i}+1\\).\n\n- Primer caso\n- Segundo caso\n\n\\[y=\\frac{a}{b}\\]"
        result = fragment(source, "markdown")
        self.assertIn("<h1>Tema: ñ</h1>", result)
        self.assertIn(r"\(x_{i}+1\)", result)
        self.assertIn(r"\[y=\frac{a}{b}\]", result)
        self.assertIn("<li>Primer caso</li>", result)
        self.assertNotIn("MATHPLACEHOLDER", result)

    @unittest.skipUnless(HAS_MARKDOWN, "markdown-it-py no está instalado")
    def test_markdown_tables_are_rendered(self):
        result = fragment("| Concepto | Valor |\n| --- | --- |\n| Energía | 2 |", "markdown")
        self.assertIn("<table>", result)
        self.assertIn("<th>Concepto</th>", result)
        self.assertIn("<td>Energía</td>", result)

    @unittest.skipUnless(HAS_MARKDOWN, "markdown-it-py no está instalado")
    def test_render_markdown_html_only_is_honest_and_preserves_source(self):
        with tempfile.TemporaryDirectory(prefix="asistente-render-test-") as tmp:
            root = Path(tmp)
            source = root / "apuntes-ñ.md"
            original = "# Apuntes\n\nUna idea principal: ñ, ¿sí?"
            source.write_text(original, encoding="utf-8")
            result = render_markdown(source, root / "output", html_only=True)
            self.assertTrue(Path(result["html"]).is_file())
            self.assertIsNone(result["pdf"])
            self.assertEqual(result["pdf_status"], "not_requested")
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertFalse(list((root / "output").glob("*.pdf")))
            with self.assertRaises(ValueError):
                render_markdown(source, root / "output", html_only=True)


@unittest.skipUnless(os.environ.get("RUN_PDF_TESTS") == "1", "Pruebas PDF opcionales: RUN_PDF_TESTS=1")
class PDFRenderTests(unittest.TestCase):
    def test_real_pdf_from_unicode_and_math_is_generated_offline(self):
        with tempfile.TemporaryDirectory(prefix="asistente-pdf-test-") as tmp:
            root = Path(tmp)
            html_path = root / "math.html"
            pdf_path = root / "math.pdf"
            content = r"<h1>¿Medición? · ñ</h1><p>\(x_i^2+\frac{1}{2}\)</p><p>\[\int_0^1 x\,dx=\frac{1}{2}\]</p>"
            html_path.write_text(document("Matemáticas", content, math=True), encoding="utf-8")
            ok, status = print_pdf(html_path, pdf_path)
            self.assertTrue(ok, status)
            self.assertEqual(status, "generated")
            self.assertTrue(pdf_path.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(pdf_path.stat().st_size, 1000)

    def test_unknown_tex_command_does_not_produce_a_false_successful_pdf(self):
        with tempfile.TemporaryDirectory(prefix="asistente-pdf-test-") as tmp:
            root = Path(tmp)
            html_path = root / "invalid.html"
            pdf_path = root / "invalid.pdf"
            html_path.write_text(document("Inválida", r"<p>\(\comandoInexistente{1}\)</p>", math=True), encoding="utf-8")
            ok, status = print_pdf(html_path, pdf_path)
            self.assertFalse(ok)
            self.assertIn("MathJax", status)
            self.assertFalse(pdf_path.exists())
            self.assertTrue(html_path.is_file())


if __name__ == "__main__":
    unittest.main()
