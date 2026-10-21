"""Propuestas de reorganización del curso: nunca aplica movimientos.

El informe ayuda al agente a presentar un cambio concreto antes de solicitar
aprobación. Los hashes permiten comprobar que la fuente no cambió entre la
propuesta y su aplicación. La revisión de enlaces cubre Markdown ordinario;
PDF, documentos ofimáticos, HTML y enlaces construidos requieren revisión manual.
Los registros reconocidos se señalan para revisión semántica: no se sustituyen
rutas sin conocer su base ni se alteran los snapshots de evaluaciones.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from .project import CONFIG_NAME, CONFIG_V3, _inside, _relative, _root, _safe_path

SKIP_DIRECTORIES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+[^\n)]*)?\)")
REFERENCE = re.compile(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(?:<([^>\n]+)>|(\S+))")
CONTROL_FILES = {CONFIG_NAME, CONFIG_V3, "AGENTS.md", "LEEME.md"}


def _files(folder: Path):
    """No seguir symlinks; informar aparte de los que impedirían una migración."""
    files, links, errors = [], [], []
    def visit(path):
        try:
            with os.scandir(path) as entries:
                entries = sorted(entries, key=lambda item: item.name)
            for entry in entries:
                child = Path(entry.path)
                if entry.is_symlink():
                    links.append(child)
                elif entry.is_dir(follow_symlinks=False):
                    visit(child)
                elif entry.is_file(follow_symlinks=False):
                    files.append(child)
                else:
                    errors.append(f"Archivo no regular: {child}")
        except OSError as exc:
            errors.append(f"No se puede recorrer {path}: {exc}")
    visit(folder)
    return files, links, errors


def _after(path: Path, moves: list[dict], root: Path) -> Path:
    for move in moves:
        source = root / move["source"]
        if path == source or move["kind"] == "directory" and _inside(path, source):
            return root / move["destination"] / path.relative_to(source)
    return path


def _markdown_files(root: Path):
    errors = []
    def failed(exc):
        errors.append(str(exc))
    found = []
    for directory, names, filenames in os.walk(root, followlinks=False, onerror=failed):
        names[:] = sorted(name for name in names if name not in SKIP_DIRECTORIES
                          and not (Path(directory) / name).is_symlink())
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.suffix.lower() == ".md" and not path.is_symlink():
                found.append(path)
    return found, errors


def _review_links(root: Path, moves: list[dict]) -> tuple[list[dict], list[str]]:
    references = []
    files, warnings = _markdown_files(root)
    for page in files:
        try:
            content = page.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            warnings.append(f"No se pueden revisar los enlaces de {page.relative_to(root)}: {exc}")
            continue
        page_after = _after(page, moves, root)
        matches = sorted([*LINK.finditer(content), *REFERENCE.finditer(content)], key=lambda match: match.start())
        for match in matches:
            link = match.group(1) or match.group(2)
            try:
                parsed = urlsplit(link)
            except ValueError:
                warnings.append(f"Enlace no interpretable en {page.relative_to(root)}: {link}")
                continue
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
                continue
            try:
                target = (page.parent / unquote(parsed.path)).resolve()
            except (OSError, ValueError):
                continue
            if not _inside(target, root):
                continue
            target_after = _after(target, moves, root)
            if page_after == page and target_after == target:
                continue
            relative = os.path.relpath(target_after, page_after.parent).replace(os.sep, "/")
            suggested = urlunsplit(("", "", quote(relative, safe="/.-_~"), parsed.query, parsed.fragment))
            references.append({"document": page.relative_to(root).as_posix(),
                               "document_after": page_after.relative_to(root).as_posix(),
                               "line": content.count("\n", 0, match.start()) + 1,
                               "link": link, "suggested_link": suggested,
                               "target": target.relative_to(root).as_posix(),
                               "target_after": target_after.relative_to(root).as_posix(),
                               "needs_update": unquote(suggested) != unquote(link)})
    return references, warnings


def _review_metadata(root: Path, moves: list[dict]) -> tuple[list[dict], list[str]]:
    """Inventariar controles afectados potencialmente sin reescribirlos.

    La base de rutas puede ser el curso, el registro, el catálogo o una raíz del
    mapa. Por eso una coincidencia textual no basta para sugerir una sustitución.
    Se informa de todos los registros reconocidos cuando hay movimientos;
    requiere que el agente compruebe las referencias según su contrato.
    """
    if not moves:
        return [], []
    found, warnings = [], []
    def failed(exc):
        warnings.append(str(exc))
    for directory, names, filenames in os.walk(root, followlinks=False, onerror=failed):
        names[:] = sorted(name for name in names if name not in SKIP_DIRECTORIES
                          and not (Path(directory) / name).is_symlink())
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.is_symlink() or path.suffix.lower() != ".json":
                continue
            lower = name.lower()
            if name == CONFIG_NAME:
                kind, reason = "project", "Revisar structure, sources.include/exclude y map tras la migración aprobada."
            elif lower == "fuentes.json":
                kind, reason = "map", "Revisar raíces, rutas, páginas y dependencias del mapa sin declarar lecturas nuevas."
            elif "catalogo" in lower or "catalog" in lower:
                kind, reason = "catalog", "Revisar la base de rutas y los enlaces a bancos y metadatos, sin duplicar originales."
            elif lower in ("actividad.json", "activity.json"):
                kind, reason = "activity", "Revisar las rutas a fuentes, enunciado, plantillas, rúbrica y guía de corrección."
            elif lower == "material-docente.json":
                kind, reason = "material", "Conservar identidad, tipo y estado; comprobar su carpeta estable y el LEEME asociado."
            elif "manifest" in lower or "manifiesto" in lower:
                kind, reason = "exam_snapshot", "Preservar el manifiesto y los bancos congelados; comprobar referencias externas sin regenerar el cuestionario."
            elif "metadatos" in lower or "metadata" in lower or lower.endswith(".meta.json"):
                kind, reason = "metadata", "Revisar localizadores y referencias a materiales según la base de rutas declarada."
            else:
                continue
            found.append({"document": path.relative_to(root).as_posix(),
                          "document_after": _after(path, moves, root).relative_to(root).as_posix(),
                          "kind": kind, "reason": reason, "requires_review": True})
    return found, warnings


def plan_migration(root, moves) -> dict:
    """Proponer movimientos exactos, sin mover ni editar un solo archivo.

    ``moves`` admite un dict ``{origen: destino}`` o una lista de objetos
    ``{"from": "ruta", "to": "ruta"}`` (también ``source``/``destination``),
    todos relativos al curso.
    Destinos existentes, movimientos solapados y symlinks bloquean la propuesta.
    """
    root = _root(root)
    result = {"status": "ready", "root": str(root), "moves": [], "errors": [],
              "warnings": ["Esta propuesta no mueve archivos ni actualiza enlaces.",
                           "Revisión automática limitada a enlaces Markdown ordinarios. Revisar manualmente PDF, documentos ofimáticos, HTML y enlaces construidos.",
                           "Tras aprobar y aplicar movimientos, revisar configuración, catálogos, registros de actividad y metadatos del mapa; preservar los manifiestos y snapshots de cuestionarios.",
                           "metadata_reviews identifica registros para revisión semántica; no determina automáticamente qué campos deben cambiar."],
              "links": [], "metadata_reviews": [], "requires_approval": True}
    if not root.is_dir():
        raise ValueError("La raíz debe existir para preparar una migración.")
    if isinstance(moves, dict):
        moves = [{"source": source, "destination": destination} for source, destination in moves.items()]
    if not isinstance(moves, list):
        raise ValueError("moves debe ser una lista de movimientos o un objeto origen-destino.")
    for item in moves:
        try:
            if not isinstance(item, dict):
                raise ValueError("Cada movimiento debe declarar from/to o source/destination.")
            if ("source" in item and "from" in item and item["source"] != item["from"]) or ("destination" in item and "to" in item and item["destination"] != item["to"]):
                raise ValueError("Un movimiento contiene nombres alternativos contradictorios.")
            source = _relative(item.get("source", item.get("from")), label="source")
            destination = _relative(item.get("destination", item.get("to")), label="destination")
            config_relocation = source == CONFIG_NAME and destination == CONFIG_V3
            if (source in CONTROL_FILES or destination in CONTROL_FILES) and not config_relocation:
                raise ValueError("AGENTS.md, LEEME.md y la configuración requieren una propuesta específica; no se reubican implícitamente.")
            source_path, destination_path = _safe_path(root, source), _safe_path(root, destination)
            if source == destination:
                raise ValueError(f"Origen y destino son iguales: {source}")
            if not source_path.exists():
                raise ValueError(f"No existe el origen: {source}")
            if destination_path.exists():
                raise ValueError(f"Colisión: ya existe el destino {destination}")
            if _inside(destination_path, source_path):
                raise ValueError(f"El destino no puede estar dentro del origen: {source}")
            kind = "directory" if source_path.is_dir() else "file"
            if kind == "directory":
                files, links, errors = _files(source_path)
                if links or errors:
                    raise ValueError(f"No se puede migrar {source}: contiene enlaces simbólicos o rutas no accesibles.")
            elif source_path.is_file():
                files = [source_path]
            else:
                raise ValueError(f"El origen no es un archivo o directorio regular: {source}")
            details = []
            for file in files:
                digest = hashlib.sha256()
                with file.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
                suffix = file.relative_to(source_path) if kind == "directory" else Path()
                details.append({"source": file.relative_to(root).as_posix(),
                                "destination": (destination_path / suffix).relative_to(root).as_posix(),
                                "sha256": digest.hexdigest(), "size": file.stat().st_size})
            result["moves"].append({"source": source, "destination": destination, "kind": kind, "files": details})
        except (ValueError, OSError) as exc:
            result["errors"].append(str(exc))
    for index, first in enumerate(result["moves"]):
        for second in result["moves"][index + 1:]:
            for field in ("source", "destination"):
                left, right = root / first[field], root / second[field]
                if _inside(left, right) or _inside(right, left):
                    result["errors"].append(f"Movimientos con {field} solapados: {first[field]} y {second[field]}")
                elif left.as_posix().casefold() == right.as_posix().casefold():
                    result["errors"].append(f"Colisión de {field} en sistemas que no distinguen mayúsculas: {first[field]} y {second[field]}")
            for source_move, destination_move in ((first, second), (second, first)):
                source_path = root / source_move["source"]
                destination_path = root / destination_move["destination"]
                if _inside(source_path, destination_path) or _inside(destination_path, source_path):
                    result["errors"].append("Un destino se solapa con el origen de otro movimiento: "
                                            + destination_move["destination"] + " / " + source_move["source"])
    if result["errors"]:
        result["status"] = "invalid"
    else:
        result["links"], warnings = _review_links(root, result["moves"])
        result["warnings"].extend(warnings)
        result["metadata_reviews"], warnings = _review_metadata(root, result["moves"])
        result["warnings"].extend(warnings)
    return result
