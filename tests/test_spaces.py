import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from docencia.catalog import reconcile
from docencia.project import (CONFIG_V3, CONFIG_V4, DEFAULT_SPACES, MANAGEMENT_DIR,
                              check_project, find_project, initialize_course, initialize_project,
                              load_project, project_config_path, source_allowed)
from docencia.spaces import resolve_space


class CourseSpacesTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve() / "Curso"

    def test_defaults_and_lazy_management(self):
        preview = initialize_course(self.root, dry_run=True)
        self.assertFalse(self.root.exists())
        actual = initialize_course(self.root)
        self.assertEqual(actual["created"], preview["would_create"])
        self.assertEqual(set(x.name for x in self.root.iterdir()),
                         {"AGENTS.md", *(v[0] for v in DEFAULT_SPACES.values())})
        self.assertEqual(load_project(self.root)["spaces"], DEFAULT_SPACES)
        self.assertEqual(find_project(self.root / "Entregas"), self.root)
        self.assertIsNone(project_config_path(self.root))
        self.assertEqual(initialize_course(self.root)["created"], [])
        (self.root / "Entregas").rmdir()
        self.assertIn("Entregas", check_project(self.root)["missing_directories"])
        initialize_course(self.root, include=[])
        self.assertTrue((self.root / CONFIG_V4).exists())
        self.assertEqual(initialize_course(self.root)["updated"], [])
        self.assertEqual(check_project(self.root)["selection_status"], "none")

    def test_existing_units_are_assigned_without_reorganization(self):
        notes = self.root / "Mi estructura/Unidad 1"
        notes.mkdir(parents=True)
        source = notes / "tema.md"
        source.write_text("Apuntes", encoding="utf-8")
        proposal = initialize_course(self.root)
        self.assertEqual(proposal["status"], "pending_approval")
        self.assertEqual(proposal["proposals"][0]["entries"], ["Mi estructura"])
        self.assertEqual([p.name for p in self.root.iterdir()], ["Mi estructura"])
        roles = {"sources": ["Mi estructura", "Otra colección"], "generated": ["Producción"],
                 "submissions": ["Evaluación privada"]}
        initialize_course(self.root, spaces=roles, include=["Mi estructura/Unidad 1"])
        self.assertTrue(source_allowed(self.root, load_project(self.root), source))
        self.assertEqual(check_project(self.root)["selected_files"], ["Mi estructura/Unidad 1/tema.md"])
        with self.assertRaisesRegex(ValueError, "Elige"):
            resolve_space(self.root, "sources")
        self.assertEqual(resolve_space(self.root, "sources", "Mi estructura/Unidad 1"), notes)
        with self.assertRaises(ValueError):
            resolve_space(self.root, "generated", "Mi estructura")
        self.assertEqual(source.read_text(encoding="utf-8"), "Apuntes")
        self.assertFalse((self.root / "Material de la asignatura").exists())

    def test_notes_reuse_preserves_existing_course_selection_and_teacher_files(self):
        roles = {"sources": ["Lecturas"], "generated": ["Taller"], "submissions": ["Trabajos"]}
        initialize_course(self.root, spaces=roles, include=["Lecturas"])
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8") + "\nRegla del profesor.\n", encoding="utf-8")
        before = agents.read_bytes()
        config_before = (self.root / CONFIG_V4).read_bytes()
        notes = self.root / "Mi planificación"
        notes.mkdir()
        idea = notes / "debate.md"
        idea.write_text("Pregunta en preparación", encoding="utf-8")
        initialize_course(self.root)
        self.assertEqual((self.root / CONFIG_V4).read_bytes(), config_before)
        self.assertEqual(load_project(self.root)["spaces"], roles)
        with self.assertRaises(ValueError):
            resolve_space(self.root, "notes")
        preview = initialize_course(self.root, notes=notes.name, dry_run=True)
        self.assertEqual(preview["would_update"], [CONFIG_V4])
        self.assertEqual((self.root / CONFIG_V4).read_bytes(), config_before)
        result = initialize_course(self.root, notes=notes.name)
        config = load_project(self.root)
        self.assertEqual(config["spaces"], {**roles, "notes": [notes.name]})
        self.assertEqual(config["sources"]["include"], ["Lecturas"])
        self.assertEqual(agents.read_bytes(), before)
        proposed = result["proposals"][0]["proposed_content"]
        self.assertIn("Regla del profesor.", proposed)
        self.assertIn(notes.name, proposed)
        # Aceptación del bloque acordado en este curso de prueba.
        agents.write_text(proposed, encoding="utf-8")
        repeat = initialize_course(self.root, notes=notes.name)
        self.assertEqual((repeat["status"], repeat["created"], repeat["updated"]), ("ok", [], []))
        self.assertEqual(resolve_space(self.root, "notes"), notes)
        self.assertEqual(idea.read_text(encoding="utf-8"), "Pregunta en preparación")
        self.assertEqual(initialize_course(self.root, spaces=roles)["config"]["spaces"], config["spaces"])

    def test_notes_must_be_independent_and_cannot_be_selected_as_corpus(self):
        for folder in ("Material de la asignatura/Notas", "Material generado por IA", "entregas", "Gestión del proyecto"):
            with self.subTest(folder=folder), self.assertRaises(ValueError):
                initialize_course(self.root, notes=folder)
            self.assertFalse(self.root.exists())
        with self.assertRaises(ValueError):
            initialize_course(self.root, notes="Cuaderno", include=["Cuaderno"])
        self.assertFalse(self.root.exists())

    def test_only_the_individually_incorporated_note_enters_the_catalog(self):
        from docencia.catalog import read_catalog
        roles = {**DEFAULT_SPACES, "notes": ["Ideas", "Planificación"]}
        source = "Material de la asignatura"
        initialize_course(self.root, spaces=roles, include=[source])
        idea = self.root / "Ideas/actividad.md"
        idea.write_text("Actividad sintética aprobada", encoding="utf-8")
        private = self.root / "Planificación/otra-idea.md"
        private.write_text("Idea reservada", encoding="utf-8")
        with self.assertRaises(ValueError):
            reconcile(self.root, scope="Ideas")
        reconcile(self.root)
        self.assertFalse(source_allowed(self.root, load_project(self.root), idea))
        self.assertEqual(check_project(self.root)["selected_files"], [])
        self.assertFalse(any("Ideas" in r["path"] or "Planificación" in r["path"]
                             for r in read_catalog(self.root)["materials"].values()))
        # El docente elige esta nota concreta y la incorpora a una raíz seleccionada.
        idea.rename(self.root / source / idea.name)
        reconcile(self.root)
        self.assertEqual(check_project(self.root)["selected_files"], [f"{source}/{idea.name}"])
        self.assertFalse(source_allowed(self.root, load_project(self.root), private))
        self.assertTrue(private.is_file())

    def test_reject_overlapping_reserved_and_unsafe_spaces_before_writing(self):
        for invalid in ("Material de la asignatura/Privado", "Entregas", "Entregas/Estudiantes",
                        "Gestión del proyecto", "../Externo", ".agents", "Carpeta/_datos_internos"):
            roles = copy.deepcopy(DEFAULT_SPACES)
            roles["generated"] = [invalid]
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                initialize_course(self.root, spaces=roles)
            self.assertFalse(self.root.exists())

    def test_corpus_never_follows_a_private_link_and_respects_exclusions(self):
        sources = "Material de la asignatura"
        config = initialize_course(self.root, include=[sources], exclude=[sources + "/Privado"])["config"]
        private = self.root / "Entregas/calificaciones.csv"
        private.write_text("synthetic", encoding="utf-8")
        alias = self.root / sources / "datos.csv"
        try:
            alias.symlink_to(private)
        except OSError:
            self.skipTest("Enlaces no disponibles")
        self.assertFalse(source_allowed(self.root, config, alias))
        self.assertFalse(source_allowed(self.root, config, private))
        self.assertFalse(source_allowed(self.root, config, sources + "/privado/tarea"))
        self.assertFalse(source_allowed(self.root, config, sources + "/_datos_internos/clave"))
        self.assertEqual(check_project(self.root)["selected_files"], [])

    def test_hard_link_to_submissions_is_not_a_source(self):
        sources = "Material de la asignatura"
        config = initialize_course(self.root, include=[sources])["config"]
        private = self.root / "Entregas/notas.csv"
        private.write_text("synthetic", encoding="utf-8")
        alias = self.root / sources / "aparentemente-docente.csv"
        try:
            alias.hardlink_to(private)
        except OSError:
            self.skipTest("Enlaces duros no disponibles")
        self.assertFalse(source_allowed(self.root, config, alias))
        self.assertEqual(check_project(self.root)["selected_files"], [])

    def test_ai_draft_cannot_enter_corpus_by_manual_move(self):
        sources = "Material de la asignatura"
        config = initialize_course(self.root, include=[sources])["config"]
        draft = self.root / "Material generado por IA/borrador.md"
        draft.write_text("Borrador sin consolidación", encoding="utf-8")
        reconcile(self.root)
        moved = self.root / sources / draft.name
        draft.rename(moved)
        # Antes y después de la reconciliación se conserva la procedencia.
        self.assertFalse(source_allowed(self.root, config, moved))
        reconcile(self.root)
        self.assertFalse(source_allowed(self.root, config, moved))
        original = self.root / sources / "otra.md"
        original.write_text("Aportado", encoding="utf-8")
        self.assertEqual(check_project(self.root)["selected_files"], [sources + "/otra.md"])

    def test_selection_follows_renamed_units_and_excludes_moved_children(self):
        base = "Material de la asignatura"
        unit = self.root / base / "Unidad"
        private = unit / "Reservado"
        private.mkdir(parents=True)
        (unit / "tema.md").write_text("Lectura", encoding="utf-8")
        marked = private / "clave.md"
        marked.write_text("Reservado", encoding="utf-8")
        config = initialize_course(self.root, include=[base + "/Unidad"],
                                   exclude=[base + "/Unidad/Reservado"])["config"]
        current = unit.with_name("Tema primero")
        unit.rename(current)
        (current / "Reservado").rename(current / "Originales")
        secret = current / "solucion-fuera.md"
        (current / "Originales/clave.md").rename(secret)
        self.assertTrue(source_allowed(self.root, config, current / "tema.md"))
        self.assertFalse(source_allowed(self.root, config, secret))
        self.assertEqual(check_project(self.root)["selected_files"], [base + "/Tema primero/tema.md"])
        from docencia.spaces import corpus_policy
        with patch("os.scandir", wraps=__import__("os").scandir) as scans, patch("pathlib.Path.open",
                side_effect=AssertionError("Se intentó abrir contenido")):
            policy = corpus_policy(self.root, config)
        self.assertFalse(any("Entregas" in str(arg.args) for arg in scans.call_args_list))
        self.assertIn(base + "/Tema primero/Originales", policy["exclude"])
        self.assertIn(base + "/Tema primero/solucion-fuera.md", policy["exclude"])
        self.assertEqual(policy["review"], [])
        from docencia.catalog import _digest, read_catalog
        with patch("docencia.catalog._digest", wraps=_digest) as digests:
            reconcile(self.root)
        self.assertNotIn(secret, [call.args[0] for call in digests.call_args_list])
        inventory = read_catalog(self.root)["materials"]
        paths = [row["path"] for row in inventory.values()]
        self.assertNotIn(secret.relative_to(self.root).as_posix(), paths)

    def test_disappeared_exclusion_fails_closed_until_restored_or_confirmed(self):
        base = "Material de la asignatura"
        folder = self.root / base
        folder.mkdir(parents=True)
        allow = folder / "tema.md"
        allow.write_text("original", encoding="utf-8")
        protected = folder / "reservado.md"
        protected.write_text("reservado", encoding="utf-8")
        config = initialize_course(self.root, include=[base], exclude=[base + "/reservado.md"])["config"]
        backup = self.root.parent / "apartado.md"
        protected.rename(backup)
        self.assertFalse(source_allowed(self.root, config, allow))
        self.assertEqual(check_project(self.root)["selected_files"], [])
        backup.rename(protected)
        self.assertTrue(source_allowed(self.root, config, allow))
        self.assertFalse(source_allowed(self.root, config, protected))
        protected.rename(backup)
        cleared = initialize_course(self.root, exclude=[])["config"]
        self.assertTrue(source_allowed(self.root, cleared, allow))

    def test_future_exclusion_does_not_block_unrelated_sources(self):
        from docencia.spaces import corpus_policy
        roles = {"sources": ["Originales"], "generated": ["Salidas"], "submissions": ["Privado"]}
        config = initialize_course(self.root, spaces=roles, include=["Originales"],
                                   exclude=["Originales/Privado"])["config"]
        future = self.root / "Originales/Privado"
        source = self.root / "Originales/teoria.md"
        source.write_text("Material docente", encoding="utf-8")
        self.assertEqual(corpus_policy(self.root, config, refresh=True)["review"], [])
        self.assertTrue(source_allowed(self.root, load_project(self.root), source))
        future.mkdir()
        reconcile(self.root)
        future.rename(self.root.parent / "desaparecido")
        self.assertFalse(source_allowed(self.root, load_project(self.root), source))

    def test_refresh_tracks_later_additions_without_opening_excluded_files(self):
        from docencia.spaces import corpus_policy
        base = "Material de la asignatura"
        folder = self.root / base / "Privado"
        folder.mkdir(parents=True)
        config = initialize_course(self.root, include=[base], exclude=[base + "/Privado"])["config"]
        late = folder / "clave-nueva.md"
        late.write_text("clave", encoding="utf-8")
        corpus_policy(self.root, config, refresh=True)
        moved = late.rename(folder.parent / "cambio.md")
        self.assertFalse(source_allowed(self.root, load_project(self.root), moved))

    def test_adoption_is_explicit_preserves_contract_and_queries_conflicts(self):
        previous = initialize_project(self.root, include=["fuentes/teoria"])["config"]
        legacy = (self.root / CONFIG_V3).read_bytes()
        agents = (self.root / "AGENTS.md").read_bytes()
        proposal = initialize_course(self.root)
        self.assertEqual(proposal["status"], "pending_approval")
        self.assertFalse((self.root / MANAGEMENT_DIR).exists())
        self.assertEqual(load_project(self.root), previous)
        adopted = initialize_course(self.root, adopt_v3=True)
        self.assertTrue(adopted["proposals"])
        self.assertEqual(load_project(self.root)["structure"], "curso-v4")
        self.assertEqual(load_project(self.root)["sources"], previous["sources"])
        self.assertEqual(load_project(self.root)["spaces"]["sources"], ["fuentes"])
        self.assertEqual((self.root / CONFIG_V3).read_bytes(), legacy)
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), agents)
        self.assertEqual(initialize_course(self.root)["created"], [])

    def test_conflicting_active_configs_are_reported(self):
        initialize_project(self.root)
        before = load_project(self.root)
        other = self.root / CONFIG_V4
        other.parent.mkdir()
        other.write_text(json.dumps(before), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Dos configuraciones"):
            load_project(self.root)
