"""Synthetic graph exports exercise provenance, privacy and filesystem safety."""
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_graph import GraphError, MARKER, build_graph


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_graph.py"


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="grafo-sintetico-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.guide = self.root / "mapa docente"
        self.guide.mkdir()
        self.public_root = self.root / "fuentes-a"
        self.private_root = self.root / "fuentes-b"
        self.public_root.mkdir()
        self.private_root.mkdir()
        self.original = self.public_root / "clase 1 (v2).txt"
        self.original.write_text("Fuente pública sintética.\n", encoding="utf-8")
        self.secret = self.private_root / "secreto-profesor.txt"
        self.secret.write_text("Solución sintética reservada.\n", encoding="utf-8")
        for name in ("index.md", "LEEME.md", "incidencias.md", "log.md"):
            (self.guide / name).write_text("# Documento administrativo\n", encoding="utf-8")
        self.data = {"schema_version": 2, "title": "MASTER_PRIVADO", "course": None,
                     "source_roots": {"publico": "../fuentes-a", "interno": "../fuentes-b"},
                     "sources": [self.source("publico", "Material público", "publico", self.original.name,
                                             "estudiante", "presentacion"),
                                 self.source("id-secreto", "TITULO_PRIVADO", "interno", self.secret.name,
                                             "docente", "examen")], "pages": []}
        self.page("contenidos/tema uno.md", "Tema público", "estudiante", ["publico"],
                  "[Original](../../fuentes-a/clase%201%20%28v2%29.txt#seccion)\n[Índice](../index.md)\n")
        self.page("reservado/solucion-secreta.md", "PAGINA_PRIVADA", "docente", ["id-secreto"],
                  "[Original](../../fuentes-b/secreto-profesor.txt)\n", kind="evaluacion")
        self.output = self.root / "grafo.html"
        self.save()

    @staticmethod
    def source(identifier, title, root, path, access, kind="apuntes"):
        return {"id": identifier, "title": title, "root": root, "path": path, "kind": kind,
                "course": None, "currency": "vigente", "access": access, "reading": "pendiente",
                "reviewed_locators": [], "sha256": None, "page": None}

    def page(self, path, title, access, source_ids, text="", kind="tema"):
        destination = self.guide / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("# " + title + "\n\n" + text, encoding="utf-8")
        self.data["pages"].append({"path": path, "title": title, "kind": kind,
                                   "access": access, "source_ids": source_ids})
        return destination

    def save(self):
        (self.guide / "fuentes.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def build(self, audience="docente", output=None):
        self.save()
        result = build_graph(self.guide, output or self.output, audience)
        return result, self.payload(output or self.output)

    def payload(self, output=None):
        text = (output or self.output).read_text(encoding="utf-8")
        match = re.search(r'<script\b[^>]*id=["\']graph-data["\'][^>]*>(.*?)</script>', text, re.DOTALL)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_teacher_multiroot_edges_are_only_real_markdown_links(self):
        result, payload = self.build()
        self.assertEqual(result["status"], "ok")
        self.assertEqual((result["nodes"], result["edges"]), (4, 2))
        edges = {(edge["source"], edge["target"]) for edge in payload["edges"]}
        self.assertEqual(edges, {("page:contenidos/tema uno.md", "source:publico"),
                                 ("page:reservado/solucion-secreta.md", "source:id-secreto")})
        nodes = {node["id"]: node for node in payload["nodes"]}
        self.assertEqual(nodes["source:id-secreto"]["kind"], "evaluacion")
        self.assertEqual(nodes["source:id-secreto"]["access"], "docente")
        self.assertEqual(nodes["source:publico"]["href"], "fuentes-a/clase%201%20%28v2%29.txt")
        self.assertEqual(nodes["page:contenidos/tema uno.md"]["href"], "mapa%20docente/contenidos/tema%20uno.md")
        self.assertFalse(any(name in node["id"] for node in payload["nodes"]
                             for name in ("index.md", "LEEME.md", "incidencias.md", "log.md")))

    def test_student_payload_contains_no_private_records_paths_or_counts(self):
        result, payload = self.build("estudiante")
        self.assertEqual(result["nodes"], 2)
        self.assertEqual(result["edges"], 1)
        self.assertEqual(payload["title"], "Mapa de materiales para estudiantes")
        self.assertTrue(all(node["href"] is None for node in payload["nodes"]))
        html = self.output.read_text(encoding="utf-8")
        for private in ("MASTER_PRIVADO", "TITULO_PRIVADO", "PAGINA_PRIVADA", "id-secreto",
                        "solucion-secreta", "fuentes-b", "secreto-profesor"):
            self.assertNotIn(private, html)
        self.assertNotIn("excluded", result)

    def test_source_ids_remove_student_page_even_without_a_markdown_link(self):
        self.data["pages"][0]["source_ids"].append("id-secreto")
        result, payload = self.build("estudiante")
        self.assertEqual([node["id"] for node in payload["nodes"]], ["source:publico"])
        self.assertEqual(result["edges"], 0)

    def test_transitive_private_dependency_propagates_through_student_pages(self):
        self.page("contenidos/intermedio.md", "Intermedio", "estudiante", [],
                  "[Interno](../reservado/solucion-secreta.md)\n")
        self.page("contenidos/inicio.md", "Inicio", "estudiante", [], "[Paso](intermedio.md)\n")
        _, payload = self.build("estudiante")
        ids = {node["id"] for node in payload["nodes"]}
        self.assertNotIn("page:contenidos/intermedio.md", ids)
        self.assertNotIn("page:contenidos/inicio.md", ids)
        self.assertIn("page:contenidos/tema uno.md", ids)

    def test_privacy_propagates_through_cycles(self):
        self.page("contenidos/ciclo-a.md", "Ciclo A", "estudiante", [], "[B](ciclo-b.md)\n")
        self.page("contenidos/ciclo-b.md", "Ciclo B", "estudiante", [],
                  "[A](ciclo-a.md)\n[Interno](../reservado/solucion-secreta.md)\n")
        _, payload = self.build("estudiante")
        self.assertFalse(any("ciclo-" in node["id"] for node in payload["nodes"]))

    def test_public_cycle_is_preserved(self):
        self.page("contenidos/ciclo-a.md", "Ciclo A", "estudiante", [], "[B](ciclo-b.md)\n")
        self.page("contenidos/ciclo-b.md", "Ciclo B", "estudiante", [], "[A](ciclo-a.md)\n")
        _, payload = self.build("estudiante")
        self.assertEqual(sum("ciclo-" in node["id"] for node in payload["nodes"]), 2)

    def test_unclassified_linked_original_is_not_assumed_public(self):
        (self.public_root / "sin-clasificar.txt").write_text("Sin metadatos.", encoding="utf-8")
        self.page("contenidos/no-publicable.md", "No publicable", "estudiante", [],
                  "[Original](../../fuentes-a/sin-clasificar.txt)\n")
        _, payload = self.build("estudiante")
        self.assertFalse(any("no-publicable" in node["id"] for node in payload["nodes"]))

    def test_aliases_for_same_original_keep_all_edges_and_privacy(self):
        alias = copy.deepcopy(self.data["sources"][0])
        alias.update(id="alias-privado", access="restringido", title="ALIAS_PRIVADO")
        self.data["sources"].append(alias)
        _, teacher = self.build()
        self.assertTrue(any(edge["target"] == "source:alias-privado" for edge in teacher["edges"]))
        _, student = self.build("estudiante")
        self.assertNotIn("page:contenidos/tema uno.md", {node["id"] for node in student["nodes"]})
        self.assertNotIn("ALIAS_PRIVADO", self.output.read_text(encoding="utf-8"))

    def test_provenance_does_not_invent_graph_edges(self):
        self.page("contenidos/concepto.md", "Concepto sin enlaces", "estudiante", ["publico"])
        _, payload = self.build()
        self.assertFalse(any(edge["source"] == "page:contenidos/concepto.md" for edge in payload["edges"]))

    def test_links_in_code_and_external_urls_do_not_become_edges(self):
        self.page("contenidos/codigo.md", "Código", "estudiante", [],
                  "[Web](https://example.invalid/no-fetch)\n[Ancla](#ancla)\n"
                  "`[Interno](../reservado/solucion-secreta.md)`\n"
                  "```markdown\n[Interno](../reservado/solucion-secreta.md)\n```\n")
        _, payload = self.build("estudiante")
        self.assertIn("page:contenidos/codigo.md", {node["id"] for node in payload["nodes"]})
        self.assertFalse(any(edge["source"] == "page:contenidos/codigo.md" for edge in payload["edges"]))

    def test_reference_links_and_space_paths_create_real_edges(self):
        self.page("contenidos/referencia.md", "Referencia", "estudiante", [],
                  "[Tema][tema]\n\n[tema]: <tema uno.md>\n")
        _, payload = self.build()
        self.assertIn({"source": "page:contenidos/referencia.md", "target": "page:contenidos/tema uno.md"}, payload["edges"])

    def test_script_closing_title_is_embedded_as_data(self):
        malicious = "</script><script>globalThis.PWNED=true</script>\u2028"
        self.data["pages"][0]["title"] = malicious
        _, payload = self.build()
        self.assertTrue(any(node["title"] == malicious for node in payload["nodes"]))
        html = self.output.read_text(encoding="utf-8")
        self.assertNotIn(malicious, html)
        self.assertIn("\\u003c/script>", html)
        self.assertIn("\\u2028", html)

    def test_idempotent_generation_changes_no_inputs_or_mtime(self):
        self.save()
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.root.rglob("*") if path.is_file()}
        first = build_graph(self.guide, self.output)
        graph_bytes, graph_mtime = self.output.read_bytes(), self.output.stat().st_mtime_ns
        second = build_graph(self.guide, self.output)
        self.assertEqual(first, second)
        self.assertEqual(self.output.read_bytes(), graph_bytes)
        self.assertEqual(self.output.stat().st_mtime_ns, graph_mtime)
        for path, state in before.items():
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), state)
        self.assertFalse(list(self.root.glob(".graph-*")))

    def test_generated_graph_can_be_updated(self):
        self.build()
        original = self.output.read_bytes()
        self.data["pages"][0]["title"] = "Título revisado"
        self.build()
        self.assertNotEqual(self.output.read_bytes(), original)
        self.assertTrue(self.output.read_text(encoding="utf-8").startswith(MARKER + "\n"))

    def test_existing_non_generated_file_is_never_overwritten(self):
        self.output.write_text("<h1>Contenido propio</h1>", encoding="utf-8")
        original = self.output.read_bytes()
        with self.assertRaises(GraphError):
            self.build()
        self.assertEqual(self.output.read_bytes(), original)
        self.assertFalse(list(self.root.glob(".graph-*")))

    def test_source_is_protected_even_if_it_contains_generator_marker(self):
        protected = self.public_root / "original.html"
        protected.write_text(MARKER + "\n<h1>Fuente docente</h1>", encoding="utf-8")
        self.data["sources"].append(self.source("original-html", "Original HTML", "publico", protected.name, "docente", "otro"))
        original = protected.read_bytes()
        with self.assertRaises(GraphError):
            self.build(output=protected)
        self.assertEqual(protected.read_bytes(), original)

    def test_output_symlink_is_rejected(self):
        own = self.root / "propio.html"
        own.write_text(MARKER + "\nPropio", encoding="utf-8")
        self.output.symlink_to(own)
        with self.assertRaises(GraphError):
            self.build()
        self.assertTrue(self.output.is_symlink())
        self.assertEqual(own.read_text(encoding="utf-8"), MARKER + "\nPropio")

    def test_validation_failure_does_not_create_or_replace_output(self):
        self.build()
        original = self.output.read_bytes()
        self.data["sources"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(GraphError, "Biblioteca inválida"):
            self.build()
        self.assertEqual(self.output.read_bytes(), original)
        self.output.unlink()
        with self.assertRaises(GraphError):
            self.build()
        self.assertFalse(self.output.exists())

    def test_missing_output_parent_is_not_created(self):
        destination = self.root / "no-creada" / "grafo.html"
        with self.assertRaises(GraphError):
            self.build(output=destination)
        self.assertFalse(destination.parent.exists())

    def test_valid_v1_library_requires_explicit_migration(self):
        old = self.root / "guia-antigua"
        old.mkdir()
        for name in ("index.md", "LEEME.md", "incidencias.md", "log.md"):
            (old / name).write_text("# Documento", encoding="utf-8")
        (old / "fuentes.json").write_text(json.dumps({"schema_version": 1, "title": "Anterior",
            "course": None, "sources_root": "../fuentes-a", "sources": []}), encoding="utf-8")
        with self.assertRaisesRegex(GraphError, "Migra"):
            build_graph(old, self.output)
        self.assertFalse(self.output.exists())

    def test_cli_from_external_cwd_is_reproducible(self):
        self.build()
        original = self.output.read_bytes()
        elsewhere = self.root / "otro-cwd"
        elsewhere.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.guide), "--output", str(self.output)],
                                cwd=elsewhere, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"], "ok")
        self.assertEqual(self.output.read_bytes(), original)

    def test_teacher_links_are_relative_to_output_directory(self):
        directory = self.root / "exportados"
        directory.mkdir()
        _, payload = self.build(output=directory / "grafo.html")
        source = next(node for node in payload["nodes"] if node["id"] == "source:publico")
        self.assertEqual(source["href"], "../fuentes-a/clase%201%20%28v2%29.txt")

    def test_export_contains_no_remote_script_stylesheet_or_fetch(self):
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertNotRegex(html, r'<script[^>]+src=["\']https?://')
        self.assertNotRegex(html, r'<link[^>]+href=["\']https?://')
        self.assertNotRegex(html, r"\bfetch\s*\(")

    def test_invalid_audience_is_rejected_before_writing(self):
        with self.assertRaises(GraphError):
            build_graph(self.guide, self.output, "publicar-todo")
        self.assertFalse(self.output.exists())

    def test_wiki_documents_include_own_linked_and_source_backed_pages(self):
        self.page("contenidos/otra.md", "Otra página", "estudiante", ["publico"],
                  "[Tema](tema%20uno.md)\n")
        self.save()
        wiki = self.guide / "index.html"
        result = build_graph(self.guide, self.output, wiki_output=wiki)
        self.assertTrue(wiki.is_file())
        self.assertEqual(result["wiki"]["status"], "ok")
        payload = self.payload()
        self.assertEqual(payload["wikiHref"], "mapa%20docente/index.html#doc=index.md")
        nodes = {node["id"]: node for node in payload["nodes"]}
        documents = nodes["source:publico"]["wikiDocuments"]
        self.assertEqual({doc["title"] for doc in documents}, {"Tema público", "Otra página"})
        self.assertTrue(all(doc["href"].startswith("mapa%20docente/index.html#doc=contenidos%2F") for doc in documents))
        self.assertTrue(all(doc["markdownHref"].endswith(".md") for doc in documents))
        self.assertEqual(nodes["page:contenidos/tema uno.md"]["wikiDocuments"][0]["title"], "Tema público")
        self.assertEqual(len(payload["edges"]), 3, "La navegación adicional no inventa relaciones conceptuales")

    def test_student_wiki_option_is_rejected_before_creating_files(self):
        wiki = self.guide / "index.html"
        with self.assertRaisesRegex(GraphError, "uso docente"):
            build_graph(self.guide, self.output, "estudiante", wiki_output=wiki)
        self.assertFalse(wiki.exists())
        self.assertFalse(self.output.exists())
        self.build("estudiante")
        self.assertNotIn("wikiHref", self.payload())
        self.assertTrue(all("wikiDocuments" not in node for node in self.payload()["nodes"]))

    def test_wiki_and_graph_cannot_share_a_destination(self):
        with self.assertRaisesRegex(GraphError, "diferentes"):
            build_graph(self.guide, self.output, wiki_output=self.output)
        self.assertFalse(self.output.exists())

    def test_unowned_graph_is_rejected_before_generating_wiki(self):
        self.output.write_text("Documento ajeno", encoding="utf-8")
        with self.assertRaises(GraphError):
            build_graph(self.guide, self.output, wiki_output=self.guide / "index.html")
        self.assertFalse((self.guide / "index.html").exists())

    def test_combined_generation_from_another_cwd_is_reproducible(self):
        wiki = self.guide / "index.html"
        args = [sys.executable, str(SCRIPT), str(self.guide), "--output", str(self.output),
                "--wiki-output", str(wiki)]
        result = subprocess.run(args, cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = self.output.read_bytes(), wiki.read_bytes()
        result = subprocess.run(args, cwd=self.public_root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(expected, (self.output.read_bytes(), wiki.read_bytes()))


if __name__ == "__main__":
    unittest.main()
