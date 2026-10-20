#!/usr/bin/env python3
"""Read-only validation of a Markdown teaching library and its source registry.

Validate inline/image Markdown links and reference definitions, excluding code.
URL destinations are not fetched. Heading names and fragment anchors are not
validated. This tool never creates a library, changes a source, or writes hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SOURCE_FIELDS = {"id", "title", "path", "kind", "course", "currency", "access",
                 "reading", "reviewed_locators", "sha256", "page"}
CHOICES = {
    "kind": {"diapositivas", "presentacion", "apuntes", "examen", "evaluacion", "practica", "taller", "rubrica", "programa", "otro"},
    "currency": {"vigente", "historica", "desconocida"},
    "access": {"docente", "estudiante", "restringido", "desconocido"},
    "reading": {"pendiente", "parcial", "completa", "no_legible"},
}
PAGE_KINDS = {"concepto", "tema", "presentacion", "apuntes", "practica", "taller", "evaluacion", "programa", "otro"}
ADMIN_PAGES = {"index.md", "LEEME.md", "incidencias.md", "log.md"}


def _inside(path, root):
    return path == root or root in path.parents


def _relative(value):
    return (isinstance(value, str) and bool(value.strip()) and "\\" not in value
            and "\x00" not in value and not PurePosixPath(value).is_absolute()
            and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value))


def _links(text):
    """Extract file destinations from common Markdown link forms, not code."""
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    text = re.sub(r"(`+).*?\1", "", "\n".join(lines), flags=re.DOTALL)
    inline = r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|(?:\\.|[^()\s]|\([^()\n]*\))+)"
    reference = r"^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|[^\s]+)"
    return [match.group(1).strip("<>") for pattern in (inline, reference)
            for match in re.finditer(pattern, text, re.MULTILINE)]


def _validate_pages(data, guide, errors, warnings):
    """Check the page registry without pretending to verify its academic claims."""
    pages = data.get("pages")
    if not isinstance(pages, list):
        errors.append("pages debe ser una lista en schema_version 2.")
        return
    raw_sources = data.get("sources", [])
    source_by_id = {s["id"]: s for s in raw_sources
                    if isinstance(s, dict) and isinstance(s.get("id"), str)} if isinstance(raw_sources, list) else {}
    declared = {}
    for index, page in enumerate(pages, 1):
        prefix = f"Página {index}: "
        if not isinstance(page, dict):
            errors.append(prefix + "debe ser un objeto JSON.")
            continue
        if set(page) != {"path", "title", "kind", "access", "source_ids"}:
            errors.append(prefix + "se requieren path, title, kind, access y source_ids, sin otros campos.")
        name = page.get("path")
        if (not _relative(name) or PurePosixPath(name).suffix != ".md"
                or ".." in PurePosixPath(name).parts or PurePosixPath(name).as_posix() != name):
            errors.append(prefix + "path debe identificar una página .md dentro del mapa.")
        elif name in declared:
            errors.append(prefix + "path duplicado: " + name)
        else:
            declared[name] = page
            try:
                resolved = (guide / name).resolve()
                if not _inside(resolved, guide) or not resolved.is_file():
                    errors.append(prefix + "path no identifica una página existente dentro del mapa: " + name)
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(prefix + str(exc))
            folder = "contenidos" if page.get("access") == "estudiante" else "reservado"
            if PurePosixPath(name).parts[0] != folder:
                errors.append(prefix + f"guardar la página en {folder}/ según su acceso declarado.")
        if not isinstance(page.get("title"), str) or not page["title"].strip():
            errors.append(prefix + "title debe ser texto no vacío.")
        if not isinstance(page.get("kind"), str) or page["kind"] not in PAGE_KINDS:
            errors.append(prefix + "kind no admitido.")
        if not isinstance(page.get("access"), str) or page["access"] not in CHOICES["access"]:
            errors.append(prefix + "access no admitido.")
        ids = page.get("source_ids")
        if not isinstance(ids, list) or any(not isinstance(s, str) for s in ids):
            errors.append(prefix + "source_ids debe ser una lista de identificadores de fuente.")
            continue
        if len(ids) != len(set(ids)) or any(s not in source_by_id for s in ids):
            errors.append(prefix + "source_ids contiene duplicados o fuentes no registradas.")
        if page.get("access") == "estudiante" and any(source_by_id.get(s, {}).get("access") != "estudiante" for s in ids):
            warnings.append(prefix + "cita fuentes no compartibles; el grafo del estudiante la excluirá junto con sus dependientes.")
    for source in source_by_id.values():
        page = source.get("page")
        if page is None:
            continue
        if not isinstance(page, str) or page not in declared:
            errors.append(f"Fuente {source['id']}: su ficha no está registrada en pages.")
        elif not isinstance(declared[page].get("source_ids"), list) or source["id"] not in declared[page]["source_ids"]:
            errors.append(f"Fuente {source['id']}: la ficha debe declarar su ID en source_ids.")
    for path in guide.rglob("*.md"):
        name = path.relative_to(guide).as_posix()
        if name not in ADMIN_PAGES and name not in declared:
            errors.append("Página de contenido sin registrar en pages: " + name)


def validate_library(guide_dir, sources_root=None, source_roots=None, project_root=None):
    """Return {status, errors, warnings, sources}; perform no filesystem writes."""
    errors, warnings = [], ["No se comprueban encabezados ni anclas de los enlaces Markdown."]
    result = {"status": "invalid", "errors": errors, "warnings": warnings, "sources": 0}
    try:
        guide = Path(guide_dir).expanduser().resolve()
        if not guide.is_dir():
            raise ValueError("GUIDE_DIR no es una carpeta existente.")
        registry = guide / "fuentes.json"
        if not _inside(registry.resolve(), guide):
            raise ValueError("fuentes.json se resuelve fuera de GUIDE_DIR.")
        data = json.loads(registry.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("fuentes.json debe contener un objeto JSON.")
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        errors.append(str(exc))
        return result
    version = data.get("schema_version")
    if type(version) is not int or version not in (1, 2):
        errors.append("schema_version debe ser el entero 1 o 2.")
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        errors.append("title debe ser un texto no vacío.")
    if "course" not in data or (data["course"] is not None and not isinstance(data["course"], str)):
        errors.append("course debe ser texto o null.")
    roots = {}
    declared_roots = data.get("source_roots") if version == 2 else {"principal": data.get("sources_root")}
    overrides = source_roots or {}
    if not isinstance(overrides, dict):
        errors.append("Los overrides de source_roots deben ser un objeto.")
        overrides = {}
    if version == 2 and sources_root is not None:
        errors.append("Para schema_version 2 usar --source-root ID=DIR, no --sources-root.")
    if version != 2 and sources_root is not None:
        overrides = {**overrides, "principal": sources_root}
    # Comprobar la selección antes de leer o calcular huellas de los originales.
    from docencia.project_map import check_map_policy
    try:
        policy = check_map_policy(guide, data, source_roots=overrides,
                                  project_root=project_root, link_extractor=_links)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        errors.append(f"No se pudo comprobar la selección del curso: {exc}")
        return result
    if policy["status"] != "not_applicable":
        result["project_policy"] = policy
        if policy["status"] != "ok":
            errors.extend(policy["errors"])
            return result
    if not isinstance(declared_roots, dict) or not declared_roots:
        errors.append("source_roots debe declarar una o varias carpetas elegidas por el usuario.")
        declared_roots = {}
    if set(overrides) - set(declared_roots):
        errors.append("Override de una raíz no declarada en el inventario.")
    for root_id, relative in declared_roots.items():
        if not isinstance(root_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", root_id):
            errors.append("Identificador de raíz inválido.")
            continue
        if not _relative(relative):
            errors.append("sources_root/source_roots debe ser una ruta POSIX relativa no vacía.")
            continue
        try:
            root = (Path(overrides[root_id]).expanduser() if root_id in overrides
                    else guide / relative).resolve()
            roots[root_id] = root
            if not root.is_dir():
                errors.append(f"La carpeta de fuentes {root_id} no existe.")
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            errors.append(f"No se puede resolver sources_root: {exc}")
    sources = data.get("sources")
    if not isinstance(sources, list):
        errors.append("sources debe ser una lista.")
        sources = []
    else:
        result["sources"] = len(sources)
        if not sources:
            warnings.append("La biblioteca todavía no contiene fuentes registradas.")
    identifiers = set()
    for index, source in enumerate(sources, 1):
        prefix, initial_errors = f"Fuente {index}: ", len(errors)
        if not isinstance(source, dict):
            errors.append(prefix + "debe ser un objeto JSON.")
            continue
        fields = SOURCE_FIELDS | {"root"} if version == 2 else SOURCE_FIELDS
        if set(source) != fields:
            errors.append(prefix + "campos obligatorios ausentes o campos no reconocidos: "
                          + ", ".join(sorted(fields.symmetric_difference(source))))
        root_id = source.get("root") if version == 2 else "principal"
        root = roots.get(root_id) if isinstance(root_id, str) else None
        if version == 2 and (not isinstance(root_id, str) or root_id not in declared_roots):
            errors.append(prefix + "root no identifica una carpeta declarada.")
        identifier = source.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
            errors.append(prefix + "id debe usar lowercase kebab-case.")
        elif identifier in identifiers:
            errors.append(prefix + "id duplicado: " + identifier)
        else:
            identifiers.add(identifier)
        if not isinstance(source.get("title"), str) or not source["title"].strip():
            errors.append(prefix + "title debe ser un texto no vacío.")
        if source.get("course") is not None and not isinstance(source["course"], str):
            errors.append(prefix + "course debe ser texto o null.")
        for field, allowed in CHOICES.items():
            if not isinstance(source.get(field), str) or source[field] not in allowed:
                errors.append(prefix + field + " tiene un valor no admitido.")
        locators = source.get("reviewed_locators")
        if not isinstance(locators, list) or any(not isinstance(item, str) or not item.strip() for item in locators):
            errors.append(prefix + "reviewed_locators debe ser una lista de textos no vacíos.")
        elif source.get("reading") in ("parcial", "completa") and not locators:
            errors.append(prefix + "una lectura parcial o completa requiere localizadores revisados.")
        elif source.get("reading") in ("pendiente", "no_legible") and locators:
            errors.append(prefix + "una fuente pendiente o no legible debe tener localizadores vacíos.")
        digest = source.get("sha256")
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            errors.append(prefix + "sha256 debe ser hexadecimal minúscula de 64 caracteres o null.")
        elif digest is None:
            warnings.append(prefix + "sin sha256; no se puede comprobar si el original cambió.")
        page = source.get("page")
        if source.get("reading") in ("parcial", "completa") and page is None:
            errors.append(prefix + "una lectura parcial o completa requiere page.")
        for field, value, base in (("path", source.get("path"), root), ("page", page, guide)):
            if field == "page" and value is None:
                continue
            if not _relative(value) or (field == "page" and PurePosixPath(value).suffix != ".md"):
                errors.append(prefix + field + " debe ser una ruta POSIX relativa" + (" .md." if field == "page" else "."))
                continue
            if base is None:
                continue
            try:
                resolved = (base / value).resolve()
                if not _inside(resolved, base):
                    errors.append(prefix + field + " se resuelve fuera de su carpeta permitida.")
                elif not resolved.is_file():
                    errors.append(prefix + field + " no identifica un archivo existente: " + value)
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(prefix + f"no se puede resolver {field}: {exc}")
        if digest is not None and root is not None and len(errors) == initial_errors:
            try:
                actual = hashlib.sha256()
                with (root / source["path"]).open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        actual.update(chunk)
                if actual.hexdigest() != digest:
                    errors.append(prefix + "sha256 no coincide: original modificado; revisión pendiente.")
            except OSError as exc:
                errors.append(prefix + "no se puede leer el original: " + str(exc))
    if version == 2:
        try:
            _validate_pages(data, guide, errors, warnings)
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append("No se pudieron revisar las páginas: " + str(exc))
    for name in sorted(ADMIN_PAGES):
        try:
            required = guide / name
            if not _inside(required.resolve(), guide) or not required.read_text(encoding="utf-8-sig").strip():
                errors.append(name + " debe ser un documento no vacío dentro de GUIDE_DIR.")
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append(name + ": " + str(exc))
    try:
        for markdown in sorted(guide.rglob("*.md")):
            try:
                if not _inside(markdown.resolve(), guide):
                    errors.append(str(markdown.relative_to(guide)) + " se resuelve fuera de GUIDE_DIR.")
                    continue
                for target in _links(markdown.read_text(encoding="utf-8-sig")):
                    if target.startswith("#"):
                        continue
                    if target.startswith("file:") or re.match(r"^[A-Za-z]:", target):
                        raise ValueError("enlace local absoluto no permitido: " + target)
                    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                        continue
                    path = unquote(urlsplit(target).path)
                    path = re.sub(r"\\([() ])", r"\1", path)
                    if not _relative(path):
                        raise ValueError("enlace local inseguro: " + target)
                    resolved = (markdown.parent / path).resolve()
                    if not (_inside(resolved, guide) or any(_inside(resolved, root) for root in roots.values())):
                        errors.append(f"{markdown.relative_to(guide)}: enlace fuera de las carpetas permitidas: {target}")
                    elif not resolved.exists():
                        errors.append(f"{markdown.relative_to(guide)}: enlace local roto: {target}")
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(f"{markdown.relative_to(guide)}: {exc}")
    except (OSError, ValueError, RuntimeError) as exc:
        errors.append("No se pudieron revisar los enlaces: " + str(exc))
    result["status"] = "invalid" if errors else "ok"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide_dir", metavar="GUIDE_DIR")
    parser.add_argument("--sources-root", metavar="DIR")
    parser.add_argument("--project", metavar="ROOT", help="Raíz del curso; se detecta en antecesores por defecto")
    parser.add_argument("--source-root", metavar="ID=DIR", action="append", default=[],
                        help="Reubicar una raíz declarada (schema 2); se puede repetir.")
    args = parser.parse_args(argv)
    overrides = {}
    for pair in args.source_root:
        name, separator, path = pair.partition("=")
        if not separator or not name or not path or name in overrides:
            parser.error("--source-root requiere ID=DIR, con ID no repetido.")
        overrides[name] = path
    result = validate_library(args.guide_dir, args.sources_root, overrides, project_root=args.project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
