"""Pruebas sobre paquetes extraídos; no basta con validar la fuente."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_release import build_release, build_source_archive
from sync_manifests import sync
from validate_plugin import validate


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="asistente-docente-packaging-")
        cls.root = Path(cls.temp.name) / "source"
        shutil.copytree(ROOT, cls.root, ignore=shutil.ignore_patterns(
            ".venv", ".git", "release", "__pycache__", "*.pyc", ".DS_Store"))
        cls.hashes = build_release(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_separate_manifests_and_identical_resources(self):
        entries = []
        for name, digest in self.hashes.items():
            file = self.root / "release" / name
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), digest)
            with zipfile.ZipFile(file) as archive:
                names = archive.namelist()
                expected = ".claude-plugin/plugin.json" if "-claude.zip" in name else "plugin.json"
                self.assertIn(expected, names)
                self.assertIn('LICENSE', names)
                self.assertIn('schemas/AGENT-PLUGINS-LICENSE.txt', names)
                self.assertFalse(any(n.endswith('marketplace.json') for n in names))
                if '-claude.zip' not in name:
                    self.assertIn('.codex-plugin/plugin.json', names)
                self.assertNotIn("plugin.json" if "-claude.zip" in name else ".claude-plugin/plugin.json", names)
                self.assertEqual(json.loads(archive.read(expected))["name"], "asistente-docente")
                self.assertEqual(sum(n.startswith("skills/") and n.endswith("/SKILL.md") for n in names), 12)
                self.assertIn("skills/proyecto-docente-inicializacion-adaptacion/SKILL.md", names)
                self.assertIn("skills/proyecto-docente-ayuda/SKILL.md", names)
                self.assertEqual(sum(n.startswith("skills/") and n.endswith("/agents/openai.yaml") for n in names), 12)
                self.assertIn("skills/mapa-docente-creacion-visualizacion/references/visualizacion.md", names)
                self.assertFalse(any(n.startswith("skills/visualizar-mapa-docente/") for n in names))
                self.assertIn("skills/mapa-docente-creacion-visualizacion/assets/agents-mapa.md", names)
                self.assertNotIn("skills/proyecto-docente-inicializacion-adaptacion/assets/agents-proyecto.md", names)
                self.assertTrue(all(not n.startswith(("/", "bin/")) and "\\" not in n and ".." not in Path(n).parts for n in names))
                self.assertFalse(any(".venv" in n or "__pycache__" in n or n.endswith(".zip") for n in names))
                entries.append({n:archive.read(n) for n in names if Path(n).name != 'plugin.json'})
        self.assertEqual(entries[0], entries[1])

    def test_reproducible_archive(self):
        self.assertEqual(build_release(self.root), self.hashes)

    def test_course_and_external_environment_preview_from_both_packages(self):
        for name in self.hashes:
            with self.subTest(package=name), tempfile.TemporaryDirectory() as temp:
                base = Path(temp).resolve()
                install = base / "plugin"
                with zipfile.ZipFile(self.root / "release" / name) as archive:
                    archive.extractall(install)
                # Probar sin site-packages y con instalación de solo lectura.
                paths = list(install.rglob("*")) + [install]
                try:
                    for path in paths:
                        path.chmod(0o555 if path.is_dir() else 0o444)
                    preview = subprocess.run([sys.executable, "-S", str(install / "scripts/setup_environment.py"),
                                              "--dry-run"], cwd=base, capture_output=True, text=True,
                                             encoding="utf-8")
                    self.assertEqual(preview.returncode, 0, preview.stderr)
                    destination = Path(json.loads(preview.stdout)[0][-1])
                    self.assertFalse(destination.is_relative_to(install))
                    course = base / "curso"
                    result = subprocess.run([sys.executable, "-S", str(install / "scripts/docencia.py"),
                                             "init-project", str(course)], cwd=base,
                                            capture_output=True, text=True, encoding="utf-8")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertFalse(json.loads(result.stdout)["wiki_created"])
                    self.assertTrue((course / "AGENTS.md").is_file())
                    self.assertTrue((course / "resultados").is_dir())
                    self.assertTrue((course / "creados/actividades").is_dir())
                    self.assertEqual(list((course / "mapa-docente").iterdir()), [])
                    connected = subprocess.run(
                        [sys.executable, str(install / "examples/recorrido-docente/comprobar.py"),
                         str(base / "recorrido")], cwd=base, capture_output=True,
                        text=True, encoding="utf-8")
                    self.assertEqual(connected.returncode, 0, connected.stderr)
                    self.assertTrue(json.loads(connected.stdout)["originals_preserved"])
                finally:
                    for path in reversed(paths):
                        path.chmod(0o755 if path.is_dir() else 0o644)

    def test_packaging_preserves_unicode_with_legacy_system_encoding(self):
        original_read = Path.read_text

        def read_with_legacy_default(path, encoding=None, errors=None):
            return original_read(path, encoding=encoding or 'cp1252', errors=errors)

        with patch.object(Path, 'read_text', read_with_legacy_default):
            self.assertEqual(build_release(self.root), self.hashes)
            self.assertTrue(build_source_archive(self.root))

    def test_source_contains_catalogs_and_clean_rebuild_works(self):
        source_hashes = build_source_archive(self.root)
        self.assertEqual(build_source_archive(self.root), source_hashes)
        destination = Path(self.temp.name) / 'github-copy'
        name, digest = next(iter(source_hashes.items()))
        archive_path = self.root / 'release' / name
        self.assertEqual(hashlib.sha256(archive_path.read_bytes()).hexdigest(), digest)
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            for required in ('.github/workflows/ci.yml', '.gitignore', '.gitattributes', '.agents/plugins/marketplace.json',
                             '.claude-plugin/marketplace.json', '.claude-plugin/plugin.json', 'LICENSE'):
                self.assertIn('asistente-docente/' + required, names)
            self.assertFalse(any('/release/' in n or '/.venv/' in n or '/.git/' in n for n in names))
            archive.extractall(destination)
        root = destination / 'asistente-docente'
        self.assertEqual(sync(root, check=True), [])
        self.assertEqual(validate(root, public=True), [])
        run = subprocess.run([sys.executable, str(root / 'scripts/build_release.py')],
                             cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout), self.hashes)

    def test_skill_interface_drift_and_absence_are_reported(self):
        interface = self.root / "skills/actividades-evaluacion/agents/openai.yaml"
        original = interface.read_bytes()
        try:
            interface.write_text('interface:\n  display_name: "Otra categoría"\n  short_description: "Breve"\n', encoding="utf-8")
            errors = validate(self.root)
            self.assertTrue(any("Nombre visible incorrecto" in e for e in errors))
            self.assertTrue(any("Descripción corta inválida" in e for e in errors))
            interface.unlink()
            self.assertTrue(any("Interfaz ausente" in e for e in validate(self.root)))
        finally:
            interface.write_bytes(original)

    def test_generated_adapter_drift_and_missing_license_are_reported(self):
        adapter = self.root / '.claude-plugin/plugin.json'
        original = adapter.read_bytes()
        try:
            data = json.loads(original)
            data['version'] = '999.0.0'
            adapter.write_text(json.dumps(data), encoding='utf-8')
            self.assertTrue(any('desactualizado' in error for error in validate(self.root)))
        finally:
            adapter.write_bytes(original)
        license_path = self.root / 'LICENSE'
        license_data = license_path.read_bytes()
        try:
            license_path.unlink()
            self.assertTrue(any('licencia' in error for error in validate(self.root, public=True)))
        finally:
            license_path.write_bytes(license_data)

    def test_private_runtime_files_are_excluded_from_all_archives(self):
        env = self.root / 'examples/.env'
        cache = self.root / 'scripts/__pycache__'
        env.write_text('SYNTHETIC_PRIVATE_VALUE', encoding='utf-8')
        cache.mkdir(exist_ok=True)
        cached = cache / 'synthetic.pyc'
        cached.write_bytes(b'SYNTHETIC_PRIVATE_VALUE')
        try:
            hashes = {**build_release(self.root), **build_source_archive(self.root)}
            for name in hashes:
                with zipfile.ZipFile(self.root / 'release' / name) as archive:
                    self.assertFalse(any('/.env' in n or '__pycache__' in n for n in archive.namelist()))
        finally:
            env.unlink()
            cached.unlink()

    def test_extracted_packages_work_from_other_cwd(self):
        for index, name in enumerate(self.hashes):
            destination = Path(self.temp.name) / f"host-{index}"
            with zipfile.ZipFile(self.root / "release" / name) as archive:
                archive.extractall(destination)
            self.assertEqual(validate(destination), [])
            run = subprocess.run([sys.executable, str(destination / "scripts/docencia.py"),
                                  "validate-bank", str(destination / "examples/ciencias/banco.gift")],
                                 cwd=self.temp.name, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["questions"], 6)
            library = subprocess.run([sys.executable, str(destination / "scripts/validate_library.py"),
                                      str(destination / "examples/mapa-docente/mapa-docente")],
                                     cwd=self.temp.name, capture_output=True, text=True)
            self.assertEqual(library.returncode, 0, library.stdout + library.stderr)
            self.assertEqual(json.loads(library.stdout)["sources"], 7)
            graph = subprocess.run([sys.executable, str(destination / "scripts/build_graph.py"),
                                    str(destination / "examples/mapa-docente/mapa-docente"),
                                    "--output", str(Path(self.temp.name) / f"student-{index}.html"),
                                    "--audience", "estudiante"],
                                   cwd=self.temp.name, capture_output=True, text=True)
            self.assertEqual(graph.returncode, 0, graph.stdout + graph.stderr)
            exported = (Path(self.temp.name) / f"student-{index}.html").read_text(encoding="utf-8")
            self.assertNotIn("source:f004", exported)
            self.assertNotIn("archivo-evaluaciones", exported)

            # Both distributions must render the wiki without writing into the
            # installed plugin, or importing helpers from the source checkout.
            for path in sorted(destination.rglob("*"), reverse=True):
                path.chmod(0o555 if path.is_dir() else 0o444)
            destination.chmod(0o555)
            try:
                teacher = subprocess.run([sys.executable, str(destination / "scripts/build_graph.py"),
                    str(destination / "examples/mapa-docente/mapa-docente"),
                    "--output", str(Path(self.temp.name) / f"teacher-{index}.html"),
                    "--wiki-output", str(Path(self.temp.name) / f"wiki-{index}.html")],
                    cwd=self.temp.name, capture_output=True, text=True,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                self.assertEqual(teacher.returncode, 0, teacher.stdout + teacher.stderr)
                self.assertTrue((Path(self.temp.name) / f"wiki-{index}.html").is_file())
                self.assertEqual(json.loads(teacher.stdout)["wiki"]["status"], "ok")
            finally:
                destination.chmod(0o755)
                for path in destination.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)

    def test_documented_markdown_examples_are_not_real_links(self):
        readme = self.root / "README.md"
        original_bytes = readme.read_bytes()
        original = original_bytes.decode("utf-8")
        try:
            readme.write_text(original + "\n`[ejemplo](no-existe.md)`\n```md\n[otro](tampoco.md)\n```\n", encoding="utf-8")
            self.assertEqual(validate(self.root), [])
        finally:
            readme.write_bytes(original_bytes)

    def test_broken_documentation_link_is_reported(self):
        readme = self.root / "README.md"
        original_bytes = readme.read_bytes()
        original = original_bytes.decode("utf-8")
        try:
            readme.write_text(original + "\n[roto](no-existe.md)\n", encoding="utf-8")
            self.assertTrue(any("no-existe.md" in error for error in validate(self.root)))
        finally:
            readme.write_bytes(original_bytes)
