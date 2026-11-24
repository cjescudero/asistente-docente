"""Propuestas acotadas por material_id. El catálogo guarda la intención antes del rename."""
from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import unicodedata
from uuid import uuid4

from .catalog import CATEGORIES, SKIP, _digest, add_path, refresh_stat, transaction
from .project import _relative, _root, _safe_path, load_project
from .spaces import RESERVED, reserved, corpus_policy


def _within(path, directory):
    return path == directory or path.startswith(directory + "/")


def _overlap(left, right):
    def normal(value):
        return unicodedata.normalize("NFC", value).casefold()
    return _within(normal(left), normal(right)) or _within(normal(right), normal(left))


def _space(path, config):
    if reserved(path) or any(part.startswith(".") for part in Path(path).parts):
        raise ValueError(f"Ruta de control o recurso oculto: {path}")
    areas = config["spaces"]
    protected = [*areas["submissions"], "Gestión del proyecto", *config["sources"]["exclude"]]
    if config.get("map"):
        protected.append(config["map"])
    if any(_overlap(path, item) for item in protected):
        raise ValueError(f"Ruta reservada, excluida o con contenidos excluidos: {path}")
    for role in ("sources", "generated"):
        for area in areas[role]:
            if path != area and _within(path, area):
                return role
    raise ValueError(f"La operación debe quedar dentro de un espacio docente asignado: {path}")


def _whole_unit(root, relative):
    """Nunca desmembrar una actividad o una evaluación que conserva claves y bancos."""
    for parent in (root / relative).parents:
        if parent == root:
            break
        if any((parent / "_datos_internos" / name).is_file()
               for name in ("material-docente.json", "manifest.json", "actividad.json")):
            raise ValueError(f"Planifica el traslado de la unidad completa {parent.relative_to(root)}.")


