"""Uso de bancos con un corpus seleccionado, actividades directas y el catálogo lógico."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from docencia import banks, catalog
from docencia.project import initialize_course, source_allowed, load_project


class BankCourseTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.sources = "Material de la asignatura"
        self.ai = "Material generado por IA"
        self.config = initialize_course(self.root, include=[self.sources],
                                       exclude=[self.sources + "/privado", self.ai + "/excluido"])["config"]
        self.gift = self.ai + "/bancos/celulas/tema.gift"
        self.meta = self.ai + "/bancos/celulas/_datos_internos/metadatos.json"
        self.index = self.ai + "/bancos/_datos_internos/catalogo.json"
        self.write(self.gift, "::forma::La célula cambia de forma.{T}")
        self.bank = {"id": "ciencias", "gift": self.gift, "metadata": self.meta}
        self.index_data = {"schema_version": 1, "path_base": "project", "banks": [self.bank]}
        self.write(self.index, self.index_data)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
        return path

    def declare(self, ref, *, access="docente", identity=None, version=None):
        material = {"title": "Muestra", "path": ref, "access": access,
                    "sha256": hashlib.sha256((self.root / ref).read_bytes()).hexdigest()}
        if identity:
            material.update(material_id=identity, content_version=version)
        self.metadata = {"schema_version": 1, "materials": {"celulas": material},
                         "concepts": {"forma": {"label": "Formas celulares",
                                                "references": [{"title": "Repaso", "path": ref,
                                                               "access": access}]}},
                         "questions": {"forma": {"concepts": ["forma"], "objective": "Reconocer formas",
                                                 "guidance": "Observa la muestra", "difficulty": "basica",
                                                 "source_refs": [{"material_id": "celulas", "locators": ["1"]}]}}}
        self.write(self.meta, self.metadata)

    def load(self, direct=None):
        return banks.load_catalog(self.root / self.index, direct_materials=direct)

    def test_direct_activity_requires_selection_and_keeps_its_wiki_status(self):
        rel = self.ai + "/clase/practica.md"
        self.write(rel, "# Práctica de laboratorio")
        self.declare(rel)
        with self.assertRaisesRegex(ValueError, "no seleccionada"):
            self.load()
        self.assertEqual(len(self.load([rel])["bank"]), 1)
        self.assertFalse(source_allowed(self.root, load_project(self.root), self.root / rel))
        with self.assertRaises(ValueError):
            self.load([self.ai + "/clase"])
        self.declare(rel, access="estudiante")
        with self.assertRaisesRegex(ValueError, "reserva"):
            self.load([rel])
        catalog.reconcile(self.root, scope=self.ai + "/clase")
        rid = next(r["material_id"] for r in catalog.read_catalog(self.root)["materials"].values()
                   if r["path"] == rel)
        catalog.classify(self.root, rid, primary="Práctica", access="estudiante")
        self.assertEqual(self.load([rid])["metadata"]["materials"]["celulas"]["access"], "estudiante")

    def test_pinned_version_and_reference_follow_moves_not_content_edits(self):
        rel = self.sources + "/tema.md"
        old = self.write(rel, "# Fundamentos teóricos")
        catalog.reconcile(self.root)
        record = next(r for r in catalog.read_catalog(self.root)["materials"].values() if r["path"] == rel)
        self.declare(rel, identity=record["material_id"], version=1)
        current = self.sources + "/tema-a.md"
        old.rename(self.root / current)
        catalog.reconcile(self.root)
        data = self.load()["metadata"]
        self.assertEqual(data["materials"]["celulas"]["path"], current)
        self.assertEqual(data["concepts"]["forma"]["references"][0]["path"], current)
        self.assertEqual(json.loads((self.root / self.meta).read_bytes())["materials"]["celulas"]["path"], rel)
        self.write(current, "# Fundamentos teóricos de la medición")
        with self.assertRaisesRegex(ValueError, "ha cambiado"):
            self.load()
        catalog.reconcile(self.root)
        with self.assertRaisesRegex(ValueError, "versión"):
            self.load()

    def test_no_catalog_gift_metadata_or_direct_input_from_protected_roots(self):
        rel = self.sources + "/permitido.md"
        self.write(rel, "Materia de estudio")
        self.declare(rel)
        for restricted in ("Entregas/lote", self.sources + "/privado", self.ai + "/excluido",
                           "Archivos de gestión del proyecto", self.ai + "/.carpeta"):
            with self.subTest(restricted=restricted):
                self.write(restricted + "/entrada.json", "inválido")
                for field in ("gift", "metadata"):
                    self.write(self.index, {**self.index_data, "banks": [{**self.bank, field: restricted + "/entrada.json"}]})
                    with self.assertRaisesRegex(ValueError, "excluida"):
                        self.load()
                with self.assertRaisesRegex(ValueError, "excluida"):
                    banks.load_catalog(self.root / restricted / "entrada.json")
                with self.assertRaisesRegex(ValueError, "excluida"):
                    banks.validate_course_bank_files(self.root / self.gift, self.root / restricted / "entrada.json")
                with self.assertRaisesRegex(ValueError, "excluida"):
                    banks.validate_course_bank_files(self.root / restricted / "entrada.json")
                self.write(self.index, self.index_data)
                self.declare(restricted + "/entrada.json")
                with self.assertRaises(ValueError):
                    self.load([restricted + "/entrada.json"])
        self.declare(rel)
        forbidden = self.root / "Entregas"
        alias = self.root / self.ai / "vinculo"
        try:
            alias.symlink_to(forbidden, target_is_directory=True)
        except OSError:
            return
        with self.assertRaisesRegex(ValueError, "simbólico"):
            banks.load_catalog(alias / "lote/entrada.json")
