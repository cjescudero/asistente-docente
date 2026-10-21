#!/usr/bin/env python3
"""Dos paquetes reproducibles desde una fuente; no publica ni configura hosts."""

from __future__ import annotations

import hashlib
import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_plugin import validate
from sync_manifests import adapters

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("skills", "docencia", "scripts", "assets", "docs", "templates", "examples", "schemas", "tests")
FILES = ("README.md", "CHANGELOG.md", "AGENTS.md", "NOTICE.md", "LICENSE", "CONTRIBUTING.md",
         "requirements.txt", "requirements-pdf.txt", "requirements-dev.txt", "install.sh")


def excluded(path):
    return (any(p in {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache"} for p in path.parts)
            or path.name == ".DS_Store" or path.name.startswith(".env")
            or path.suffix in {".pyc", ".zip", ".pem", ".key"})


def write_archive(stage, archive, prefix=""):
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as out:
        for file in sorted(stage.rglob("*")):
            if file.is_file():
                name = prefix + file.relative_to(stage).as_posix()
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                out.writestr(info, file.read_bytes())
    return hashlib.sha256(archive.read_bytes()).hexdigest()


def build_release(root=ROOT):
    root = Path(root).resolve()
    errors = validate(root)
    if errors:
        raise ValueError("Plugin inválido: " + "; ".join(errors))
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    release = root / "release"
    release.mkdir(exist_ok=True)
    hashes = {}
    content_hashes = {}
    for target in ("agent-plugins", "claude"):
        with tempfile.TemporaryDirectory(prefix="asistente-docente-release-") as temp:
            stage = Path(temp)
            for folder in FOLDERS:
                source = root / folder
                if source.exists():
                    if source.is_symlink():
                        raise ValueError(f"No se empaquetan enlaces simbólicos: {source}")
                    for file in source.rglob("*"):
                        if excluded(file.relative_to(root)):
                            continue
                        if file.is_symlink():
                            raise ValueError(f"No se empaquetan enlaces simbólicos: {file}")
                        if not file.is_file() or "__pycache__" in file.parts or file.suffix in {".pyc", ".zip"} or file.name == ".DS_Store":
                            continue
                        destination = stage / file.relative_to(root)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(file, destination)
            for name in FILES:
                if (root / name).is_symlink():
                    raise ValueError(f"No se empaquetan enlaces simbólicos: {name}")
                shutil.copyfile(root / name, stage / name)
            if target == "agent-plugins":
                shutil.copyfile(root / "plugin.json", stage / "plugin.json")
                (stage / ".codex-plugin").mkdir()
                (stage / ".codex-plugin/plugin.json").write_text(json.dumps(adapters(manifest)[".codex-plugin/plugin.json"], ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
            else:
                (stage / ".claude-plugin").mkdir()
                adapter = adapters(manifest)[".claude-plugin/plugin.json"]
                (stage / ".claude-plugin/plugin.json").write_text(json.dumps(adapter, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
            errors = validate(stage)
            if errors:
                raise ValueError(f"Paquete {target}: " + "; ".join(errors))
            common = {file.relative_to(stage).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
                      for file in stage.rglob("*") if file.is_file() and file.name != "plugin.json"}
            if content_hashes and common != content_hashes:
                raise ValueError("Los paquetes difieren en su contenido funcional.")
            content_hashes = common
            archive = release / f"asistente-docente-{manifest['version']}-{target}.zip"
            hashes[archive.name] = write_archive(stage, archive)
    (release / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for name,digest in hashes.items()), encoding="utf-8", newline="\n")
    (release / "contents.json").write_text(json.dumps(content_hashes, indent=2)+"\n", encoding="utf-8", newline="\n")
    return hashes


def build_source_archive(root=ROOT):
    """Fuente para GitHub con catálogos y CI, sin instalaciones ni releases anteriores."""
    root = Path(root).resolve()
    errors = validate(root, public=True)
    if errors:
        raise ValueError("Fuente no preparada: " + "; ".join(errors))
    from sync_manifests import sync
    if sync(root, check=True):
        raise ValueError("Regenera los manifiestos y catálogos antes de distribuir la fuente.")
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    release = root / 'release'
    release.mkdir(exist_ok=True)
    archive = release / f"asistente-docente-{manifest['version']}-source.zip"
    with tempfile.TemporaryDirectory() as temp:
        stage = Path(temp)
        for name in (*FOLDERS, *FILES, 'plugin.json', '.zenodo.json', '.github', '.agents', '.claude-plugin', '.codex-plugin', '.gitignore', '.gitattributes'):
            source = root / name
            if source.is_symlink():
                raise ValueError(f"Enlace simbólico no distribuible: {name}")
            for file in source.rglob('*') if source.is_dir() else [source]:
                relative = file.relative_to(root)
                if excluded(relative):
                    continue
                if file.is_symlink():
                    raise ValueError(f"Enlace simbólico no distribuible: {relative}")
                if file.is_file():
                    destination = stage / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(file, destination)
        digest = write_archive(stage, archive, prefix='asistente-docente/')
    (release / 'SOURCE-SHA256SUMS').write_text(f'{digest}  {archive.name}\n', encoding='utf-8', newline='\n')
    return {archive.name: digest}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='store_true', help='Añadir ZIP de fuente para GitHub')
    args = parser.parse_args()
    hashes = build_release()
    if args.source:
        hashes.update(build_source_archive())
    print(json.dumps(hashes, indent=2))
