"""Synthetic fixtures for the read-only Markdown library validator."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_library.py"
SPEC = importlib.util.spec_from_file_location("validate_library", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
validate_library = MODULE.validate_library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="biblioteca-sintetica-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.guide = self.root / "guia"
        self.materials = self.root / "materiales"
        self.guide.mkdir()
        self.materials.mkdir()
        (self.guide / "fuentes").mkdir()
        for filename in ("index.md", "LEEME.md", "incidencias.md", "log.md"):
            (self.guide / filename).write_text("# Biblioteca sintética\n", encoding="utf-8")
        (self.guide / "index.md").write_text("# Índice\n\n[Apunte](fuentes/apunte.md)\n", encoding="utf-8")
        (self.guide / "fuentes" / "apunte.md").write_text("# Apunte\n\nLectura de la sección inicial.\n", encoding="utf-8")
        self.original = self.materials / "apunte.txt"
        self.original.write_text("Fuente sintética: acción, ñ y energía.\n", encoding="utf-8")
        self.data = {"schema_version": 1, "title": "Biblioteca de ejemplo", "course": None,
                     "sources_root": "../materiales", "sources": [{
                         "id": "apunte-uno", "title": "Apunte sintético", "path": "apunte.txt",
                         "kind": "apuntes", "course": None, "currency": "vigente",
                         "access": "docente", "reading": "completa", "reviewed_locators": ["sección 1"],
                         "sha256": hashlib.sha256(self.original.read_bytes()).hexdigest(),
                         "page": "fuentes/apunte.md"}]}
        self.save()

    def save(self):
        (self.guide / "fuentes.json").write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def validate(self, **kwargs):
        self.save()
        return validate_library(self.guide, **kwargs)

    def assert_invalid(self, result, text=None):
        self.assertEqual(result["status"], "invalid", result)
        self.assertTrue(result["errors"])
        if text:
            self.assertTrue(any(text in item for item in result["errors"]), result)

    def test_minimal_library_passes_without_writing_any_file(self):
        def snapshot():
            return {str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
                    for path in self.root.rglob("*") if path.is_file()}
        before = snapshot()
        result = validate_library(self.guide)
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(result["sources"], 1)
        self.assertEqual(result["errors"], [])
        self.assertEqual(snapshot(), before)
        self.assertTrue(any("anclas" in warning for warning in result["warnings"]))

    def test_changed_source_is_stale_error(self):
        self.original.write_text("Un cambio posterior.\n", encoding="utf-8")
        self.assert_invalid(self.validate(), "sha256 no coincide")

    def test_missing_source_is_error(self):
        self.original.unlink()
        self.assert_invalid(self.validate(), "archivo existente")

    def test_duplicate_source_identifiers_block(self):
        self.data["sources"].append(copy.deepcopy(self.data["sources"][0]))
        self.assert_invalid(self.validate(), "id duplicado")

    def test_partial_requires_reviewed_locators(self):
        self.data["sources"][0].update(reading="parcial", reviewed_locators=[])
        self.assert_invalid(self.validate(), "requiere localizadores")

    def test_partial_requires_a_source_page(self):
        self.data["sources"][0].update(reading="parcial", page=None)
        self.assert_invalid(self.validate(), "requiere page")

    def test_pending_without_page_is_valid(self):
        self.data["sources"][0].update(reading="pendiente", reviewed_locators=[], page=None)
        self.assertEqual(self.validate()["status"], "ok")

    def test_unreadable_source_without_page_is_valid(self):
        self.data["sources"][0].update(reading="no_legible", reviewed_locators=[], page=None)
        self.assertEqual(self.validate()["status"], "ok")

    def test_pending_cannot_claim_reviewed_locators(self):
        self.data["sources"][0].update(reading="pendiente", page=None)
        self.assert_invalid(self.validate(), "localizadores vacíos")

    def test_null_sha_warns_without_being_fabricated(self):
        self.data["sources"][0]["sha256"] = None
        result = self.validate()
        self.assertEqual(result["status"], "ok", result)
        self.assertTrue(any("sin sha256" in warning for warning in result["warnings"]))
        stored = json.loads((self.guide / "fuentes.json").read_text())
        self.assertIsNone(stored["sources"][0]["sha256"])

    def test_empty_library_is_valid_with_warning(self):
        self.data["sources"] = []
        result = self.validate()
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(result["sources"], 0)
        self.assertTrue(any("todavía no contiene fuentes" in warning for warning in result["warnings"]))

    def test_source_path_escape_rejected_even_when_file_exists(self):
        self.data["sources"][0]["path"] = "../guia/index.md"
        self.assert_invalid(self.validate(), "fuera de su carpeta")

    def test_symlink_escape_is_rejected(self):
        self.original.unlink()
        self.original.symlink_to(self.guide / "index.md")
        self.assert_invalid(self.validate(), "fuera de su carpeta")

    def test_source_page_cannot_escape_guide(self):
        outside = self.materials / "externa.md"
        outside.write_text("# Afuera", encoding="utf-8")
        self.data["sources"][0]["page"] = "../materiales/externa.md"
        self.assert_invalid(self.validate(), "fuera de su carpeta")

    def test_source_page_symlink_must_stay_inside_guide(self):
        page = self.guide / "fuentes" / "apunte.md"
        page.unlink()
        page.symlink_to(self.original)
        self.assert_invalid(self.validate(), "fuera de")

    def test_missing_source_page_is_error(self):
        (self.guide / "fuentes" / "apunte.md").unlink()
        self.assert_invalid(self.validate(), "archivo existente")

    def test_required_documents_must_exist_and_be_nonempty(self):
        (self.guide / "log.md").write_text(" \n", encoding="utf-8")
        (self.guide / "incidencias.md").unlink()
        result = self.validate()
        self.assert_invalid(result, "log.md")
        self.assertTrue(any("incidencias.md" in error for error in result["errors"]))

    def test_sources_root_override_supports_moved_originals(self):
        moved = self.root / "otra carpeta"
        self.materials.rename(moved)
        result = validate_library(self.guide, moved)
        self.assertEqual(result["status"], "ok", result)

    def test_cli_uses_guide_location_not_current_working_directory(self):
        elsewhere = self.root / "directorio independiente"
        elsewhere.mkdir()
        process = subprocess.run([sys.executable, str(SCRIPT), str(self.guide)], cwd=elsewhere,
                                 text=True, capture_output=True, check=False)
        self.assertEqual(process.returncode, 0, process.stderr + process.stdout)
        self.assertEqual(json.loads(process.stdout)["status"], "ok")
        self.assertEqual(process.stderr, "")

    def test_cli_invalid_library_returns_one_and_json(self):
        self.original.unlink()
        process = subprocess.run([sys.executable, str(SCRIPT), str(self.guide)],
                                 text=True, capture_output=True, check=False)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(json.loads(process.stdout)["status"], "invalid")
        self.assertEqual(process.stderr, "")

    def test_cli_sources_root_override_from_different_cwd(self):
        moved = self.root / "nuevas fuentes"
        self.materials.rename(moved)
        process = subprocess.run([sys.executable, str(SCRIPT), str(self.guide),
                                  "--sources-root", str(moved)], cwd=self.root,
                                 text=True, capture_output=True, check=False)
        self.assertEqual(process.returncode, 0, process.stdout)
        self.assertEqual(json.loads(process.stdout)["status"], "ok")

    def test_local_links_resolve_to_guide_or_explicit_source_root(self):
        (self.guide / "index.md").write_text(
            "[Guía](LEEME.md#un-ancla-no-comprobada)\n"
            "[Original](../materiales/apunte.txt)\n"
            "[Página](fuentes/apunte.md)\n"
            "[Referencia][original]\n[original]: ../materiales/apunte.txt\n",
            encoding="utf-8")
        self.assertEqual(self.validate()["status"], "ok")

    def test_percent_encoded_paths_and_angle_brackets_are_supported(self):
        (self.guide / "notas con espacios.md").write_text("# Nota", encoding="utf-8")
        (self.guide / "index.md").write_text(
            "[Nota](notas%20con%20espacios.md)\n[Nota](<notas con espacios.md>)\n", encoding="utf-8")
        self.assertEqual(self.validate()["status"], "ok")

    def test_broken_local_links_and_images_are_errors(self):
        (self.guide / "index.md").write_text("[Roto](no-existe.md)\n![Imagen](no-existe.png)\n", encoding="utf-8")
        result = self.validate()
        self.assert_invalid(result, "no-existe.md")
        self.assertTrue(any("no-existe.png" in error for error in result["errors"]))

    def test_broken_reference_definition_is_error(self):
        (self.guide / "index.md").write_text("[Referencia][roto]\n\n[roto]: falta.md \"Título\"\n", encoding="utf-8")
        self.assert_invalid(self.validate(), "enlace local roto")

    def test_external_urls_anchors_and_fenced_examples_are_ignored(self):
        (self.guide / "index.md").write_text(
            "[Web](https://invalid.example/not-fetched)\n[Correo](mailto:nadie@example.test)\n"
            "[Ancla](#no-comprobada)\n`[Ejemplo](no-existe.md)`\n"
            "```md\n[Ejemplo](tampoco-existe.md)\n```\n", encoding="utf-8")
        self.assertEqual(self.validate()["status"], "ok")

    def test_absolute_and_escaped_markdown_links_are_rejected(self):
        for target in (str(self.original), "C:/privado/fuente.pdf", "file:///tmp/fuente.md",
                       "../../fuera.md", "%2Fetc/passwd"):
            with self.subTest(target=target):
                (self.guide / "index.md").write_text(f"[Inseguro]({target})\n", encoding="utf-8")
                self.assert_invalid(self.validate())

    def test_source_symlink_within_root_is_allowed(self):
        original_name = self.materials / "renombrado.txt"
        self.original.rename(original_name)
        self.original.symlink_to(original_name.name)
        self.assertEqual(self.validate()["status"], "ok")

    def test_malformed_json_is_reported_without_traceback(self):
        (self.guide / "fuentes.json").write_text("{invalid", encoding="utf-8")
        self.assert_invalid(validate_library(self.guide))

    def test_malformed_top_level_values_never_raise_type_error(self):
        for value in (None, [], "text", 1):
            with self.subTest(value=value):
                (self.guide / "fuentes.json").write_text(json.dumps(value), encoding="utf-8")
                self.assert_invalid(validate_library(self.guide))
        for field, value in (("schema_version", True), ("title", []), ("course", {}),
                             ("sources_root", {}), ("sources", {})):
            with self.subTest(field=field):
                original = self.data[field]
                self.data[field] = value
                self.assert_invalid(self.validate())
                self.data[field] = original

    def test_malformed_source_fields_never_raise_type_error(self):
        original = copy.deepcopy(self.data["sources"][0])
        for field, value in (("id", {}), ("id", "Not-Kebab"), ("title", []), ("path", []),
                             ("kind", []), ("course", []), ("currency", {}), ("access", []),
                             ("reading", {}), ("reviewed_locators", [None]), ("sha256", []),
                             ("sha256", "A" * 64), ("page", {})):
            with self.subTest(field=field, value=value):
                self.data["sources"][0] = {**original, field: value}
                self.assert_invalid(self.validate())
        self.data["sources"] = [None, [], 1, "texto"]
        self.assert_invalid(self.validate())

    def test_sources_require_exact_fields(self):
        self.data["sources"][0]["inventado"] = "valor"
        self.assert_invalid(self.validate(), "campos no reconocidos")
        self.data["sources"][0].pop("inventado")
        self.data["sources"][0].pop("course")
        self.assert_invalid(self.validate(), "campos obligatorios")


if __name__ == "__main__":
    unittest.main()
