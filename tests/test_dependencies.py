"""Pruebas de reparación de artefactos generados sin releer ni mutar fuentes."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from docencia import dependencies
from docencia.catalog import read_catalog, reconcile, transaction
from docencia.organization import apply_organization, plan_organization
from docencia.project import initialize_course


class GeneratedDependenciesTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name).resolve()
        spaces = {"sources": ["Mis temarios"], "generated": ["Trabajo"], "submissions": ["Lotes"]}
        initialize_course(self.root, spaces=spaces, include=["Mis temarios"])
        self.source = self.file("Mis temarios/Tema.md", "Historia")
        self.handout = self.file("Trabajo/Unidad/guia.md", "[Tema](../../Mis%20temarios/Tema.md#uno)\n")
        self.internal = "Trabajo/Unidad/_datos_internos"
        self.activity = self.file(self.internal + "/actividad.json", json.dumps({
            "schema_version": 1, "sources": [{"path": "../../../Mis temarios/Tema.md"}],
            "files": {"statement": {"path": "../guia.md"}}}))
        self.bank = self.file(self.internal + "/metadatos.json", json.dumps({
            "schema_version": 1, "materials": {"t": {"path": "Mis temarios/Tema.md"}},
            "concepts": {"c": {"references": [{"path": "Mis temarios/Tema.md"}]}}, "questions": {}}))
        self.snapshot = self.file("Trabajo/Quiz/_datos_internos/source/metadatos.json", self.bank.read_text(encoding="utf-8"))
        self.file("Trabajo/Quiz/_datos_internos/manifest.json", "{}")
        self.graded = self.file("Lotes/grupo/respuesta.md", "Privado")
        self.catalog = self.file("Trabajo/Bancos/_datos_internos/catalogo.json", json.dumps({
            "schema_version": 1, "path_base": "project",
            "banks": [{"id": "uno", "gift": "Trabajo/Unidad/banco.gift",
                       "metadata": self.internal + "/metadatos.json"}]}))
        self.file("Trabajo/Unidad/banco.gift", "Banco")
        reconcile(self.root)
        self.initial = read_catalog(self.root)["materials"]
        self.ids = {r["path"]: mid for mid, r in self.initial.items()}
        dependencies.refresh_dependencies(self.root)

    def file(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_manual_move_then_changed_content_selective_repair(self):
        old = self.source.read_bytes()
        self.source.rename(self.source.with_name("Historia y cultura.md"))
        changes = reconcile(self.root)["moves"]
        result = dependencies.refresh_dependencies(self.root, changes)
        self.assertEqual(3, len(result["repaired"]))
        self.assertIn("Historia%20y%20cultura.md#uno", self.handout.read_text(encoding="utf-8"))
        self.assertEqual("../../../Mis temarios/Historia y cultura.md",
                         json.loads(self.activity.read_text(encoding="utf-8"))["sources"][0]["path"])
        self.assertEqual("Mis temarios/Historia y cultura.md",
                         json.loads(self.bank.read_text(encoding="utf-8"))["concepts"]["c"]["references"][0]["path"])
        self.assertEqual("Mis temarios/Tema.md",
                         json.loads(self.snapshot.read_text(encoding="utf-8"))["materials"]["t"]["path"])
        self.assertEqual("Privado", self.graded.read_text(encoding="utf-8"))
        self.assertEqual(old, self.source.with_name("Historia y cultura.md").read_bytes())
        rows = read_catalog(self.root)["materials"]
        self.assertEqual(1, rows[self.ids["Trabajo/Unidad/guia.md"]]["content_version"])
        self.assertEqual([], reconcile(self.root)["modified"])
        self.file("Mis temarios/Historia y cultura.md", "Contenido revisado")
        reconcile(self.root)
        result = dependencies.refresh_dependencies(self.root)
        self.assertEqual(3, len(result["needs_review"]))
        self.assertEqual([], result["repaired"])

    def test_move_of_generated_unit_rebases_links_and_bank_registry(self):
        mid = self.ids["Trabajo/Unidad"]
        plan = plan_organization(self.root, [{"material_id": mid, "destination": "Trabajo/2026/U"}])
        changes = apply_organization(self.root, plan["plan_id"], accepted="all")["changes"]
        report = dependencies.refresh_dependencies(self.root, changes)
        self.assertEqual("ok", report["status"])
        unit = self.root / "Trabajo/2026/U"
        self.assertIn("../../../Mis%20temarios/Tema.md", (unit / "guia.md").read_text(encoding="utf-8"))
        self.assertEqual("../guia.md", json.loads((unit / "_datos_internos/actividad.json").read_text(encoding="utf-8"))
                         ["files"]["statement"]["path"])
        bank = json.loads(self.catalog.read_text(encoding="utf-8"))["banks"][0]
        self.assertEqual("Trabajo/2026/U/banco.gift", bank["gift"])
        self.assertEqual("Trabajo/2026/U/_datos_internos/metadatos.json", bank["metadata"])
        self.assertEqual([], dependencies.refresh_dependencies(self.root, changes)["repaired"])

    def test_retry_checkpoints_before_replacing_document(self):
        self.source.rename(self.source.with_name("Nuevo.md"))
        moves = reconcile(self.root)["moves"]
        write = dependencies._write
        def interrupt(path, text):
            write(path, text)
            raise RuntimeError("simulación")
        with patch.object(dependencies, "_write", side_effect=interrupt):
            with self.assertRaises(RuntimeError):
                dependencies.refresh_dependencies(self.root, moves)
        self.assertIn("dependency_write", read_catalog(self.root))
        dependencies.recover_dependencies(self.root)
        reconcile(self.root)
        result = dependencies.refresh_dependencies(self.root)
        self.assertEqual("ok", result["status"])
        self.assertNotIn("dependency_write", read_catalog(self.root))
        self.assertIn("Nuevo.md", self.handout.read_text(encoding="utf-8"))
        self.assertEqual("Mis temarios/Nuevo.md", json.loads(self.bank.read_text(encoding="utf-8"))["materials"]["t"]["path"])

    def test_unbound_documents_with_reused_old_path_require_review(self):
        with transaction(self.root) as tx:
            tx.data.pop("derived_documents")
        self.source.rename(self.source.with_name("Nuevo.md"))
        self.file("Mis temarios/Tema.md", "Otra obra")
        changes = reconcile(self.root)["moves"]
        result = dependencies.refresh_dependencies(self.root, changes)
        self.assertTrue(result["needs_review"])
        self.assertEqual([], result["repaired"])
        self.assertIn("Tema.md", self.handout.read_text(encoding="utf-8"))
