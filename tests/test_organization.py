"""Movimientos aprobados con cursos sintéticos. Se comprueban archivos y catálogo."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from docencia import organization
from docencia.catalog import CATEGORIES, read_catalog, reconcile
from docencia.project import initialize_course


class OrganizationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.sources = "Mis unidades"
        self.generated = "Propuestas"
        self.submissions = "Subidas"
        spaces = {"sources": [self.sources], "generated": [self.generated],
                  "submissions": [self.submissions]}
        initialize_course(self.root, spaces=spaces, include=[self.sources],
                          exclude=[f"{self.sources}/Privado"])

    def file(self, path, text="Tema"):
        target = self.root / path
        target.parent.mkdir(exist_ok=True, parents=True)
        target.write_text(text, encoding="utf-8")
        return target

    def ids(self):
        reconcile(self.root)
        return {row["path"]: key for key, row in read_catalog(self.root)["materials"].items()}

    def proposal(self, *pairs, mode="moves"):
        return organization.plan_organization(self.root, [
            {"material_id": key, "destination": target} for key, target in pairs], mode=mode)

    def apply(self, plan, accepted="all", **kwargs):
        return organization.apply_organization(self.root, plan["plan_id"], accepted=accepted, **kwargs)

    def test_partial_authorization_with_exception_and_later_collision(self):
        unit = self.sources + "/Medievo"
        a = unit + "/Carta.md"
        b = self.sources + "/Cronica.md"
        self.file(a)
        self.file(b)
        ids = self.ids()
        sa, sb = self.sources + "/Textos/Carta.md", self.sources + "/Primarias/Cronica.md"
        plan = self.proposal((ids[a], sa), (ids[b], sb))
        self.assertEqual(2, plan["summary"]["files"])
        self.assertFalse((self.root / sa).exists())
        with self.assertRaises(ValueError):
            organization.apply_organization(self.root, plan["plan_id"])
        self.assertEqual([], self.apply(plan, [])["applied"])
        self.assertEqual(["op-1"], self.apply(plan, ["op-1"])["applied"])
        self.assertTrue((self.root / b).exists())
        self.file(sb, "Imprescindible")
        self.assertEqual("needs_review", self.apply(plan, ["op-2"])["status"])
        self.assertEqual("Imprescindible", (self.root / sb).read_text(encoding="utf-8"))
        new_b = self.sources + "/Otros/Cronica.md"
        self.assertEqual(["op-2"], self.apply(plan, ["op-2"], changes={"op-2": new_b})["applied"])
        rows = read_catalog(self.root)["materials"]
        self.assertEqual(rows[ids[a]]["logical_parent_id"], ids[unit])
        self.assertNotEqual(rows[ids[a]]["physical_parent_id"], ids[unit])
        self.assertEqual(new_b, rows[ids[b]]["path"])
        self.assertEqual(["op-1", "op-2"], self.apply(plan)["applied"])


    def test_destination_race_never_replaces_file_and_plan_stays_negotiable(self):
        old = self.sources + "/Carta.md"
        new = self.sources + "/Copia.md"
        self.file(old)
        ids = self.ids()
        plan = self.proposal((ids[old], new))
        rename = organization._rename_new
        def occupy(source, destination):
            destination.write_text("Ajeno")
            rename(source, destination)
        with mock.patch.object(organization, "_rename_new", side_effect=occupy):
            self.assertEqual("needs_review", self.apply(plan)["status"])
        self.assertEqual("Ajeno", (self.root / new).read_text(encoding="utf-8"))
        self.assertTrue((self.root / old).is_file())
        self.assertEqual("ok", self.apply(plan, changes={"op-1": self.sources + "/Alternativa.md"})["status"])

    def test_stale_version_new_child_and_scope_protections(self):
        unit = self.sources + "/Seminario"
        a = unit + "/Lectura.md"
        self.file(a)
        ids = self.ids()
        same_role = self.sources + "/Lecturas"
        plan = self.proposal((ids[unit], same_role))
        self.file(a, "Revisión")
        self.assertEqual("needs_review", self.apply(plan)["status"])
        self.assertTrue((self.root / a).exists())
        with self.assertRaisesRegex(ValueError, "Reconciliar"):
            self.proposal((ids[unit], same_role))
        self.ids()
        self.file(unit + "/Nuevo.md")
        with self.assertRaisesRegex(ValueError, "Reconciliar"):
            self.proposal((ids[unit], same_role))
        for bad in (self.submissions + "/x", self.generated + "/x", self.sources + "/Privado/z",
                    self.sources + "/.git/config", self.sources + "/_datos_internos/x"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.proposal((ids[a], bad))

    def test_empty_categories_preserve_materials(self):
        old = self.file(self.sources + "/material.md")
        self.assertEqual("unchanged", organization.plan_organization(self.root, mode="keep")["status"])
        plan = organization.plan_organization(self.root, mode="categories", directory=self.sources)
        self.assertEqual(len(CATEGORIES), len(plan["operations"]))
        self.assertFalse((self.root / self.sources / "Teoría").exists())
        self.apply(plan)
        for category in CATEGORIES:
            self.assertEqual([], list((self.root / self.sources / category).iterdir()))
        self.assertTrue(old.exists())
        record = next(r for r in read_catalog(self.root)["materials"].values()
                      if r.get("path") == self.sources + "/Teoría")
        self.assertEqual("Teoría", record["classification"]["primary"])
        self.assertEqual("unchanged", organization.plan_organization(
            self.root, mode="categories", directory=self.sources)["status"])

    def test_interrupted_directory_promotion_recovers_without_regrading_or_deduping(self):
        old = self.generated + "/Ecosistemas"
        new = self.sources + "/Campo/Ecosistemas"
        inner = "/plantilla.md"
        self.file(old + inner, "Ficha")
        self.file(old + "/_datos_internos/material-docente.json", "{}")
        ids = self.ids()
        with self.assertRaisesRegex(ValueError, "unidad completa"):
            self.proposal((ids[old + inner], new + inner), mode="promote")
        plan = self.proposal((ids[old], new), mode="promote")
        rename = organization._rename_new
        def interrupt(source, destination):
            rename(source, destination)
            raise RuntimeError("Interrupción simulada")
        with mock.patch.object(organization, "_rename_new", side_effect=interrupt):
            with self.assertRaises(RuntimeError):
                self.apply(plan)
        self.assertTrue((self.root / new / "plantilla.md").is_file())
        with self.assertRaisesRegex(ValueError, "interrumpido"):
            reconcile(self.root)
        output = self.apply(plan)
        self.assertEqual("ok", output["status"])
        self.assertTrue(all(c["promoted"] for c in output["changes"]))
        rows = read_catalog(self.root)["materials"]
        for suffix in ("", inner):
            row = rows[ids[old + suffix]]
            self.assertEqual((row["path"], row["origin"], row["consolidation"], row["content_version"]),
                             (new + suffix, "ai", "consolidated", 1))
            self.assertEqual("needs_review", row["processing"])
        self.assertEqual("unchanged", self.proposal((ids[old], new), mode="promote")["status"])
        self.apply(plan)
        history = self.root / "Archivos de gestión del proyecto" / "historial_operaciones.jsonl"
        events = [event["kind"] for line in history.read_text(encoding="utf-8").splitlines()
                  for event in json.loads(line)["operations"]]
        self.assertEqual(1, events.count("promote"))
        self.assertEqual(1, events.count("move_intent"))
