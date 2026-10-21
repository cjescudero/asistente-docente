"""Proyectos sintéticos: conservación, selección y límites de lectura/escritura."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from docencia.project import (
    AGENTS_BLOCK, AGENTS_BLOCK_V1, CONFIG_NAME, LEEME_CONTENT, LEEME_CONTENT_V1,
    MATERIAL_RECORD_NAME, MATERIAL_TYPES, PLUGIN_ROOT, PROJECT_DIRECTORIES, PROJECT_DIRECTORIES_V1,
    check_project, find_project, initialize_project, load_project, source_allowed, validate_material_record,
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
            "schema_version": 1, "structure": "curso-v2",
            "sources": {"selected": False, "include": [], "exclude": []}, "map": None})
        for relative in PROJECT_DIRECTORIES:
            self.assertTrue((self.root / relative).is_dir())
        self.assertEqual(list((self.root / "mapa-docente").iterdir()), [])
        self.assertIn("`espanol-conciso-redaccion`", (self.root / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(check_project(self.root)["selection_status"], "pending")

    def test_second_initialization_is_byte_and_timestamp_identical(self):
        self.file("fuentes/teoria/apuntes.md")
        initialize_project(self.root, include=["fuentes/teoria"])
        before = self.snapshot()
        result = initialize_project(self.root)
        self.assertEqual(result["created"], [])
        self.assertEqual(result["updated"], [])
        self.assertEqual(result["proposals"], [])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(check_project(self.root)["status"], "ok")

    def test_previous_course_adds_submissions_without_rewriting_or_selecting_them(self):
        self.file(CONFIG_NAME, json.dumps({"schema_version": 1, "structure": "curso-v1",
            "sources": {"selected": True, "include": ["alumnado/materiales"], "exclude": []}, "map": None}))
        initialize_project(self.root)
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
        result = initialize_project(self.root, include=["fuentes/teoria"], dry_run=True)
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
        self.assertTrue((self.root / "creados/actividades").is_dir())

    def test_existing_managed_block_proposal_preserves_surrounding_content(self):
        altered = AGENTS_BLOCK.replace("conservar rigor", "conservar el rigor")
        agents = self.file("AGENTS.md", "Antes\n" + altered + "\nDespués\n")
        result = initialize_project(self.root)
        self.assertEqual(agents.read_text(encoding="utf-8"), "Antes\n" + altered + "\nDespués\n")
        self.assertEqual(result["proposals"][0]["proposed_content"], "Antes\n" + AGENTS_BLOCK + "\nDespués\n")

    def test_selection_preserved_unless_explicit_and_empty_is_distinct_from_pending(self):
        initialize_project(self.root, include=["fuentes/teoria"], exclude=["fuentes/teoria/omitido.md"])
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
        self.file("mapa-docente/index.md", "# Mapa real\n")
        config = load_project(self.root)
        config["map"] = "mapa-docente"
        self.save(config)
        initialize_project(self.root, include=["fuentes/teoria"])
        self.assertEqual(load_project(self.root)["map"], "mapa-docente")
        (self.root / "mapa-docente/index.md").unlink()
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
        included = self.file("fuentes/teoria/apunte.md")
        excluded = self.file("fuentes/teoria/reservado/examen.md")
        outside = self.file("archivo/viejo.md")
        initialize_project(self.root, include=["fuentes/teoria"], exclude=["fuentes/teoria/reservado"])
        config = load_project(self.root)
        with patch.object(Path, "read_text", side_effect=AssertionError("No leer")), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("No leer")):
            self.assertTrue(source_allowed(self.root, config, included))
            self.assertFalse(source_allowed(self.root, config, excluded))
            self.assertFalse(source_allowed(self.root, config, outside))
        self.assertEqual(check_project(self.root)["selected_files"], ["fuentes/teoria/apunte.md"])

    def test_reserved_exam_can_be_selected_but_results_drafts_and_map_cannot(self):
        exam = self.file("fuentes/evaluaciones/examen.md")
        initialize_project(self.root, include=["fuentes/evaluaciones"])
        self.assertTrue(source_allowed(self.root, load_project(self.root), exam))
        for forbidden in ("docente", "resultados", "docente/borradores", "mapa-docente"):
            with self.subTest(forbidden=forbidden), self.assertRaises(ValueError):
                initialize_project(self.root, include=[forbidden])
        self.assertEqual(load_project(self.root)["sources"]["include"], ["fuentes/evaluaciones"])

    def test_alternate_map_inside_selected_tree_is_excluded(self):
        self.file("referencias/mapa/index.md")
        self.file("referencias/apunte.md")
        initialize_project(self.root, include=["referencias"])
        config = load_project(self.root)
        config["map"] = "referencias/mapa"
        self.save(config)
        self.assertEqual(check_project(self.root)["selected_files"], ["referencias/apunte.md"])

    def test_symlink_cannot_bypass_exclusion_or_escape_selection(self):
        excluded = self.file("resultados/notas.csv")
        internal = self.file("archivo/no-elegido.md")
        self.symlink(self.root / "fuentes/teoria/notas.csv", excluded)
        self.symlink(self.root / "fuentes/teoria/otro.md", internal)
        initialize_project(self.root, include=["fuentes/teoria"])
        config = load_project(self.root)
        self.assertFalse(source_allowed(self.root, config, "fuentes/teoria/notas.csv"))
        self.assertFalse(source_allowed(self.root, config, "fuentes/teoria/otro.md"))
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
        self.symlink(self.root / "fuentes", external)
        with self.assertRaises(ValueError):
            initialize_project(self.root)
        self.assertEqual(list(external.iterdir()), [])

    def test_collision_in_ancestor_fails_before_any_creation(self):
        self.file("fuentes", "Un archivo existente")
        before = self.snapshot()
        with self.assertRaises(ValueError):
            initialize_project(self.root)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / "creados").exists())

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
        self.assertEqual(find_project(self.root / "fuentes/teoria"), self.root.resolve())
        file = self.file("subcurso/proyecto-docente.json", "No JSON")
        self.assertEqual(find_project(file), file.parent.resolve())
        self.assertEqual(check_project(file.parent)["status"], "invalid")

    def test_distribution_placeholders_do_not_count_as_sources(self):
        self.file("fuentes/teoria/.gitkeep", "")
        self.file("fuentes/teoria/.DS_Store", "Metadata")
        initialize_project(self.root, include=["fuentes/teoria"])
        report = check_project(self.root)
        self.assertEqual(report["sources"][0]["status"], "empty")
        self.assertEqual(report["selected_files"], [])
        self.assertFalse(source_allowed(self.root, load_project(self.root), "fuentes/teoria/.gitkeep"))

    def test_diagnostics_do_not_modify_files(self):
        self.file("fuentes/teoria/útil.md")
        initialize_project(self.root, include=["fuentes/teoria"])
        before = self.snapshot()
        self.assertEqual(check_project(self.root)["status"], "ok")
        self.assertEqual(self.snapshot(), before)

    def test_missing_configuration_is_reported_without_creating_it(self):
        report = check_project(self.root)
        self.assertEqual(report["status"], "incomplete")
        self.assertFalse(self.root.exists())

    def record(self, folder, status="revisado", **overrides):
        data = {"schema_version": 1, "id": "actividad-sintetica", "type": "actividad", "status": status}
        data.update(overrides)
        return self.file(f"{folder}/{MATERIAL_RECORD_NAME}", json.dumps(data, ensure_ascii=False))

    def test_legacy_initialization_keeps_layout_config_and_instructions(self):
        config = {"schema_version": 1, "structure": "curso-v1",
                  "sources": {"selected": True, "include": ["docente/fuentes"], "exclude": []}, "map": None}
        self.file(CONFIG_NAME, json.dumps(config))
        self.file("AGENTS.md", "# Curso previo\n\n" + AGENTS_BLOCK_V1 + "\n")
        self.file("LEEME.md", LEEME_CONTENT_V1)
        self.file("docente/fuentes/teoria.md")
        initialize_project(self.root)
        before = self.snapshot()
        report = initialize_project(self.root)
        self.assertEqual(report["proposals"], [])
        self.assertEqual(report["created"], [])
        self.assertEqual(load_project(self.root), config)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(check_project(self.root)["status"], "ok")
        self.assertFalse((self.root / "creados").exists())
        for folder in PROJECT_DIRECTORIES_V1:
            self.assertTrue((self.root / folder).is_dir())

    def test_new_structure_does_not_create_a_catch_all_drafts_or_audience_root(self):
        initialize_project(self.root, include=[])
        self.assertFalse((self.root / "docente").exists())
        self.assertFalse((self.root / "alumnado").exists())
        self.assertFalse((self.root / "borradores").exists())
        self.assertEqual(list((self.root / "mapa-docente").iterdir()), [])
        self.assertEqual(list((self.root / "resultados").iterdir()), [])

    def test_selected_created_files_require_reviewed_record_without_reading_content(self):
        folder = "creados/actividades/comentario"
        statement = self.file(folder + "/alumnado/enunciado.md")
        initialize_project(self.root, include=[folder + "/alumnado"])
        config = load_project(self.root)
        self.assertFalse(source_allowed(self.root, config, statement))
        for status in ("borrador", "revisado", "listo-para-entregar"):
            self.record(folder, status=status)
            real_read = Path.read_text
            def guarded(path, *args, **kwargs):
                if path == statement:
                    raise AssertionError("La comprobación no debe leer el documento")
                return real_read(path, *args, **kwargs)
            with self.subTest(status=status), patch.object(Path, "read_text", guarded):
                self.assertEqual(source_allowed(self.root, config, statement), status != "borrador")
        self.assertEqual(check_project(self.root)["selected_files"], [folder + "/alumnado/enunciado.md"])
        self.assertTrue(statement.exists())

    def test_reviewed_record_never_selects_a_created_material_implicitly(self):
        folder = "creados/actividades/comentario"
        statement = self.file(folder + "/alumnado/enunciado.md")
        self.record(folder)
        initialize_project(self.root, include=["fuentes/teoria"])
        self.assertFalse(source_allowed(self.root, load_project(self.root), statement))
        self.assertNotIn(folder + "/alumnado/enunciado.md", check_project(self.root)["selected_files"])

    def test_category_selection_descends_without_admitting_drafts_unknown_or_control_records(self):
        for name in ("listo", "borrador", "sin-registro"):
            self.file(f"creados/actividades/{name}/alumnado/enunciado.md")
        self.record("creados/actividades/listo")
        self.record("creados/actividades/borrador", status="borrador")
        initialize_project(self.root, include=["creados/actividades"])
        self.assertEqual(check_project(self.root)["selected_files"],
                         ["creados/actividades/listo/alumnado/enunciado.md"])

    def test_nearest_invalid_or_draft_record_cannot_inherit_reviewed_parent(self):
        folder = "creados/actividades/comentario"
        statement = self.file(folder + "/anexo/enunciado.md")
        self.record(folder)
        initialize_project(self.root, include=[folder])
        config = load_project(self.root)
        self.assertTrue(source_allowed(self.root, config, statement))
        record = self.record(folder + "/anexo", status="borrador")
        self.assertFalse(source_allowed(self.root, config, statement))
        record.write_text("{invalid", encoding="utf-8")
        self.assertFalse(source_allowed(self.root, config, statement))

    def test_global_or_category_record_does_not_accredit_unregistered_outputs(self):
        statement = self.file("creados/actividades/comentario/alumnado/enunciado.md")
        initialize_project(self.root, include=["creados/actividades"])
        config = load_project(self.root)
        for folder in ("creados", "creados/actividades"):
            self.record(folder)
            self.assertFalse(source_allowed(self.root, config, statement))
        self.assertEqual(check_project(self.root)["selected_files"], [])

    def test_excluded_material_and_record_are_not_read_or_admitted(self):
        folder = "creados/actividades/comentario"
        statement = self.file(folder + "/alumnado/enunciado.md")
        record = self.record(folder)
        initialize_project(self.root, include=[folder], exclude=[folder + "/alumnado"])
        config = load_project(self.root)
        with patch.object(Path, "read_text", side_effect=AssertionError("No leer excluidos")):
            self.assertFalse(source_allowed(self.root, config, statement))
        initialize_project(self.root, exclude=[folder + "/" + MATERIAL_RECORD_NAME])
        config = load_project(self.root)
        with patch.object(Path, "read_text", side_effect=AssertionError("No leer registro excluido")):
            self.assertFalse(source_allowed(self.root, config, statement))
        self.assertTrue(record.exists())

    def test_symbolic_material_record_cannot_grant_corpus_access(self):
        folder = "creados/actividades/comentario"
        statement = self.file(folder + "/alumnado/enunciado.md")
        other = self.record("creados/actividades/otro")
        self.symlink(self.root / folder / MATERIAL_RECORD_NAME, other)
        initialize_project(self.root, include=[folder])
        self.assertFalse(source_allowed(self.root, load_project(self.root), statement))

    def test_material_record_validation_covers_types_and_rejects_ambiguous_states(self):
        folder = "creados/materiales/apuntes"
        for material_type in MATERIAL_TYPES:
            path = self.record(folder, type=material_type)
            self.assertEqual(validate_material_record(path)["type"], material_type)
        for changes in ({"schema_version": True}, {"id": " "}, {"type": "otro"},
                        {"type": []}, {"status": "aprobado"}, {"status": False}):
            with self.subTest(changes=changes):
                path = self.record(folder, **changes)
                with self.assertRaises(ValueError):
                    validate_material_record(path)
        path.write_text('{"schema_version":1,"status":"revisado","status":"borrador"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicada"):
            validate_material_record(path)

    def test_result_inputs_and_correction_outputs_cannot_enter_corpus(self):
        received = self.file("resultados/actividad/ordinaria/recibidos/notas.csv")
        corrected = self.file("resultados/actividad/ordinaria/correccion/notas.csv")
        initialize_project(self.root, include=["fuentes/teoria"])
        config = load_project(self.root)
        for path in (received, corrected):
            self.assertFalse(source_allowed(self.root, config, path))
        with self.assertRaisesRegex(ValueError, "permanentemente"):
            initialize_project(self.root, include=["resultados/actividad/ordinaria/recibidos"])


if __name__ == "__main__":
    unittest.main()
