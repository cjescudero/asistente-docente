"""Comportamiento del instalador, sin descargas ni cambios globales en la suite."""
import json
import io
import importlib.util
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import setup_environment as setup


class SetupTests(unittest.TestCase):
    def test_runtime_defaults_to_user_cache_on_all_platforms(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            version = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))['version']
            for platform, prefix in (('darwin', home / 'Library/Caches'),
                                     ('win32', home / 'AppData/Local'),
                                     ('linux', home / '.cache')):
                target = setup.default_destination(platform=platform, environ={}, home=home)
                self.assertEqual(target, prefix / 'asistente-docente' / version / 'venv')
                self.assertFalse(target.is_relative_to(ROOT))
            self.assertEqual(setup.default_destination(dev=True), ROOT / '.venv')

    def test_runtime_cannot_be_created_among_course_materials(self):
        from docencia.project import initialize_project
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'curso'
            initialize_project(root)
            with patch.object(sys, 'argv', ['setup', '--venv', str(root / 'alumnado/venv'), '--dry-run']), \
                    redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                setup.main()
            self.assertFalse((root / 'alumnado/venv').exists())

    def test_basic_and_pdf_dependencies_are_distinct(self):
        basic = setup.commands(Path('entorno con espacios'), windows=False)
        self.assertEqual(len(basic), 2)
        self.assertEqual(Path(basic[1][-1]).name, 'requirements.txt')
        self.assertEqual(basic[1][0].replace('\\', '/'), 'entorno con espacios/bin/python')
        pdf = setup.commands(Path('entorno'), pdf=True, windows=True)
        self.assertEqual(len(pdf), 3)
        self.assertTrue(pdf[1][0].replace('\\', '/').endswith('Scripts/python.exe'))
        self.assertEqual(Path(pdf[1][-1]).name, 'requirements-pdf.txt')
        self.assertEqual(pdf[2][1:], ['-m', 'playwright', 'install', 'chromium'])
        dev = setup.commands(Path('entorno'), dev=True)
        self.assertEqual(len(dev), 2)
        self.assertEqual(Path(dev[1][-1]).name, 'requirements-dev.txt')

    def test_dry_run_from_other_cwd_does_not_create_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'entorno con espacios'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/setup_environment.py'),
                                     '--venv', str(target), '--dry-run'],
                                    cwd=temp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)[0][-1], str(target.resolve()))
            self.assertFalse(target.exists())

    def test_non_environment_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'material.md'
            file.write_text('No sobrescribir', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/setup_environment.py'),
                                     '--venv', temp], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(temp).iterdir()), [file])

    def test_install_failure_stops_before_browser_download(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'venv'
            with patch.object(sys, 'argv', ['setup', '--venv', str(target), '--pdf']), \
                    patch.object(setup.subprocess, 'run', side_effect=[None, subprocess.CalledProcessError(1, 'pip')]) as run, redirect_stderr(io.StringIO()):
                self.assertEqual(setup.main(), 1)
                self.assertEqual(run.call_count, 2)

    def test_doctor_accepts_basic_environment_but_reports_pdf_unavailable(self):
        spec = importlib.util.spec_from_file_location('docencia_cli', ROOT / 'scripts/docencia.py')
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with patch.object(cli.importlib.util, 'find_spec', side_effect=lambda name: object() if name == 'markdown_it' else None):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(cli.main(['doctor']), 0)
            report = json.loads(output.getvalue())
            self.assertTrue(report['basic_ready'])
            self.assertFalse(report['pdf_ready'])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(['doctor', '--pdf']), 2)
