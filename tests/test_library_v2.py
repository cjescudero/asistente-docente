"""Multiple user-selected roots and explicit sharing boundaries."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_library import validate_library


class MultipleRootLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mapa-docente-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.guide = self.base / "mapa elegido"
        self.guide.mkdir()
        self.sources = []
        self.pages = []
        self.roots = {"actual": "../materiales del curso", "archivo": "../archivo elegido"}
        for root_id, access, page_path in (
            ("actual", "estudiante", "contenidos/apuntes/f1.md"),
            ("archivo", "restringido", "reservado/evaluaciones/f2.md"),
        ):
            folder = self.guide / self.roots[root_id]
            folder.mkdir()
            source = folder / "mismo-nombre.md"
            source.write_text("Contenido " + root_id, encoding="utf-8")
            page = self.guide / page_path
            page.parent.mkdir(parents=True)
            page.write_text("# Fuente\n", encoding="utf-8")
            identifier = root_id
            self.sources.append(dict(id=identifier, title=root_id, path=source.name,
                                     root=root_id, kind="apuntes", course=None,
                                     currency="desconocida", access=access,
                                     reading="completa", reviewed_locators=["Documento completo"],
                                     sha256=hashlib.sha256(source.read_bytes()).hexdigest(), page=page_path))
            self.pages.append(dict(path=page_path, title=root_id, kind="apuntes",
                                   access=access, source_ids=[identifier]))
        for name in ("index.md", "LEEME.md", "incidencias.md", "log.md"):
            (self.guide / name).write_text("# Mapa\n", encoding="utf-8")
        self.data = dict(schema_version=2, title="Mapa", course=None,
                         source_roots=self.roots, sources=self.sources, pages=self.pages)
        self.save()

    def save(self):
        (self.guide / "fuentes.json").write_text(json.dumps(self.data), encoding="utf-8")

    def check(self, **kwargs):
        self.save()
        return validate_library(self.guide, **kwargs)

    def test_multiple_roots_same_filename_and_relative_links(self):
        (self.guide / "index.md").write_text(
            "[Actual](<../materiales del curso/mismo-nombre.md>)\n"
            "[Archivo](../archivo%20elegido/mismo-nombre.md)\n", encoding="utf-8")
        self.assertEqual(self.check()["status"], "ok")

    def test_sources_cannot_escape_their_assigned_root(self):
        self.sources[0]["path"] = "../archivo elegido/mismo-nombre.md"
        result = self.check()
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(any("fuera de su carpeta" in item for item in result["errors"]))

    def test_unknown_root_and_no_selected_roots_rejected(self):
        self.sources[0]["root"] = "inventada"
        self.assertEqual(self.check()["status"], "invalid")
        self.data["source_roots"] = {}
        self.assertEqual(self.check()["status"], "invalid")

    def test_user_can_relocate_one_root_explicitly(self):
        target = self.base / "nueva ubicacion"
        (self.guide / self.roots["actual"]).rename(target)
        self.assertEqual(self.check()["status"], "invalid")
        self.assertEqual(self.check(source_roots={"actual": target})["status"], "ok")
        self.assertEqual(self.check(source_roots={"no-declarada": target})["status"], "invalid")

    def test_cli_relocation_from_another_cwd(self):
        target = self.base / "copia"
        (self.guide / self.roots["actual"]).rename(target)
        script = Path(__file__).resolve().parents[1] / "scripts/validate_library.py"
        process = subprocess.run([sys.executable, str(script), str(self.guide),
                                  "--source-root", f"actual={target}"], cwd=self.base,
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["sources"], 2)

    def test_every_content_page_and_its_sources_are_registered(self):
        extra = self.guide / "contenidos/apuntes/sin-registro.md"
        extra.write_text("# Sin registrar", encoding="utf-8")
        self.assertEqual(self.check()["status"], "invalid")
        extra.unlink()
        self.pages[0]["source_ids"] = []
        self.assertEqual(self.check()["status"], "invalid")

    def test_private_pages_cannot_be_placed_in_contents(self):
        self.pages[0]["access"] = "docente"
        result = self.check()
        self.assertTrue(any("reservado/" in error for error in result["errors"]))

    def test_duplicate_or_missing_page_declarations_rejected(self):
        self.pages.append(copy.deepcopy(self.pages[0]))
        self.assertEqual(self.check()["status"], "invalid")
        self.pages.pop()
        self.pages[0]["path"] = "contenidos/apuntes/no-existe.md"
        self.assertEqual(self.check()["status"], "invalid")

    def test_new_material_kinds_are_supported(self):
        for kind in ("presentacion", "taller", "evaluacion"):
            with self.subTest(kind=kind):
                self.sources[0]["kind"] = kind
                self.pages[0]["kind"] = kind
                self.assertEqual(self.check()["status"], "ok")

    def test_malformed_v2_fields_do_not_crash(self):
        original = copy.deepcopy(self.data)
        for key, value in (("source_roots", []), ("pages", {}), ("pages", [None])):
            with self.subTest(key=key, value=value):
                self.data = {**original, key: value}
                self.assertEqual(self.check()["status"], "invalid")
        for key, value in (("root", []), ("path", {})):
            self.data = copy.deepcopy(original)
            self.data["sources"][0][key] = value
            self.assertEqual(self.check()["status"], "invalid")

        for key, value in (("source_ids", [{}]), ("access", []), ("path", {}), ("kind", [])):
            self.data = copy.deepcopy(original)
            self.data["pages"][0][key] = value
            self.assertEqual(self.check()["status"], "invalid")

    def test_page_aliases_do_not_create_duplicate_graph_nodes(self):
        self.pages.append({**self.pages[0], "path": "./" + self.pages[0]["path"]})
        self.assertEqual(self.check()["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
