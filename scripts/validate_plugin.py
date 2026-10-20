#!/usr/bin/env python3
"""Valida manifiestos, frontmatter, enlaces locales y dependencias empaquetadas."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from validate_library import _links
from sync_manifests import generated_files

EXPECTED = {"preparar-actividades-docentes", "generar-apuntes-estudio",
            "evaluar-entregas", "crear-bancos-preguntas",
            "preparar-examenes-papel-moodle", "generar-feedback-evaluaciones",
            "redactar-espanol-claro", "crear-infografias-didacticas",
            "crear-mapa-docente", "consultar-mapa-docente",
            "visualizar-mapa-docente", "iniciar-proyecto-docente"}
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def validate(root: Path, public: bool = False) -> list[str]:
    import jsonschema
    import yaml
    root = root.resolve()
    errors = []
    portable = root / "plugin.json"
    claude = root / ".claude-plugin/plugin.json"
    if not portable.exists() and not claude.exists():
        return ["Falta un manifiesto de plugin."]
    manifest = json.loads((portable if portable.exists() else claude).read_text(encoding="utf-8"))
    if portable.exists():
        schema = json.loads((root / "schemas/agent-plugins-1.0.0.schema.json").read_text(encoding="utf-8"))
        errors.extend(f"Manifest: {e.message}" for e in jsonschema.Draft202012Validator(schema).iter_errors(manifest))
    else:
        if set(manifest) - {"name", "version", "description", "author", "homepage", "repository", "license", "keywords"}:
            errors.append("Manifiesto Claude: campos no previstos en el adaptador.")
    if portable.exists():
        interface = manifest.get("extensions", {}).get("com.openai", {}).get("interface", {})
        if not 1 <= len(interface.get("shortDescription", "")) <= 30:
            errors.append("Presentación OpenAI: shortDescription debe tener 1–30 caracteres.")
        prompts = interface.get("defaultPrompt")
        if not isinstance(prompts, (str, list)) or isinstance(prompts, list) and (len(prompts) > 3 or not all(isinstance(p, str) and p.strip() for p in prompts)):
            errors.append("Presentación OpenAI: defaultPrompt debe ser un texto o hasta tres textos.")
        for name, expected in generated_files(manifest).items():
            file = root / name
            if file.exists() and json.loads(file.read_text(encoding="utf-8")) != expected:
                errors.append(f"Adaptador o catálogo desactualizado: {name}")
    if public:
        if manifest.get("license") != "MIT" or not (root / "LICENSE").is_file():
            errors.append("Distribución pública: falta la licencia MIT acordada o su archivo.")
        repository = urlsplit(manifest.get("repository", ""))
        if repository.scheme != "https" or repository.netloc != "github.com" or len(repository.path.strip('/').split('/')) != 2:
            errors.append("Distribución pública: falta la URL HTTPS del repositorio GitHub.")
    if manifest.get("name") != "asistente-docente" or not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        errors.append("Identidad o versión de plugin incorrectas.")
    found = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    if found != EXPECTED:
        errors.append(f"Catálogo inesperado: faltan {EXPECTED-found}; sobran {found-EXPECTED}.")
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n") or "\n---\n" not in content[4:]:
            errors.append(f"Frontmatter ausente: {path.relative_to(root)}")
            continue
        data = yaml.safe_load(content.split("---", 2)[1])
        if not isinstance(data, dict):
            errors.append(f"Frontmatter inválido: {path.name}")
            continue
        if data.get("name") != path.parent.name or set(data)-ALLOWED:
            errors.append(f"Nombre/campos no portables: {path.parent.name}")
        description = data.get("description")
        if not isinstance(description, str) or not 1 <= len(description) <= 1024:
            errors.append(f"Descripción inválida: {path.parent.name}")
        if len(path.parent.name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.parent.name):
            errors.append(f"Nombre no válido: {path.parent.name}")
    for folder in [root / "skills", root / "docs", root]:
        paths = folder.glob("*.md") if folder == root else folder.rglob("*.md")
        for path in paths:
            content = path.read_text(encoding="utf-8")
            if re.search(r"/Users/|/home/[^\s]+/|C:\\\\Users\\\\", content):
                errors.append(f"Ruta personal: {path.relative_to(root)}")
            for target in _links(content):
                if not target or re.match(r"[a-z]+:", target):
                    continue
                target = unquote(urlsplit(target).path)
                if not target:
                    continue
                dest = (path.parent / target).resolve()
                if root not in dest.parents or not dest.exists():
                    errors.append(f"Enlace roto/fuera del paquete: {path.relative_to(root)} -> {target}")
    vendor = root / "assets/vendor/mathjax"
    provenance = json.loads((vendor / "provenance.json").read_text(encoding="utf-8"))
    for name, expected in provenance["files"].items():
        file = vendor / name
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            errors.append(f"Integridad MathJax: {name}")
    if not (vendor / "LICENSE").is_file():
        errors.append("Falta licencia de MathJax.")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--public", action="store_true", help="Exigir licencia y repositorio de distribución")
    args = parser.parse_args()
    try:
        errors = validate(args.root, public=args.public)
    except (OSError, ValueError, ImportError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "invalid" if errors else "ok", "errors": errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
