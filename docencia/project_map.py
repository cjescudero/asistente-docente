"""Aplicar la selección del curso a mapas existentes sin leer fuentes excluidas."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from docencia.project import (CONFIG_NAME, project_config_path, _replace_config, _safe_path, find_project,
                              load_project, source_allowed)
from .spaces import under


def map_course(guide, project_root=None):
    """Resolver el curso antes de abrir cualquier registro o página del mapa."""
    project = Path(project_root).resolve() if project_root else find_project(guide)
    if project is None:
        return None, None
    relative = guide.relative_to(project).as_posix()
    config = load_project(project)
    for name in config.get("spaces", {}).get("notes", []):
        if relative == "." or under(relative, name) or under(name, relative):
            raise ValueError("El mapa debe quedar separado de las notas del curso.")
    return project, config


def check_map_policy(guide, data, *, source_roots=None, project_root=None,
                     link_extractor=None, course=None):
    """Informe de revisión pendiente; nunca altera el mapa ni abre originales.

    Sin configuración de proyecto, la política del curso no se aplica al mapa.
    Se calculan dependencias tanto por source_ids como por enlaces Markdown.
    """
    guide = Path(guide).resolve()
    result = {"status": "not_applicable", "errors": [], "excluded_source_ids": [],
              "affected_pages": []}
    errors = result["errors"]
    try:
        project, config = map_course(guide, project_root) if course is None else course
    except (ValueError, OSError) as exc:
        errors.append(f"Configuración del proyecto: {exc}")
        result["status"] = "invalid"
        return result
    if project is None:
        return result
    result.update(status="ok", project=str(project))
    if not config["sources"]["selected"]:
        errors.append("La selección de fuentes está pendiente; elegir el corpus antes de reutilizar el mapa.")
    if link_extractor is None:
        from scripts.validate_library import _links
        link_extractor = _links
    roots = data.get("source_roots") if data.get("schema_version") == 2 else {
        "principal": data.get("sources_root")}
    roots = roots if isinstance(roots, dict) else {}
    overrides = source_roots or {}
    notes = config.get("spaces", {}).get("notes", [])
    if notes:
        for root_id, root_path in roots.items():
            if isinstance(root_path, str):
                base = (Path(overrides[root_id]).expanduser() if root_id in overrides else guide / root_path).resolve()
                if base.is_relative_to(project) and any(under(base.relative_to(project).as_posix(), folder)
                                                        for folder in notes):
                    errors.append(f"La raíz de fuentes {root_id} pertenece a las notas del curso.")
    rows = {}
    if config["structure"] == "curso-v4":
        from .spaces import corpus_policy
        config = {**config, "sources": corpus_policy(project, config)}
        from .catalog import read_catalog
        rows = {r["path"]: r for r in read_catalog(project)["materials"].values()
                if r["kind"] == "file" and r["presence"] == "present" and r.get("access_confirmed")}
    excluded = set()
    affected = set()
    for source in data.get("sources", []) if isinstance(data.get("sources"), list) else []:
        if not isinstance(source, dict):
            continue  # El validador del registro diagnostica la estructura.
        root_id = source.get("root", "principal")
        relative = source.get("path")
        root = roots.get(root_id) if isinstance(root_id, str) else None
        if not isinstance(root, str) or not isinstance(relative, str):
            continue
        base = Path(overrides[root_id]).expanduser() if root_id in overrides else guide / root
        candidate = Path(os.path.abspath(base / relative))
        record = rows.get(candidate.relative_to(project).as_posix()) if candidate.is_relative_to(project) else None
        restricted = record and source.get("access") == "estudiante" and record["access"] != "estudiante"
        if restricted or candidate.resolve().is_relative_to(guide) or not source_allowed(project, config, candidate):
            identifier = source.get("id")
            if isinstance(identifier, str):
                excluded.add(identifier)
            if isinstance(source.get("page"), str):
                affected.add(source["page"])
    for page in data.get("pages", []) if isinstance(data.get("pages"), list) else []:
        if not isinstance(page, dict):
            continue
        ids, name = page.get("source_ids"), page.get("path")
        if isinstance(ids, list) and isinstance(name, str):
            if any(isinstance(identifier, str) and identifier in excluded for identifier in ids):
                affected.add(name)
    dependencies = {}
    for path in guide.rglob("*.md"):
        name = path.relative_to(guide).as_posix()
        if not path.resolve().is_relative_to(guide) or (notes and path.stat().st_nlink > 1):
            errors.append(f"Página fuera del mapa o con una identidad compartida: {name}")
            affected.add(name)
            continue
        dependencies[name] = set()
        try:
            content = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            errors.append(f"No se puede comprobar {name}: {exc}")
            affected.add(name)
            continue
        for link in link_extractor(content):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            decoded = re.sub(r"\\([() ])", r"\1", unquote(parsed.path))
            target = Path(os.path.abspath(path.parent / decoded))
            if target.is_relative_to(guide) and target.resolve().is_relative_to(guide):
                if target.suffix == ".md":
                    dependencies[name].add(target.relative_to(guide).as_posix())
            elif not source_allowed(project, config, target):
                affected.add(name)
    # Punto fijo: incluye ciclos y páginas enlazadas indirectamente.
    while True:
        added = {name for name, targets in dependencies.items() if targets & affected} - affected
        if not added:
            break
        affected.update(added)
    result["excluded_source_ids"] = sorted(excluded)
    result["affected_pages"] = sorted(affected)
    if excluded:
        errors.append("Fuentes fuera de la selección o del acceso autorizado: " + ", ".join(sorted(excluded)))
    if affected:
        errors.append("Páginas pendientes de revisión antes de reutilizar: " + ", ".join(sorted(affected)))
    result["status"] = "invalid" if errors else "ok"
    return result


def register_map(root, map_dir, *, dry_run=False):
    """Registrar solo un mapa real válido. La skill reconcilia AGENTS.md."""
    root = Path(root).expanduser().resolve()
    config = load_project(root)
    path = Path(map_dir).expanduser()
    path = path if path.is_absolute() else root / path
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("El mapa debe estar dentro de la raíz del curso.") from exc
    if ".." in Path(relative).parts:
        raise ValueError("El mapa debe usar una ruta dentro del curso.")
    path = _safe_path(root, relative)
    if not (path / "index.md").is_file():
        raise ValueError("El mapa necesita un index.md real antes de registrarse.")
    config["map"] = relative
    if config["structure"] == "curso-v4":
        from .spaces import validate_config
        validate_config(root, config)
    from scripts.validate_library import validate_library
    report = validate_library(path, project_root=root)
    if report["status"] != "ok":
        raise ValueError("Mapa no válido: " + "; ".join(report["errors"]))
    if not dry_run:
        if config["structure"] == "curso-v4":
            from .knowledge import register_dependencies
            from .project import ensure_management_dir
            register_dependencies(root, path)
            current = load_project(root)
            if current["spaces"] != config["spaces"] or current["sources"] != config["sources"]:
                raise ValueError("Cambió la asignación de fuentes durante el registro. Revisa el mapa.")
            current["map"] = relative
            config = current
            destination = ensure_management_dir(root) / CONFIG_NAME
        else:
            destination = project_config_path(root)
        _replace_config(destination, json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    result = {"status": "dry_run" if dry_run else "ok", "map": relative,
              "config": config, "agents_updated": False}
    if config["structure"] == "curso-v4" and not dry_run:
        from .knowledge import refresh_knowledge
        result["knowledge"] = refresh_knowledge(root)
    return result
