"""Actualizar las referencias de los documentos derivados mediante el catálogo del curso."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from .catalog import read_catalog, refresh_stat, transaction
from .knowledge import repair_markdown
from .project import _safe_path, load_project
from .spaces import under, corpus_policy

REGISTERS = ("actividad.json", "catalogo.json", "metadatos.json")


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _generated(path, config):
    return (any(under(path, area) for area in config["spaces"]["generated"])
            and not any(under(path, x) for x in config["sources"]["exclude"])
            and not (config.get("map") and under(path, config["map"])))


def _candidates(root, config, records):
    """Localizar salidas registradas y tres contratos concretos en sus unidades."""
    frozen = set()
    folders = {}
    for mid, row in records.items():
        path = row.get("path")
        if not path or row["presence"] != "present" or row["origin"] != "ai" or not _generated(path, config):
            continue
        if row["kind"] == "folder" and _safe_path(root, path + "/_datos_internos").is_dir():
            folders[mid] = path
            if _safe_path(root, path + "/_datos_internos/manifest.json").is_file():
                frozen.add(path)
    for mid, row in records.items():
        path = row.get("path")
        if (not path or row["presence"] != "present" or row["origin"] != "ai"
                or not _generated(path, config) or any(under(path, base) for base in frozen)):
            continue
        if row["kind"] == "file" and path.lower().endswith(".md"):
            yield mid, mid, "", path
        if mid in folders:
            for name in REGISTERS:
                suffix = "_datos_internos/" + name
                location = path + "/" + suffix
                if _safe_path(root, location).is_file():
                    yield mid + "/" + suffix, mid, suffix, location


def _fields(data, name, root, folder):
    """Campos cuyo significado y base de ruta están definidos por el formato."""
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Registro de formato desconocido.")
    if name == "actividad.json":
        entries = list(data["sources"])
        for value in data["files"].values():
            entries.extend(value if isinstance(value, list) else [value])
        for item in entries:
            yield item, "path", folder
    elif name == "catalogo.json":
        path_base = data.get("path_base", "catalog")
        if path_base not in ("catalog", "project"):
            raise ValueError("Base de rutas del catálogo desconocida.")
        for bank in data["banks"]:
            for key in ("gift", "metadata"):
                yield bank, key, root if path_base == "project" else folder
    else:
        for item in data["materials"].values():
            yield item, "path", root
        for section in ("concepts", "questions"):
            for entry in data[section].values():
                for item in entry.get("references", []):
                    yield item, "path", root


class _Targets:
    """Resolver cada enlace observado contra su ID previamente vinculado."""
    def __init__(self, root, paths, records, previous, config, ambiguous):
        self.root, self.paths, self.records = root, paths, records
        self.previous, self.config, self.ambiguous = previous, config, ambiguous
        self.refs, self.issues = {}, set()

    def get(self, path, default):
        if not path.is_relative_to(self.root):
            return default
        relative = path.relative_to(self.root).as_posix()
        ref = self.previous.get(relative)
        if not ref:
            # Los registros internos de un banco se trasladan con la unidad a la que pertenecen.
            if "/_datos_internos/" in relative:
                base, rest = relative.split("/_datos_internos/", 1)
                suffix = "/_datos_internos/" + rest
            else:
                base, suffix = relative, ""
            if base in self.ambiguous:
                self.issues.update(self.ambiguous[base])
                return default
            mid = self.paths.get(base)
            if not mid:
                return default
            ref = {"material_id": mid, "content_version": self.records[mid]["content_version"],
                   "suffix": suffix}
        mid = ref["material_id"]
        row = self.records[mid]
        dest = row.get("path")
        config = self.config
        if (not dest or row["presence"] != "present" or not any(
                under(dest, r) for r in config["spaces"]["sources"] + config["spaces"]["generated"])
                or any(under(dest, r) for r in config["sources"]["exclude"] + config["spaces"]["submissions"])):
            self.issues.add(mid)
            self.refs[relative] = ref
            return default
        target = dest + ref["suffix"]
        if (row["content_version"] != ref["content_version"]
                or ref.get("reviewed_hash") and ref["reviewed_hash"] != row.get("sha256")):
            self.issues.add(mid)
        self.refs[target] = ref
        return self.root / target


def _render(raw, path, previous_path, root, targets):
    text = raw.decode("utf-8")
    if path.suffix.lower() == ".md":
        return repair_markdown(text, previous_path.parent, path.parent, targets)
    data = json.loads(text.lstrip("\ufeff"))
    changed = False
    for entry, key, base in _fields(data, path.name, root, previous_path.parent):
        value = entry[key]
        if not isinstance(value, str) or os.path.isabs(value):
            raise ValueError("Se esperaba una ruta relativa.")
        old = Path(os.path.abspath(base / value))
        new = targets.get(old, old)
        new_base = path.parent if base == previous_path.parent else base
        if (new != old or base != new_base) and new.is_relative_to(root):
            updated = Path(os.path.relpath(new, new_base)).as_posix()
            if path.name == "catalogo.json" and ".." in Path(updated).parts:
                raise ValueError("Revisar la base del catálogo antes de enlazar fuera de su carpeta.")
            entry[key] = updated
            changed = True
        if entry.get("sha256") and new.is_relative_to(root):
            ref = targets.refs.get(new.relative_to(root).as_posix())
            if ref:
                ref["reviewed_hash"] = entry["sha256"]
                if targets.records[ref["material_id"]].get("sha256") != entry["sha256"]:
                    targets.issues.add(ref["material_id"])
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n" if changed else text


def _write(path, text):
    # Conservar el modo de acceso del documento al sustituirlo de forma atómica.
    mode = stat.S_IMODE(path.stat().st_mode)
    fd, name = tempfile.mkstemp(prefix=".reparar-enlaces-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(text.encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _resume(tx, root, config):
    intent = tx.data.get("dependency_write")
    if not intent:
        return
    path = _safe_path(root, intent["path"])
    if not _generated(intent["path"], config):
        raise ValueError("El registro pendiente ha salido del espacio generado.")
    sha = _hash(path.read_bytes())
    if sha == intent["before"]:
        if list(_stat(path)) != intent["stat_before"]:
            raise ValueError(f"Cambió la identidad del documento pendiente: {intent['path']}.")
        _write(path, intent["text"])
    elif sha != intent["after"]:
        raise ValueError(f"El documento cambió durante la reparación: {intent['path']}.")
    _finish(tx, root, intent["key"], intent["binding"])
    del tx.data["dependency_write"]
    tx.event("repair_generated_links", path=intent["path"])
    tx.flush()


def _finish(tx, root, key, binding):
    path = _safe_path(root, binding["path"])
    binding["stat"] = list(_stat(path))
    if key in tx.data["materials"]:
        row = tx.data["materials"][key]
        refresh_stat(row, path)
        row["sha256"] = binding["sha256"]
    tx.data.setdefault("derived_documents", {})[key] = binding


def recover_dependencies(root):
    """Reanudar una escritura antes de volver a comparar inodes o versiones."""
    if read_catalog(root).get("dependency_write"):
        root = Path(root).resolve()
        with transaction(root) as tx:
            config = load_project(root)
            _resume(tx, root, {**config, "sources": corpus_policy(root, config)})


def _stat(path):
    info = path.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def refresh_dependencies(root, changes=()):
    """Reparar enlaces e informar de qué derivados requieren revisión de contenido."""
    root = Path(root).resolve()
    config = load_project(root)
    config = {**config, "sources": corpus_policy(root, config)}
    report = {"repaired": [], "needs_review": [], "registered": 0}
    with transaction(root) as tx:
        _resume(tx, root, config)
        rows = tx.data["materials"]
        bindings = tx.data.setdefault("derived_documents", {})
        paths = {r["path"]: mid for mid, r in rows.items() if r.get("path") and r["presence"] == "present"}
        old_names, ambiguous = {}, {}
        pending = tx.data.get("dependency_moves", {})
        hints = {name: set(ids) for name, ids in pending.items()}
        for item in changes:
            before = item.get("old_path", item.get("before"))
            mid = item["material_id"]
            if before and mid in rows and rows[mid]["path"] != before:
                hints.setdefault(before, set()).add(mid)
        candidates = list(_candidates(root, config, rows))
        if hints and any(key not in bindings for key, _, _, _ in candidates):
            # Persistir las correspondencias hasta vincular todos los documentos, también
            # en el primer uso, por si el proceso se interrumpe tras reparar solo uno.
            tx.data["dependency_moves"] = {name: sorted(ids) for name, ids in hints.items()}
            tx.flush()
        for before, ids in hints.items():
            current = paths.get(before)
            if len(ids) != 1 or (current and current not in ids):
                ambiguous[before] = sorted(ids | ({current} if current else set()))
            else:
                mid = next(iter(ids))
                paths.setdefault(before, mid)
                old_names[mid] = before
        for key, mid, suffix, relative in candidates:
            path = _safe_path(root, relative)
            previous = bindings.get(key, {})
            old_path = previous.get("path") or (old_names.get(mid, rows[mid]["path"]) + ("/" + suffix if suffix else ""))
            refs = previous.get("refs", {})
            try:
                if previous and previous["stat"] == list(_stat(path)) and old_path == relative:
                    targets = _Targets(root, paths, rows, refs, config, ambiguous)
                    if all(targets.get(root / p, root / p) == root / p for p in refs):
                        issues = sorted(set(previous["issues"]) | targets.issues)
                        if issues:
                            report["needs_review"].append({"path": relative, "materials": issues})
                        continue
                stamp = list(_stat(path))
                raw = path.read_bytes()
                if key == mid and _hash(raw) != rows[mid]["sha256"]:
                    raise ValueError("El documento generado cambió. Reconciliar su contenido antes de repararlo.")
                targets = _Targets(root, paths, rows, refs, config, ambiguous)
                output = _render(raw, path, root / old_path, root, targets)
                updated = output.encode("utf-8")
                binding = {"path": relative, "refs": targets.refs, "issues": sorted(targets.issues),
                           "sha256": _hash(updated)}
                if raw != updated:
                    tx.data["dependency_write"] = {"key": key, "path": relative, "text": output,
                                                   "binding": binding, "stat_before": stamp, "before": _hash(raw), "after": _hash(updated)}
                    tx.flush()
                    _resume(tx, root, config)
                    report["repaired"].append(relative)
                else:
                    binding["stat"] = list(_stat(path))
                    bindings[key] = binding
                if targets.issues:
                    report["needs_review"].append({"path": relative, "materials": sorted(targets.issues)})
                report["registered"] += not bool(previous)
            except (ValueError, OSError, TypeError, KeyError) as exc:
                if "dependency_write" in tx.data:
                    raise
                report["needs_review"].append({"path": relative, "reason": str(exc)})
        tx.data.pop("dependency_moves", None)
    report["status"] = "review" if report["needs_review"] else "ok"
    return report
