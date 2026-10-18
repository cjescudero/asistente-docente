#!/usr/bin/env python3
"""Genera los adaptadores y catálogos desde plugin.json; no instala nada."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def adapters(manifest):
    common = {k: manifest[k] for k in
              ('name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords')
              if k in manifest}
    codex = {**common, 'skills': './skills',
             'interface': manifest['extensions']['com.openai']['interface']}
    return {'.claude-plugin/plugin.json': common, '.codex-plugin/plugin.json': codex}


def generated_files(manifest):
    name = manifest['name']
    return {**adapters(manifest),
        '.agents/plugins/marketplace.json': {
            'name': name, 'interface': {'displayName': 'Asistente docente'},
            'plugins': [{'name': name, 'source': {'source': 'local', 'path': './'},
                         'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                         'category': 'Productivity'}]},
        '.claude-plugin/marketplace.json': {
            'name': name, 'owner': manifest['author'],
            'metadata': {'description': 'Materiales y evaluación para cualquier asignatura'},
            'plugins': [{'name': name, 'source': './', 'description': manifest['description']}]}}


def sync(root=ROOT, check=False):
    root = Path(root)
    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    changed = []
    for name, data in generated_files(manifest).items():
        path = root / name
        content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if not path.is_file() or path.read_text(encoding='utf-8') != content:
            changed.append(name)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = sync(check=args.check)
    print(json.dumps({'status': 'outdated' if args.check and changed else 'ok', 'files': changed}, ensure_ascii=False))
    raise SystemExit(bool(args.check and changed))
