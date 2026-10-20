"""Proyectos sintéticos: conservación, selección y límites de lectura/escritura."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from docencia.project import (
    AGENTS_BLOCK, CONFIG_NAME, LEEME_CONTENT, PLUGIN_ROOT, PROJECT_DIRECTORIES,
    check_project, find_project, initialize_project, load_project, source_allowed,
)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="curso-sintetico-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "curso con ñ"

    def file(self, relative, text="Documento sintético: energía y ciudadanía.\n"):
        file = self.root / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
        return file

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()}

    def save(self, data):
        (self.root / CONFIG_NAME).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def symlink(self, path, target):
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.symlink_to(target, target_is_directory=target.is_dir())
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"El sistema no permite enlaces simbólicos: {exc}")

    def test_new_project_is_portable_and_does_not_create_wiki(self):
        result = initialize_project(self.root)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(load_project(self.root), {
            "schema_version": 1, "structure": "curso-v1",
            "sources": {"selected": False, "include": [], "exclude": []}, "map": None})
        for relative in PROJECT_DIRECTORIES:
            self.assertTrue((self.root / relative).is_dir())
        self.assertEqual(list((self.root / "docente/mapa-docente").iterdir()), [])
        self.assertIn("`redactar-espanol-claro`", (self.root / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(check_project(self.root)["selection_status"], "pending")

    def test_second_initialization_is_byte_and_timestamp_identical(self):
        self.file("docente/fuentes/apuntes.md")
        initialize_project(self.root, include=["docente/fuentes"])
        before = self.snapshot()
        result = initialize_project(self.root)
        self.assertEqual(result["created"], [])
        self.assertEqual(result["updated"], [])
        self.assertEqual(result["proposals"], [])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(check_project(self.root)["status"], "ok")

    def test_previous_course_adds_submissions_without_rewriting_or_selecting_them(self):
        initialize_project(self.root, include=["alumnado/materiales"])
        (self.root / "docente/resultados/entregas").rmdir()
        agents = self.file("AGENTS.md", "# Reglas previas\nNo propongas un mapa.\n")
        guide = self.file("LEEME.md", "# Guía conservada\n")
        original = self.file("docente/resultados/lote-antiguo/respuesta.txt", "Entrega sintética.")
        before = self.snapshot()
        preview = initialize_project(self.root, dry_run=True)
        self.assertIn("docente/resultados/entregas/", preview["would_create"])
        self.assertEqual(self.snapshot(), before)
        result = initialize_project(self.root)
        self.assertEqual(result["status"], "pending_approval")
        self.assertTrue((self.root / "docente/resultados/entregas").is_dir())
        self.assertEqual(agents.read_bytes(), before["AGENTS.md"][0])
        self.assertEqual(guide.read_bytes(), before["LEEME.md"][0])
        self.assertEqual(original.read_bytes(), before["docente/resultados/lote-antiguo/respuesta.txt"][0])
        submission = self.file("docente/resultados/entregas/actividad/ordinaria/originales/evidencia.txt")
        self.assertFalse(source_allowed(self.root, load_project(self.root), submission))
        self.assertIsNone(load_project(self.root)["map"])
        self.assertEqual(list((self.root / "docente/mapa-docente").iterdir()), [])

    def test_dry_run_does_not_create_root(self):
        result = initialize_project(self.root, include=["docente/fuentes"], dry_run=True)
        self.assertEqual(result["status"], "dry_run")
        self.assertFalse(self.root.exists())
        self.assertIn(CONFIG_NAME, result["would_create"])
        self.assertEqual(result["created"], [])

    def test_existing_instructions_and_guide_are_preserved_with_exact_proposals(self):
        agents = self.file("AGENTS.md", "# Mis reglas\n\nNo traduzcas las citas.\n")
        guide = self.file("LEEME.md", "# Guía propia\n")
        before = self.snapshot()
        result = initialize_project(self.root)
        self.assertEqual(result["status"], "pending_approval")
        self.assertEqual(agents.read_bytes(), before["AGENTS.md"][0])
        self.assertEqual(guide.read_bytes(), before["LEEME.md"][0])
        proposals = {item["path"]: item for item in result["proposals"]}
        self.assertIn("No traduzcas las citas.", proposals["AGENTS.md"]["proposed_content"])
        self.assertIn(AGENTS_BLOCK, proposals["AGENTS.md"]["proposed_content"])
        self.assertEqual(proposals["LEEME.md"]["proposed_content"], LEEME_CONTENT)
        self.assertTrue((self.root / "docente/borradores").is_dir())

    def test_existing_managed_block_proposal_preserves_surrounding_content(self):
        altered = AGENTS_BLOCK.replace("conservar rigor", "conservar el rigor")
        agents = self.file("AGENTS.md", "Antes\n" + altered + "\nDespués\n")
        result = initialize_project(self.root)
        self.assertEqual(agents.read_text(encoding="utf-8"), "Antes\n" + altered + "\nDespués\n")
        self.assertEqual(result["proposals"][0]["proposed_content"], "Antes\n" + AGENTS_BLOCK + "\nDespués\n")

    def test_selection_preserved_unless_explicit_and_empty_is_distinct_from_pending(self):
        initialize_project(self.root, include=["alumnado/materiales"], exclude=["alumnado/materiales/omitido.md"])
        config = load_project(self.root)
        initialize_project(self.root)
        self.assertEqual(load_project(self.root), config)
        initialize_project(self.root, include=[], exclude=[])
        self.assertTrue(load_project(self.root)["sources"]["selected"])
        self.assertEqual(check_project(self.root)["selection_status"], "none")

    def test_no_configuration_reformatting_without_a_requested_change(self):
        initialize_project(self.root)
        config = load_project(self.root)
        text = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
        (self.root / CONFIG_NAME).write_text(text, encoding="utf-8")
        initialize_project(self.root)
        self.assertEqual((self.root / CONFIG_NAME).read_text(encoding="utf-8"), text)

    def test_map_registration_preserved_and_requires_real_index(self):
        initialize_project(self.root)
        self.file("docente/mapa-docente/index.md", "# Mapa real\n")
        config = load_project(self.root)
        config["map"] = "docente/mapa-docente"
        self.save(config)
        initialize_project(self.root, include=["alumnado/materiales"])
        self.assertEqual(load_project(self.root)["map"], "docente/mapa-docente")
        (self.root / "docente/mapa-docente/index.md").unlink()
        self.assertEqual(check_project(self.root)["status"], "invalid")

    def test_missing_empty_excluded_and_inaccessible_are_different(self):
        self.file("seleccion-excluida/omitido.md")
        self.file("lectura-denegada/apunte.md")
        (self.root / "carpeta-vacia").mkdir()
        initialize_project(self.root, include=["inexistente", "carpeta-vacia", "seleccion-excluida", "lectura-denegada"],
                           exclude=["seleccion-excluida/omitido.md"])
        real_scandir = os.scandir
        def scandir(path):
            if Path(path).name == "lectura-denegada":
                raise PermissionError("Simulado")
            return real_scandir(path)
        with patch("docencia.project.os.scandir", side_effect=scandir):
            report = check_project(self.root)
        self.assertEqual([item["status"] for item in report["sources"]],
                         ["missing", "empty", "no_selected_files", "inaccessible"])
        self.assertEqual(report["status"], "incomplete")

    def test_source_selection_never_reads_contents_and_honors_exact_subtrees(self):
        included = self.file("docente/fuentes/apunte.md")
        excluded = self.file("docente/fuentes/reservado/examen.md")
        outside = self.file("archivo/viejo.md")
        initialize_project(self.root, include=["docente/fuentes"], exclude=["docente/fuentes/reservado"])
        config = load_project(self.root)
        with patch.object(Path, "read_text", side_effect=AssertionError("No leer")), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("No leer")):
            self.assertTrue(source_allowed(self.root, config, included))
            self.assertFalse(source_allowed(self.root, config, excluded))
            self.assertFalse(source_allowed(self.root, config, outside))
        self.assertEqual(check_project(self.root)["selected_files"], ["docente/fuentes/apunte.md"])

    def test_reserved_exam_can_be_selected_but_results_drafts_and_map_cannot(self):
        exam = self.file("docente/evaluaciones/examen.md")
        initialize_project(self.root, include=["docente/evaluaciones"])
        self.assertTrue(source_allowed(self.root, load_project(self.root), exam))
        for forbidden in ("docente", "docente/resultados", "docente/borradores", "docente/mapa-docente"):
            with self.subTest(forbidden=forbidden), self.assertRaises(ValueError):
                initialize_project(self.root, include=[forbidden])
        self.assertEqual(load_project(self.root)["sources"]["include"], ["docente/evaluaciones"])

    def test_alternate_map_inside_selected_tree_is_excluded(self):
        self.file("referencias/mapa/index.md")
        self.file("referencias/apunte.md")
        initialize_project(self.root, include=["referencias"])
        config = load_project(self.root)
        config["map"] = "referencias/mapa"
        self.save(config)
        self.assertEqual(check_project(self.root)["selected_files"], ["referencias/apunte.md"])

    def test_symlink_cannot_bypass_exclusion_or_escape_selection(self):
        excluded = self.file("docente/resultados/notas.csv")
        internal = self.file("archivo/no-elegido.md")
        self.symlink(self.root / "docente/fuentes/notas.csv", excluded)
        self.symlink(self.root / "docente/fuentes/otro.md", internal)
        initialize_project(self.root, include=["docente/fuentes"])
        config = load_project(self.root)
        self.assertFalse(source_allowed(self.root, config, "docente/fuentes/notas.csv"))
        self.assertFalse(source_allowed(self.root, config, "docente/fuentes/otro.md"))
        self.assertEqual(check_project(self.root)["selected_files"], [])

    def test_controlling_symlinks_rejected_before_any_mutation(self):
        external = Path(self.temporary.name) / "ajeno.md"
        external.write_text("No tocar", encoding="utf-8")
        self.symlink(self.root / "AGENTS.md", external)
        with self.assertRaises(ValueError):
            initialize_project(self.root)
        self.assertEqual(external.read_text(encoding="utf-8"), "No tocar")
        self.assertEqual([item.name for item in self.root.iterdir()], ["AGENTS.md"])

    def test_directory_symlink_rejected_before_writing_outside(self):
        external = Path(self.temporary.name) / "ajeno"
        external.mkdir()
        self.symlink(self.root / "docente", external)
        with self.assertRaises(ValueError):
            initialize_project(self.root)
        self.assertEqual(list(external.iterdir()), [])

    def test_collision_in_ancestor_fails_before_any_creation(self):
        self.file("docente", "Un archivo existente")
        before = self.snapshot()
        with self.assertRaises(ValueError):
            initialize_project(self.root)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / "alumnado").exists())

    def test_plugin_installation_cannot_become_a_course(self):
        with self.assertRaisesRegex(ValueError, "instalación"):
            initialize_project(PLUGIN_ROOT, dry_run=True)
        with self.assertRaises(ValueError):
            initialize_project(PLUGIN_ROOT / "curso-prohibido", dry_run=True)

    def test_relative_paths_and_lists_are_validated_before_creation(self):
        for value in (".", "../fuera", "/tmp/absoluta", "C:/absoluta", "carpeta\\sub", "fuentes/*"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                initialize_project(self.root, include=[value])
        with self.assertRaises(ValueError):
            initialize_project(self.root, include="fuentes")
        self.assertFalse(self.root.exists())

    def test_duplicate_json_keys_and_unsupported_versions_rejected(self):
        initialize_project(self.root)
        config = load_project(self.root)
        bad = copy.deepcopy(config)
        bad["schema_version"] = True
        self.save(bad)
        self.assertEqual(check_project(self.root)["status"], "invalid")
        (self.root / CONFIG_NAME).write_text('{"schema_version": 1, "schema_version": 2}', encoding="utf-8")
        self.assertEqual(check_project(self.root)["status"], "invalid")

    def test_find_project_prefers_nearest_and_does_not_hide_invalid_config(self):
        initialize_project(self.root)
        self.assertEqual(find_project(self.root / "alumnado/materiales"), self.root.resolve())
        file = self.file("subcurso/proyecto-docente.json", "No JSON")
        self.assertEqual(find_project(file), file.parent.resolve())
        self.assertEqual(check_project(file.parent)["status"], "invalid")

    def test_distribution_placeholders_do_not_count_as_sources(self):
        self.file("docente/fuentes/.gitkeep", "")
        self.file("docente/fuentes/.DS_Store", "Metadata")
        initialize_project(self.root, include=["docente/fuentes"])
        report = check_project(self.root)
        self.assertEqual(report["sources"][0]["status"], "empty")
        self.assertEqual(report["selected_files"], [])
        self.assertFalse(source_allowed(self.root, load_project(self.root), "docente/fuentes/.gitkeep"))

    def test_diagnostics_do_not_modify_files(self):
        self.file("docente/fuentes/útil.md")
        initialize_project(self.root, include=["docente/fuentes"])
        before = self.snapshot()
        self.assertEqual(check_project(self.root)["status"], "ok")
        self.assertEqual(self.snapshot(), before)

    def test_missing_configuration_is_reported_without_creating_it(self):
        report = check_project(self.root)
        self.assertEqual(report["status"], "incomplete")
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