def _witness(path, *, known=None):
    """Identificar físicamente el elemento y comprobar su contenido y el de sus hijos."""
    digest = hashlib.sha256()
    counts = {"files": 0, "folders": 0}
    observed = set()

    def visit(item):
        if item != path and item.name in RESERVED - {"_datos_internos"}:
            raise ValueError(f"La unidad contiene una carpeta operativa. Revisa el alcance: {item.name}.")
        st = item.lstat()
        if ((stat.S_ISREG(st.st_mode) and st.st_nlink > 1)
                or getattr(st, "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Revisa el archivo enlazado o su ubicación antes de moverlo: {item.name}")
        if stat.S_ISDIR(st.st_mode):
            kind = "folders"
        elif stat.S_ISREG(st.st_mode):
            kind = "files"
        else:
            raise ValueError(f"Tipo no admitido o enlace en la unidad: {item.name}")
        relative = item.relative_to(path)
        recorded = known is not None and relative in known
        if known is not None:
            if recorded:
                row = known[relative]
                if row["physical_id"] != {"dev": st.st_dev, "ino": st.st_ino} or row["presence"] != "present":
                    raise ValueError(f"Reconciliar la identidad de {item.name} antes de preparar el plan.")
                observed.add(relative)
            elif not any(part in SKIP or part.startswith(".") for part in relative.parts):
                raise ValueError(f"Reconciliar el elemento nuevo {item.name} antes de preparar el plan.")
        counts[kind] += 1
        digest.update(json.dumps([item.relative_to(path).as_posix(), kind, st.st_dev, st.st_ino],
                                 ensure_ascii=True).encode() + b"\n")
        if kind == "files":
            sha = _digest(item)
            if recorded and sha != row["sha256"]:
                raise ValueError(f"El contenido de {item.name} cambió. Reconciliar antes de preparar el plan.")
            digest.update(bytes.fromhex(sha))
        else:
            for child in sorted(item.iterdir()):
                visit(child)
    visit(path)
    if known is not None and observed != known.keys():
        raise ValueError("Faltan elementos inventariados. Reconciliar antes de preparar el plan.")
    return {"tree": digest.hexdigest(), **counts}


def _rename_new(source, dest):
    """Equivalente a RENAME_NOREPLACE; tampoco reemplaza un directorio vacío ajeno."""
    if os.name == "nt":
        os.rename(source, dest)  # Windows rechaza un destino existente.
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        result = libc.renamex_np(os.fsencode(source), os.fsencode(dest), 4)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        result = libc.renameat2(-100, os.fsencode(source), -100, os.fsencode(dest), 1)
    else:
        raise ValueError("El sistema de archivos requiere un traslado manual sin sobrescritura.")
    if result:
        code = ctypes.get_errno()
        if code == errno.EXDEV:
            raise ValueError("El traslado cruza volúmenes. Propón el movimiento manual y la reconciliación.")
        raise OSError(code, os.strerror(code), str(dest))


def _validate_pair(root, config, source, destination, promote):
    src = _safe_path(root, _relative(source))
    dst = _safe_path(root, _relative(destination))
    sr, dr = _space(source, config), _space(destination, config)
    if promote and (sr, dr) != ("generated", "sources"):
        raise ValueError("Consolidar requiere pasar de un espacio generado a uno de fuentes.")
    if not promote and sr != dr:
        raise ValueError("La reorganización ordinaria debe permanecer en el mismo tipo de espacio.")
    if _overlap(source, destination):
        raise ValueError("Origen y destino son iguales o se solapan.")
    _whole_unit(root, source)
    _whole_unit(root, destination)
    return src, dst


def _summary(operations):
    return {
        "folders": sum(op.get("witness", {}).get("folders", 0) for op in operations),
        "files": sum(op.get("witness", {}).get("files", 0) for op in operations),
        "destinations": [op["destination"] for op in operations],
        "units": [op["source"] for op in operations if op.get("witness", {}).get("folders")],
        "issues": [op["issue"] for op in operations if op.get("issue")],
    }


def _validate_overlaps(ops):
    for i, first in enumerate(ops):
        for second in ops[i+1:]:
            if any(_overlap(a, b) for a in (first.get("source"), first["destination"]) if a
                   for b in (second.get("source"), second["destination"]) if b):
                raise ValueError("Los movimientos seleccionados se solapan. Mantén las unidades juntas.")


def plan_organization(root, moves=(), *, mode="moves", directory=None):
    """Guardar el detalle sin mover documentos. La aceptación nombra operaciones de este plan."""
    root = _root(root)
    config = load_project(root)
    config = {**config, "sources": corpus_policy(root, config)}
    if config["structure"] != "curso-v4":
        raise ValueError("La organización por catálogo requiere un curso-v4.")
    if mode == "keep":
        return {"status": "unchanged", "operations": [], "summary": _summary([])}
    if mode not in ("categories", "moves", "promote"):
        raise ValueError("Modo de organización desconocido.")
    ops = []
    with transaction(root) as tx:
        records = tx.data["materials"]
        if mode == "categories":
            area = _relative(directory, label="espacio de fuentes")
            if area not in config["spaces"]["sources"] or not _safe_path(root, area).is_dir():
                raise ValueError("Indica la carpeta de fuentes asignada para crear las categorías.")
            for category in CATEGORIES:
                target = f"{area}/{category}"
                _space(target, config)
                dest = _safe_path(root, target)
                if dest.is_dir():
                    continue
                ops.append({"destination": target, "kind": "mkdir", "category": category, "issue": "Destino ocupado" if dest.exists() else None})
        else:
            if not isinstance(moves, (list, tuple)) or not moves:
                raise ValueError("Indica las unidades y destinos que deseas proponer.")
            for move in moves:
                mid = move["material_id"]
                record = records.get(mid, {})
                source = record.get("path")
                if not source:
                    raise ValueError(f"El identificador carece de ubicación actual: {mid}")
                target = _relative(move["destination"])
                if mode == "promote" and source == target and record.get("origin") == "ai" and record.get("consolidation") == "consolidated":
                    continue
                src, dst = _validate_pair(root, config, source, target, mode == "promote")
                if record.get("origin") != "ai" and mode == "promote":
                    raise ValueError("La promoción requiere procedencia IA registrada.")
                known = {Path(row["path"]).relative_to(source): row for row in records.values()
                         if row.get("path") and _within(row["path"], source)}
                if mode == "promote" and any(row["origin"] != "ai" for row in known.values()):
                    raise ValueError("La unidad mezcla procedencias. Revisa qué materiales deseas consolidar.")
                witness = _witness(src, known=known)
                ops.append({"source": source, "destination": target, "material_id": mid, "kind": mode,
                            "content_version": record["content_version"], "witness": witness,
                            "issue": "Destino ocupado" if dst.exists() else None})
        _validate_overlaps(ops)
        for i, op in enumerate(ops, 1):
            op.update(operation_id=f"op-{i}", status="proposed")
        if not ops:
            return {"status": "unchanged", "operations": [], "summary": _summary([])}
        pid = str(uuid4())
        plan = {"plan_id": pid, "mode": mode, "operations": ops, "summary": _summary(ops)}
        tx.data.setdefault("organization_plans", {})[pid] = plan
        tx.event("plan", plan_id=pid, mode=mode, operations=len(ops))
        return plan


def _relocate(root, records, op):
    old, new = op["source"], op["destination"]
    changes = []
    for mid, record in records.items():
        path = record.get("path")
        if not path or not _within(path, old):
            continue
        destination = new + path[len(old):]
        record["path"] = destination
        if op["kind"] == "promote":
            record["consolidation"] = "consolidated"
            record["state"] = "reference"
            record["processing"] = "needs_review"
        if (root / destination).exists():
            refresh_stat(record, root / destination)
        changes.append({"material_id": mid, "old_path": path, "new_path": destination,
                        "content_version": record["content_version"], "promoted": op["kind"] == "promote"})
    by_path = {r["path"]: mid for mid, r in records.items() if r.get("path")}
    records[op["material_id"]]["physical_parent_id"] = by_path.get(Path(new).parent.as_posix())
    return changes


def _index_folders(tx, root, config, relative):
    """Registrar los padres del destino por orden sin inventar una agrupación del material movido."""
    by_path = {r.get("path"): mid for mid, r in tx.data["materials"].items() if r.get("path")}
    for role in ("sources", "generated"):
        for area in config["spaces"][role]:
            if not _within(relative, area):
                continue
            directory = Path(relative)
            chain = list(reversed(directory.parents)) + [directory]
            for item in chain:
                name = item.as_posix()
                if _within(name, area) and name not in by_path:
                    row = add_path(tx, root, name, origin="teacher" if role == "sources" else "ai")
                    by_path[name] = row["material_id"]
            return


def _apply_one(tx, root, config, plan, op):
    key = {"plan_id": plan["plan_id"], "operation_id": op["operation_id"]}
    destination = op["destination"]
    if op["kind"] == "mkdir":
        _space(destination, config)
        dest = _safe_path(root, _relative(destination))
        if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):
            raise ValueError("El destino ya contiene materiales. Revisa la propuesta de carpeta vacía.")
        tx.event("mkdir_intent", **key, path=destination)
        tx.flush()
        dest.mkdir(exist_ok=True)
        _index_folders(tx, root, config, destination)
        row = next(r for r in tx.data["materials"].values() if r.get("path") == destination)
        row["classification"] = {"primary": op["category"], "secondary": [], "mode": "confirmed",
                                 "confidence": 1.0, "evidence": "Carpeta de categoría aceptada por el docente."}
        op["changes"] = []
    else:
        src, dest = _validate_pair(root, config, op["source"], destination, op["kind"] == "promote")
        row = tx.data["materials"][op["material_id"]]
        if (row.get("path") != op["source"] or row["content_version"] != op["content_version"]
                or row["presence"] != "present"):
            raise ValueError("La ubicación o versión del catálogo cambió. Revisa esta operación.")
        resume_at_dest = op["status"] == "moving" and not src.exists() and dest.exists()
        if not resume_at_dest and dest.exists():
            raise ValueError("El destino está ocupado; no se sobrescribe.")
        location = dest if resume_at_dest else src
        if not location.exists() or _witness(location) != op["witness"]:
            raise ValueError("Cambió la identidad o el contenido. Revisa esta operación antes de continuar.")
        if not resume_at_dest:
            op["status"] = "moving"
            tx.event("move_intent", **key, before=op["source"], after=destination)
            tx.flush()
            dest.parent.mkdir(parents=True, exist_ok=True)
            _rename_new(src, dest)
        _index_folders(tx, root, config, dest.parent.relative_to(root).as_posix())
        op["changes"] = _relocate(root, tx.data["materials"], op)
    op.update(status="applied", issue=None)
    tx.event("promote" if op["kind"] == "promote" else "organization_applied", **key,
             before=op.get("source"), after=destination, changes=op["changes"])
    tx.flush()


