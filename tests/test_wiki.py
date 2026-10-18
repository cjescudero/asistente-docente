"""Offline wiki reader: safe Markdown, stable navigation and protected inputs."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_wiki import MARKER, WikiError, build_wiki, document_href

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_wiki.py"


class WikiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lector-docente-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.guide = self.root / "mapa docente"
        self.guide.mkdir()
        self.sources = self.root / "materiales"
        self.sources.mkdir()
        for name in ("index.md", "LEEME.md", "incidencias.md", "log.md"):
            (self.guide / name).write_text("# " + name + "\n", encoding="utf-8")
        self.data = {"schema_version": 2, "title": "Mapa de física y humanidades", "course": None,
                     "source_roots": {"curso": "../materiales"}, "sources": [], "pages": []}
        self.page("contenidos/medición ñ.md", "Medición y crítica", "estudiante",
                  "# Medición y crítica\n\n## ¿Qué sabemos?\n\nEvidencia sintética.\n\n[Índice](../index.md)\n")
        self.page("reservado/examen.md", "Evaluación reservada", "docente",
                  "# Evaluación reservada\n\nSOLUCIÓN DOCENTE SINTÉTICA.\n", "evaluacion")
        self.output = self.guide / "index.html"
        self.save()

    def page(self, path, title, access, text, kind="tema"):
        file = self.guide / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
        self.data["pages"].append({"path": path, "title": title, "kind": kind,
                                  "access": access, "source_ids": []})
        return file

    def save(self):
        (self.guide / "fuentes.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def payload(self, output=None):
        text = (output or self.output).read_text(encoding="utf-8")
        match = re.search(r'<script id="wiki-data" type="application/json">(.*?)</script>', text, re.DOTALL)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def build(self, output=None, graph=None):
        self.save()
        result = build_wiki(self.guide, output, graph)
        return result, self.payload(output)

    def record(self, payload, path):
        return next(page for page in payload["documents"] if page["path"] == path)

    def test_teacher_reader_contains_registered_and_administrative_pages(self):
        result, payload = self.build()
        self.assertEqual(result["documents"], 6)
        self.assertEqual(payload["audience"], "docente")
        self.assertEqual(payload["index"], "index.md")
        self.assertEqual({d["path"] for d in payload["documents"]},
                         {"index.md", "LEEME.md", "incidencias.md", "log.md", "contenidos/medición ñ.md", "reservado/examen.md"})
        private = self.record(payload, "reservado/examen.md")
        self.assertEqual(private["access"], "docente")
        self.assertIn("SOLUCIÓN DOCENTE SINTÉTICA", private["html"])
        self.assertIn("Uso docente", self.output.read_text(encoding="utf-8"))

    def test_relative_links_reference_links_anchors_and_unicode_routes(self):
        (self.guide / "index.md").write_text(
            "# Índice\n\n[Concepto][c]\n\n[c]: <contenidos/medición ñ.md#qué-sabemos>\n", encoding="utf-8")
        _, payload = self.build()
        html = self.record(payload, "index.md")["html"]
        self.assertIn('href="#doc=contenidos%2Fmedici%C3%B3n%20%C3%B1.md&amp;section=qu%C3%A9-sabemos"', html)
        topic = self.record(payload, "contenidos/medición ñ.md")
        self.assertIn('href="#doc=index.md"', topic["html"])
        self.assertIn('id="section-qué-sabemos"', topic["html"])
        self.assertEqual(topic["sourceHref"], "contenidos/medici%C3%B3n%20%C3%B1.md")

    def test_same_page_heading_links_and_duplicate_slugs(self):
        path = self.guide / "contenidos/medición ñ.md"
        path.write_text("# Tema\n\n[Ir](#resumen-1)\n\n## Resumen\n\nA\n\n## Resumen\n\nB\n\n## Resumen-1\n", encoding="utf-8")
        _, payload = self.build()
        page = self.record(payload, "contenidos/medición ñ.md")
        self.assertEqual([h["slug"] for h in page["headings"]], ["tema", "resumen", "resumen-1", "resumen-1-1"])
        self.assertIn("&amp;section=resumen-1", page["html"])
        self.assertIn('id="section-resumen-1"', page["html"])

    def test_table_lists_and_code_render_but_source_html_cannot_execute(self):
        (self.guide / "index.md").write_text(
            '# Índice\n\n<script>window.PWNED=true</script>\n\n<img src=x onerror=alert(1)>\n\n'
            '| A | B |\n| --- | --- |\n| sí | ñ |\n\n- Uno\n- Dos\n\n```html\n<script>code</script>\n```\n', encoding="utf-8")
        _, payload = self.build()
        html = self.record(payload, "index.md")["html"]
        self.assertIn("<table>", html)
        self.assertIn("<li>Uno</li>", html)
        self.assertIn("&lt;script&gt;window.PWNED=true&lt;/script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)

    def test_url_schemes_remote_images_and_svg_are_inert(self):
        (self.sources / "vector.svg").write_text('<svg onload="alert(1)"/>', encoding="utf-8")
        (self.guide / "index.md").write_text(
            '# Índice\n\n[Web](https://example.invalid/x)\n\n[Correo](mailto:docente@example.invalid)\n\n'
            '[Malo](javascript:alert%281%29)\n\n[Datos](data:text/html,hello)\n\n[FTP](ftp://example.invalid/a)\n\n'
            '![Remota](https://example.invalid/pixel.png)\n\n![Vector](../materiales/vector.svg)\n', encoding="utf-8")
        _, payload = self.build()
        html = self.record(payload, "index.md")["html"]
        self.assertIn('href="https://example.invalid/x"', html)
        self.assertIn('href="mailto:docente@example.invalid"', html)
        self.assertNotIn('href="javascript:', html)
        self.assertNotIn('href="data:', html)
        self.assertNotIn('href="ftp:', html)
        self.assertNotIn("<img", html)
        self.assertIn("Imagen no incorporada: Remota", html)
        self.assertIn("Imagen no incorporada: Vector", html)

    def test_images_and_original_links_are_relative_to_custom_output(self):
        (self.sources / "figura 1.png").write_bytes(b"synthetic-test-raster")
        original = self.sources / "fuente ñ.txt"
        original.write_text("NEVER EMBED THIS ORIGINAL", encoding="utf-8")
        (self.guide / "index.md").write_text(
            '# Índice\n\n![Figura](<../materiales/figura 1.png>)\n\n[Fuente](<../materiales/fuente ñ.txt>)\n', encoding="utf-8")
        output = self.root / "lector.html"
        _, payload = self.build(output)
        html = self.record(payload, "index.md")["html"]
        self.assertIn('src="materiales/figura%201.png"', html)
        self.assertIn('href="materiales/fuente%20%C3%B1.txt"', html)
        self.assertNotIn("NEVER EMBED THIS ORIGINAL", output.read_text(encoding="utf-8"))
        self.assertEqual(self.record(payload, "index.md")["sourceHref"], "mapa%20docente/index.md")

    def test_title_script_closure_cannot_escape_embedded_json(self):
        malicious = "</script><script>globalThis.PWNED=true</script>\u2028"
        self.data["title"] = malicious
        self.data["pages"][0]["title"] = malicious
        _, payload = self.build()
        self.assertEqual(payload["title"], malicious)
        text = self.output.read_text(encoding="utf-8")
        self.assertNotIn(malicious, text)
        self.assertIn("\\u003c/script>", text)
        self.assertIn("\\u2028", text)

    def test_graph_and_document_href_contract_resolves_spaces(self):
        graph = self.root / "grafo docente.html"
        _, payload = self.build(graph=graph)
        self.assertEqual(payload["graphHref"], "../grafo%20docente.html")
        self.assertEqual(document_href("contenidos/medición ñ.md", graph, self.output),
                         "mapa%20docente/index.html#doc=contenidos%2Fmedici%C3%B3n%20%C3%B1.md")

    def test_generated_snapshot_is_idempotent_and_updates_after_markdown_edit(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = build_wiki(self.guide)
        mtime, html = self.output.stat().st_mtime_ns, self.output.read_bytes()
        self.assertEqual(result, build_wiki(self.guide))
        self.assertEqual(mtime, self.output.stat().st_mtime_ns)
        for path, content in before.items():
            self.assertEqual(content, path.read_bytes())
        target = self.guide / "contenidos/medición ñ.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nEdición nueva.\n", encoding="utf-8")
        build_wiki(self.guide)
        self.assertNotEqual(html, self.output.read_bytes())
        self.assertIn("Edición nueva", self.record(self.payload(), "contenidos/medición ñ.md")["html"])
        self.assertFalse(list(self.guide.glob(".wiki-*")))

    def test_unowned_output_is_not_overwritten(self):
        self.output.write_text("<h1>Manual propio</h1>", encoding="utf-8")
        with self.assertRaises(WikiError):
            build_wiki(self.guide)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "<h1>Manual propio</h1>")

    def test_output_symlink_is_not_followed(self):
        target = self.root / "original.html"
        target.write_text(MARKER + "\nOriginal", encoding="utf-8")
        self.output.symlink_to(target)
        with self.assertRaises(WikiError):
            build_wiki(self.guide)
        self.assertEqual(target.read_text(encoding="utf-8"), MARKER + "\nOriginal")

    def test_registered_original_is_protected_even_with_owned_marker(self):
        original = self.sources / "original.html"
        original.write_text(MARKER + "\nFuente", encoding="utf-8")
        self.data["sources"].append({"id": "fuente", "title": "Original", "root": "curso", "path": "original.html",
                                     "kind": "otro", "course": None, "currency": "vigente", "access": "docente",
                                     "reading": "pendiente", "reviewed_locators": [], "sha256": None, "page": None})
        self.save()
        with self.assertRaises(WikiError):
            build_wiki(self.guide, original)
        self.assertEqual(original.read_text(encoding="utf-8"), MARKER + "\nFuente")

    def test_reader_can_regenerate_when_markdown_links_to_generated_reader(self):
        self.build()
        path = self.guide / "index.md"
        path.write_text("# Índice\n\n[Visor](index.html)\n", encoding="utf-8")
        build_wiki(self.guide)
        self.assertIn('href="index.html"', self.record(self.payload(), "index.md")["html"])

    def test_refuses_graph_destination_overlap_and_non_html(self):
        for output in (self.guide / "index.md", self.guide / "fuentes.json", self.root / "missing" / "index.html"):
            with self.subTest(output=output), self.assertRaises(WikiError):
                build_wiki(self.guide, output)
        with self.assertRaises(WikiError):
            build_wiki(self.guide, self.output, graph=self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_map_aborts_without_creating_output(self):
        self.data["pages"][0]["path"] = "contenidos/inexistente.md"
        self.save()
        with self.assertRaisesRegex(WikiError, "Mapa inválido"):
            build_wiki(self.guide)
        self.assertFalse(self.output.exists())

    def test_cli_works_from_another_directory(self):
        run = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.guide)], cwd=self.root,
                             capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)["documents"], 6)
        self.assertTrue(self.output.is_file())


if __name__ == "__main__":
    unittest.main()
