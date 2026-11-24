"""Casos de identidad y clasificación de cursos v4; solo contenido sintético."""

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import shutil
import unittest
from unittest.mock import patch

from docencia import catalog as cat
from docencia.project import initialize_course


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.source = "Material de la asignatura"
        self.ai = "Material generado por IA"
        initialize_course(self.root)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def rows(self):
        return {r["path"]: r for r in cat.read_catalog(self.root)["materials"].values()}

    def test_move_and_content_change_have_distinct_effects(self):
        source = self.write(f"{self.source}/Unidad/campo.md", "# Práctica de laboratorio\n12 registros")
        rel = source.relative_to(self.root).as_posix()
        cat.reconcile(self.root)
        old = self.rows()[rel]
        self.assertEqual(old["classification"]["primary"], "Práctica")
        self.assertEqual(self.rows()[f"{self.source}/Unidad"]["classification"]["primary"], "Práctica")
        (self.root / self.source / "Unidad").rename(self.root / self.source / "Tema")
        newrel = f"{self.source}/Tema/campo.md"
        with patch.object(cat, "_digest", side_effect=AssertionError("Relectura de archivo intacto")):
            report = cat.reconcile(self.root)
            self.assertEqual({m["material_id"] for m in report["moves"]},
                             {old["material_id"], old["physical_parent_id"]})
            self.assertEqual(report["revision"], cat.reconcile(self.root)["revision"])
        row = self.rows()[newrel]
        for field in ("material_id", "logical_parent_id", "classification", "content_version"):
            self.assertEqual(old[field], row[field])
        self.write(newrel, "# Práctica de laboratorio\n13 registros modificados")
        self.assertEqual(cat.reconcile(self.root, scope=newrel)["modified"], [old["material_id"]])
        self.assertEqual(self.rows()[newrel]["content_version"], 2)
        (self.root / newrel).unlink()
        self.assertIn("missing", {p["reason"] for p in cat.reconcile(self.root)["pending"]})
        self.assertEqual(self.rows()[newrel]["presence"], "missing")

    def test_virtual_unit_confirmed_inheritance_and_mixed_folder(self):
        name = f"{self.source}/Tema"
        self.write(name + "/a.md", "# Fundamentos teóricos")
        self.write(name + "/b.md", "# Estudio de caso")
        self.write(name + "/c.txt", "péndulo")
        cat.reconcile(self.root)
        rows = self.rows()
        self.assertEqual(rows[name]["classification"]["primary"], None)
        group = cat.create_group(self.root, "Laboratorio")
        gid = group["material_id"]
        fid = rows[name + "/c.txt"]["material_id"]
        cat.classify(self.root, gid, primary="Práctica", evidence="Confirmación del profesor")
        cat.regroup(self.root, fid, gid)
        inherited = self.rows()[name + "/c.txt"]
        self.assertEqual(inherited["classification"]["mode"], "inherited")
        self.assertEqual(inherited["physical_parent_id"], rows[name]["material_id"])
        cat.classify(self.root, fid, primary="Recursos", secondary=["Práctica"])
        with self.assertRaises(ValueError):
            cat.classify(self.root, fid, primary="Organización", confirmed=False, evidence="Otros recursos")
        self.assertEqual(self.rows()[name + "/c.txt"]["classification"]["primary"], "Recursos")
        with self.assertRaises(ValueError):
            cat.regroup(self.root, gid, gid)

    def test_ambiguous_hash_resolution_does_not_merge_identical_copies(self):
        path = self.write(f"{self.source}/uno.md", "Misma información")
        cat.reconcile(self.root)
        old = self.rows()[f"{self.source}/uno.md"]["material_id"]
        a, b = path.with_name("a.md"), path.with_name("b.md")
        shutil.copy2(path, a)
        shutil.copy2(path, b)
        path.unlink()
        result = cat.reconcile(self.root)
        self.assertEqual(len([p for p in result["pending"] if p["reason"] == "identity"]), 2)
        row = cat.resolve_identity(self.root, f"{self.source}/a.md", material_id=old)
        self.assertEqual(row["material_id"], old)
        cat.reconcile(self.root)
        self.assertNotEqual(self.rows()[f"{self.source}/b.md"]["material_id"], old)

    def test_sensitive_and_operational_files_are_not_scanned(self):
        self.write("Entregas/privado.csv", "Estudiante")
        self.write(self.source + "/unidad/_datos_internos/metadatos.json", "{}")
        resource = self.write(self.source + "/unidad/datos.json", "{}")
        try:
            (resource.parent / "enlace").symlink_to(self.root / "Entregas", target_is_directory=True)
        except OSError:
            pass
        cat.reconcile(self.root)
        paths = self.rows()
        self.assertIn(self.source + "/unidad/datos.json", paths)
        self.assertFalse(any("Entregas" in p or "_datos_internos" in p or "enlace" in p for p in paths))
        with self.assertRaises(ValueError):
            cat.reconcile(self.root, scope="Entregas")

    def test_scope_registers_parent_units_without_scanning_siblings(self):
        self.write(self.source + "/Tema/Unidad/texto.md", "# Fundamentos teóricos")
        self.write(self.source + "/Tema/Aparte/privado.md", "Otra unidad")
        scope = self.source + "/Tema/Unidad/texto.md"
        with patch.object(cat, "_digest", wraps=cat._digest) as digest:
            cat.reconcile(self.root, scope=scope)
        self.assertEqual(digest.call_count, 1)
        rows = self.rows()
        self.assertEqual(rows[scope]["logical_parent_id"], rows[self.source + "/Tema/Unidad"]["material_id"])
        self.assertNotIn(self.source + "/Tema/Aparte", rows)

    def test_copy_and_remove_folder_preserves_unit_by_member_identities(self):
        unit = self.source + "/Unidad"
        self.write(unit + "/a.md", "Materia A")
        self.write(unit + "/sub/b.md", "Materia B")
        cat.reconcile(self.root)
        original = self.rows()
        dest = self.source + "/Reorganizada"
        shutil.copytree(self.root / unit, self.root / dest)
        shutil.rmtree(self.root / unit)
        result = cat.reconcile(self.root)
        self.assertEqual(result["created"], [])
        self.assertEqual(result["modified"], [])
        self.assertEqual({m["material_id"] for m in result["moves"]},
                         {r["material_id"] for p, r in original.items() if p.startswith(unit)})

    def test_rejects_hardlink_from_submissions_before_content_read(self):
        private = self.write("Entregas/respuesta.txt", "Entrega sintética")
        alias = self.root / self.source / "alias.txt"
        try:
            os.link(private, alias)
        except OSError as exc:
            self.skipTest(str(exc))
        with patch.object(cat, "_digest", side_effect=AssertionError("Se leyó un alias")):
            report = cat.reconcile(self.root)
        self.assertFalse(any(r["kind"] == "file" for r in self.rows().values()))
        self.assertIn("inaccessible", {r["reason"] for r in report["pending"]})

    def test_reads_noops_and_incident_history(self):
        directory = self.root / cat.MANAGEMENT
        self.assertEqual(cat.read_catalog(self.root)["revision"], 0)
        self.assertFalse(directory.exists())
        source = self.write(self.source + "/leer.txt", "Recurso")
        cat.reconcile(self.root)
        record = self.rows()[self.source + "/leer.txt"]
        cat.classify(self.root, record["material_id"], primary="Recursos", evidence="Confirmada por el docente")
        source.rename(source.with_suffix(".md"))
        cat.reconcile(self.root)
        source.with_suffix(".md").unlink()
        cat.reconcile(self.root)
        history = directory / cat.HISTORY
        before = history.read_bytes()
        revision = cat.read_catalog(self.root)["revision"]
        self.assertEqual(revision, cat.reconcile(self.root)["revision"])
        with cat.transaction(self.root):
            pass
        self.assertEqual(before, history.read_bytes())
        events = [op for line in before.splitlines() for op in json.loads(line)["operations"]]
        self.assertTrue(any(e["kind"] == "classification" for e in events))
        self.assertTrue(any(e.get("moves") and e["moves"][0]["material_id"] == record["material_id"] for e in events))
        self.assertTrue(any(e.get("incidents", {}).get(self.source + "/leer.md") for e in events))

    def test_recover_commit_after_intent_and_reject_second_writer(self):
        with cat.transaction(self.root) as tx:
            with self.assertRaises(ValueError):
                with cat.transaction(self.root):
                    self.fail("Se admitió un segundo escritor")
        with patch.object(cat, "_recover", wraps=cat._recover) as recover:
            recover.side_effect = [None, RuntimeError("interrupción")]
            with self.assertRaises(RuntimeError):
                cat.create_group(self.root, "Grupos")
        snapshot = cat.read_catalog(self.root)
        self.assertEqual([r["title"] for r in snapshot["materials"].values()], ["Grupos"])
        history = self.root / cat.MANAGEMENT / cat.HISTORY
        lines = [json.loads(x) for x in history.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r["revision"] for r in lines], [1])
        self.assertEqual(snapshot, cat.read_catalog(self.root))
