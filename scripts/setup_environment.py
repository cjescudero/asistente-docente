#!/usr/bin/env python3
"""Prepara Python local en macOS, Linux o Windows; no instala el plugin en un anfitrión."""
from __future__ import annotations
import argparse
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def default_destination(*, dev=False, platform=None, environ=None, home=None):
    """Separar el runtime habitual de materiales y del plugin instalado."""
    if dev:
        return ROOT / '.venv'
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    if platform == 'win32':
        cache = Path(environ.get('LOCALAPPDATA', home / 'AppData/Local'))
    elif platform == 'darwin':
        cache = home / 'Library/Caches'
    else:
        cache = Path(environ.get('XDG_CACHE_HOME', home / '.cache'))
        if not cache.is_absolute():
            cache = home / '.cache'
    manifest = ROOT / 'plugin.json'
    if not manifest.is_file():
        manifest = ROOT / '.claude-plugin/plugin.json'
    version = json.loads(manifest.read_text(encoding='utf-8'))['version']
    return cache / 'asistente-docente' / version / 'venv'


def commands(destination, *, pdf=False, dev=False, windows=None):
    windows = sys.platform == 'win32' if windows is None else windows
    python = Path(destination) / ('Scripts/python.exe' if windows else 'bin/python')
    requirements = ROOT / ('requirements-dev.txt' if dev else 'requirements-pdf.txt' if pdf else 'requirements.txt')
    result = [[sys.executable, '-m', 'venv', str(destination)],
              [str(python), '-m', 'pip', 'install', '-r', str(requirements)]]
    if pdf:
        result.append([str(python), '-m', 'playwright', 'install', 'chromium'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv', type=Path, help='Entorno destino; por defecto caché de usuario, o .venv con --dev')
    parser.add_argument('--pdf', action='store_true', help='Instalar también Playwright y Chromium')
    parser.add_argument('--dev', action='store_true', help='Instalar dependencias de desarrollo; Chromium requiere --pdf')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar las operaciones sin crear ni descargar nada')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Se necesita Python 3.10 o posterior.')
    destination = (args.venv or default_destination(dev=args.dev)).expanduser().resolve()
    sys.path.insert(0, str(ROOT))
    from docencia.project import find_project
    if find_project(destination):
        parser.error('El entorno debe quedar fuera de los materiales del curso.')
    if destination.exists() and not (destination / 'pyvenv.cfg').is_file():
        parser.error('El destino existe y no es un entorno virtual; elige una carpeta nueva.')
    steps = commands(destination, pdf=args.pdf, dev=args.dev)
    if args.dry_run:
        print(json.dumps(steps, ensure_ascii=False, indent=2))
        return 0
    try:
        for command in steps:
            subprocess.run(command, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f'Preparación incompleta: {exc}', file=sys.stderr)
        return 1
    print(f'Entorno listo: {destination}. La instalación del plugin se hace por separado en el anfitrión.')
    python = destination / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    diagnosis = [str(python), str(ROOT / 'scripts/docencia.py'), 'doctor']
    if args.pdf:
        diagnosis.append('--pdf')
    print(f'Intérprete: {python}')
    print('Diagnóstico: ' + (subprocess.list2cmdline(diagnosis) if sys.platform == 'win32' else shlex.join(diagnosis)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
