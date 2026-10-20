"""Propuestas de reorganización del curso: nunca aplica movimientos.

El informe ayuda al agente a presentar un cambio concreto antes de solicitar
aprobación. Los hashes permiten comprobar que la fuente no cambió entre la
propuesta y su aplicación. La revisión de enlaces cubre Markdown ordinario;
PDF, documentos ofimáticos, HTML y enlaces construidos requieren revisión manual.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from .project import CONFIG_NAME, _inside, _relative, _root, _safe_path

SKIP_DIRECTORIES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+[^\n)]*)?\)")
REFERENCE = re.compile(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(?:<([^>\n]+)>|(\S+))")
CONTROL_FILES = {CONFIG_NAME, "AGENTS.md", "LEEME.md"}


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
                           "Tras aprobar y aplicar movimientos, actualizar la selección de fuentes y los registros del mapa que dependan de ellos."],
              "links": [], "requires_approval": True}
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
            if source in CONTROL_FILES or destination in CONTROL_FILES:
                raise ValueError("AGENTS.md, LEEME.md y proyecto-docente.json requieren una modificación separada, no una reubicación.")
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
    return result
