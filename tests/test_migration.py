"""Previsualización de migraciones: archivos intactos y enlaces revisables."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from docencia.migration import plan_migration


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="migracion-sintetica-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def file(self, relative, content="Fuente sintética\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def snapshot(self):
        return {file.relative_to(self.root).as_posix(): (file.read_bytes(), file.stat().st_mtime_ns)
                for file in self.root.rglob("*") if file.is_file()}

    def test_common_entrypoint_accepts_cli_from_to_format(self):
        from docencia.project import plan_migration as common
        self.file("origen.md")
        result = common(self.root, [{"from": "origen.md", "to": "docente/fuentes/tema.md"}])
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["moves"][0]["source"], "origen.md")

    def test_move_preview_hashes_source_and_changes_nothing(self):
        source = self.file("viejo/tema.md")
        before = self.snapshot()
        result = plan_migration(self.root, {"viejo": "docente/fuentes"})
        self.assertEqual(result["status"], "ready", result)
        self.assertTrue(result["requires_approval"])
        detail = result["moves"][0]["files"][0]
        self.assertEqual(detail["destination"], "docente/fuentes/tema.md")
        self.assertEqual(detail["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / "docente").exists())

    def test_collisions_block_even_identical_contents_and_keep_sources(self):
        self.file("primero/tema.md")
        self.file("segundo/tema.md")
        before = self.snapshot()
        result = plan_migration(self.root, {"primero/tema.md": "segundo/tema.md"})
        self.assertEqual(result["status"], "invalid")
        self.assertIn("Colisión", result["errors"][0])
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_and_overlapping_destinations_block(self):
        self.file("a.md")
        self.file("b.md")
        result = plan_migration(self.root, [
            {"source": "a.md", "destination": "destino.md"},
            {"source": "b.md", "destination": "destino.md"},
        ])
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(any("destination solapados" in item for item in result["errors"]))

    def test_overlapping_sources_block(self):
        self.file("antiguo/tema.md")
        result = plan_migration(self.root, {"antiguo": "nuevo", "antiguo/tema.md": "otro.md"})
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(any("source solapados" in item for item in result["errors"]))

    def test_incoming_outgoing_and_reference_links_are_reported(self):
        self.file("index.md", "# Índice\n\n[Tema](viejo/tema.md#uno)\n\n[ref]: viejo/tema.md\n")
        self.file("viejo/tema.md", "# Uno\n\n[Índice](../index.md)\n![Imagen](figura.png)\n")
        self.file("viejo/figura.png", "Imagen sintética")
        before = self.snapshot()
        result = plan_migration(self.root, {"viejo/tema.md": "docente/fuentes/tema.md"})
        self.assertEqual(result["status"], "ready")
        suggestions = {(link["document"], link["link"]): link["suggested_link"] for link in result["links"]}
        self.assertEqual(suggestions[("index.md", "viejo/tema.md#uno")], "docente/fuentes/tema.md#uno")
        self.assertEqual(suggestions[("index.md", "viejo/tema.md")], "docente/fuentes/tema.md")
        self.assertEqual(suggestions[("viejo/tema.md", "../index.md")], "../../index.md")
        self.assertEqual(suggestions[("viejo/tema.md", "figura.png")], "../../viejo/figura.png")
        self.assertEqual(self.snapshot(), before)

    def test_links_inside_moved_tree_are_recorded_without_false_required_change(self):
        self.file("viejo/uno.md", "[Dos](dos.md#titulo)\n[Web](https://example.com)\n[Sección](#titulo)\n")
        self.file("viejo/dos.md")
        result = plan_migration(self.root, {"viejo": "docente/fuentes"})
        self.assertEqual(len(result["links"]), 1)
        self.assertFalse(result["links"][0]["needs_update"])
        self.assertEqual(result["links"][0]["target_after"], "docente/fuentes/dos.md")

    def test_unicode_and_spaces_links_are_preserved(self):
        self.file("index.md", "[Tema](<antiguo/acción social.md>)\n")
        self.file("antiguo/acción social.md")
        result = plan_migration(self.root, {"antiguo": "docente/fuentes"})
        self.assertEqual(result["links"][0]["suggested_link"], "docente/fuentes/acci%C3%B3n%20social.md")

    def test_outside_paths_controls_and_self_containment_are_blocked(self):
        self.file("antiguo/tema.md")
        self.file("AGENTS.md")
        for moves in ({"../fuera": "dentro"}, {"AGENTS.md": "viejo.md"},
                      {"antiguo": "antiguo/sub"}, {"antiguo/tema.md": "AGENTS.md"}):
            with self.subTest(moves=moves):
                self.assertEqual(plan_migration(self.root, moves)["status"], "invalid")

    def test_symlink_in_source_blocks_and_is_not_followed(self):
        target = self.file("privado.md")
        alias = self.root / "viejo/alias.md"
        alias.parent.mkdir()
        try:
            alias.symlink_to(target)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"Enlaces no disponibles: {exc}")
        result = plan_migration(self.root, {"viejo": "nuevo"})
        self.assertEqual(result["status"], "invalid")
        self.assertIn("enlaces simbólicos", result["errors"][0])

    def test_unreadable_markdown_is_disclosed_and_empty_folder_can_be_planned(self):
        self.file("apuntes.md").write_bytes(b"\xff\xfe")
        (self.root / "vacio").mkdir()
        result = plan_migration(self.root, {"vacio": "docente/fuentes"})
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["moves"][0]["files"], [])
        self.assertTrue(any("apuntes.md" in warning for warning in result["warnings"]))

    def test_structured_records_are_flagged_for_semantic_review_without_rewrites(self):
        self.file("antiguo/tema.md")
        controls = {
            "proyecto-docente.json": "project",
            "docente/mapa-docente/fuentes.json": "map",
            "docente/evaluaciones/bancos/catalogo.json": "catalog",
            "docente/evaluaciones/bancos/biologia/metadatos.json": "metadata",
            "docente/borradores/experimento/docente/actividad.json": "activity",
            "docente/borradores/experimento/material-docente.json": "material",
            "docente/evaluaciones/parcial/manifest.json": "exam_snapshot",
        }
        for path in controls:
            self.file(path, '{"path":"antiguo/tema.md"}\n')
        self.file("resultados/privado.json", "{}\n")
        before = self.snapshot()
        result = plan_migration(self.root, {"antiguo": "fuentes/teoria"})
        self.assertEqual(result["status"], "ready")
        self.assertEqual({item["document"]: item["kind"] for item in result["metadata_reviews"]}, controls)
        self.assertTrue(all(item["requires_review"] for item in result["metadata_reviews"]))
        snapshot = next(item for item in result["metadata_reviews"] if item["kind"] == "exam_snapshot")
        self.assertIn("sin regenerar", snapshot["reason"])
        self.assertEqual(self.snapshot(), before)

    def test_metadata_review_tracks_moved_registry_location_and_skips_empty_plan(self):
        self.file("viejo/actividad.json", "{}")
        result = plan_migration(self.root, {"viejo": "creados/actividades/uno/docente"})
        self.assertEqual(result["metadata_reviews"][0]["document_after"],
                         "creados/actividades/uno/docente/actividad.json")
        self.assertEqual(plan_migration(self.root, {})["metadata_reviews"], [])


if __name__ == "__main__":
    unittest.main()