def apply_organization(root, plan_id, *, accepted=None, changes=None):
    """Aplicar las operaciones nombradas y recuperar renombres interrumpidos del mismo plan."""
    root = _root(root)
    config = load_project(root)
    config = {**config, "sources": corpus_policy(root, config)}
    with transaction(root) as tx:
        plan = tx.data.get("organization_plans", {}).get(plan_id)
        if plan is None:
            raise ValueError("Plan desconocido.")
        all_ops = {op["operation_id"]: op for op in plan["operations"]}
        if accepted == "all":
            selected = list(all_ops)
        elif isinstance(accepted, list) and all(isinstance(item, str) for item in accepted):
            selected = list(dict.fromkeys(accepted))
        else:
            raise ValueError("Indica 'all' o la lista de operaciones aceptadas expresamente.")
        if set(selected) - all_ops.keys():
            raise ValueError("Hay operaciones fuera del plan.")
        if changes is None:
            changes = {}
        if not isinstance(changes, dict) or changes.keys() - set(selected):
            raise ValueError("Las excepciones deben corresponder a operaciones seleccionadas.")
        operations = [all_ops[key] for key in selected]
        for op in operations:
            key = op["operation_id"]
            if key in changes:
                new = _relative(changes[key])
                if op["status"] != "proposed":
                    if new != op["destination"]:
                        raise ValueError("Una operación iniciada conserva su destino.")
                elif op["kind"] == "mkdir":
                    if Path(new).parent != Path(op["destination"]).parent:
                        raise ValueError("La categoría debe quedar dentro de la carpeta de fuentes seleccionada.")
                    _space(new, config)
                    _safe_path(root, new)
                    op["destination"] = new
                else:
                    _validate_pair(root, config, op["source"], new, op["kind"] == "promote")
                    op["destination"] = new
        _validate_overlaps(operations)
        blocked, completed = [], []
        for op in operations:
            if op["status"] != "applied":
                try:
                    _apply_one(tx, root, config, plan, op)
                except (OSError, ValueError) as exc:
                    # Un fallo tras un rename deja la intención para reanudar de forma inequívoca.
                    if op["status"] == "moving" and not (root / op["source"]).exists():
                        # Después del renombre se conserva el último checkpoint completo.
                        # No confirmar filas de catálogo actualizadas parcialmente.
                        raise
                    op["issue"] = str(exc)
                    if op["status"] == "applied" or (tx.directory / "transaccion_catalogo.json").exists():
                        raise
                    if op["status"] == "moving":
                        src, dst = root / op["source"], root / op["destination"]
                        if not dst.exists() or (not src.samefile(dst) and _witness(src) == op["witness"]):
                            op["status"] = "proposed"
                    blocked.append({"operation_id": op["operation_id"], "reason": str(exc)})
                    tx.event("organization_blocked", plan_id=plan_id, operation_id=op["operation_id"], reason=str(exc))
                    tx.flush()
                    continue
            completed.extend(op.get("changes", []))
        return {"status": "needs_review" if blocked else "ok", "plan_id": plan_id,
                "applied": [op["operation_id"] for op in operations if op["status"] == "applied"],
                "issues": blocked, "changes": completed}
