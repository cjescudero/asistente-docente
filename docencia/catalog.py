"""Inventario lógico portable del curso. El historial registra metadatos, nunca entregas."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
import tempfile
import uuid
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from .project import MANAGEMENT_DIR, MANAGEMENT_NAMES, management_dir, _relative, _root, _safe_path, _within_relative, load_project
from .spaces import corpus_policy, under as _under, reserved

MANAGEMENT = MANAGEMENT_DIR
CATALOG = "catalogo_materiales.json"
HISTORY = "historial_operaciones.jsonl"
PENDING_TX = "transaccion_catalogo.json"
CATEGORIES = ("Organización", "Teoría", "Práctica", "Actividades y proyectos",
              "Evaluaciones", "Recursos", "Soluciones y feedback")
SKIP = {*MANAGEMENT_NAMES, "_datos_internos", "_datos_internos_proyecto", "node_modules",
        "venv", "__pycache__", ".gitkeep", ".DS_Store"}
# Señales de contenido explícitas. Un nombre o una extensión por sí solos
# no justifican una clasificación. El agente puede aportar evidencias adicionales.
HEADINGS = {
    "guía docente": "Organización", "programa de la asignatura": "Organización",
    "apuntes de teoría": "Teoría", "fundamentos teóricos": "Teoría",
    "práctica de laboratorio": "Práctica", "guion de prácticas": "Práctica",
    "proyecto de curso": "Actividades y proyectos", "estudio de caso": "Actividades y proyectos",
    "cuestionario de evaluación": "Evaluaciones", "rúbrica de evaluación": "Evaluaciones",
    "bibliografía complementaria": "Recursos", "recursos de aprendizaje": "Recursos",
    "solucionario": "Soluciones y feedback", "solución orientativa": "Soluciones y feedback",
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _empty():
    return {"schema_version": 1, "revision": 0, "materials": {}}


def _atomic(path, data):
    fd, name = tempfile.mkstemp(prefix=".catalogo-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _versioned(path):
    data = json.loads(path.read_bytes())
    if data.get("schema_version") != 1 or not isinstance(data.get("materials"), dict):
        raise ValueError("Versión o estructura no reconocida en el catálogo.")
    return data


@contextmanager
def _writer(root):
    directory = _safe_path(root, management_dir(root))
    directory.mkdir(exist_ok=True)
    for filename in (CATALOG, HISTORY, PENDING_TX, "catalogo.lock"):
        path = _safe_path(root, f"{management_dir(root)}/{filename}")
        if path.exists() and not path.is_file():
            raise ValueError(f"Control de catálogo inválido: {filename}")
    # El sistema operativo libera el bloqueo si el proceso termina.
    with (directory / "catalogo.lock").open("a+b") as f:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError("El catálogo está ocupado; reintenta la operación.") from exc
        else:
            import fcntl
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError("El catálogo está ocupado; reintenta la operación.") from exc
        yield directory


def _recover(directory):
    intent = directory / PENDING_TX
    if not intent.exists():
        return
    entry = json.loads(intent.read_bytes())
    target = directory / CATALOG
    observed = _versioned(target)["revision"] if target.exists() else 0
    if observed not in (entry["before_revision"], entry["after"]["revision"]):
        raise ValueError("Conflicto de revisión al recuperar el catálogo.")
    if observed == entry["before_revision"]:
        _atomic(target, _bytes(entry["after"]))
    payload = _bytes(entry["event"])
    with (directory / HISTORY).open("a+b") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() < entry["offset"]:
            raise ValueError("Historial incompleto; recuperar antes de continuar.")
        f.seek(entry["offset"])
        tail = f.read(len(payload) + 1)
        if not payload.startswith(tail):
            raise ValueError("Conflicto de historial al recuperar el catálogo.")
        if tail != payload:
            f.write(payload[len(tail):])
            f.flush()
            os.fsync(f.fileno())
    intent.unlink()


class CatalogTransaction:
    def __init__(self, directory):
        self.directory = directory
        path = directory / CATALOG
        self.data = _versioned(path) if path.exists() else _empty()
        self.original = copy.deepcopy(self.data)
        self.events = []

    def event(self, kind, **details):
        self.events.append({"kind": kind, **details})

    def flush(self):
        if self.original == self.data and not self.events:
            return
        revision = self.original["revision"]
        self.data["revision"] = revision + 1
        before, after = self.original["materials"], self.data["materials"]
        changes = {}
        for key in before.keys() | after.keys():
            if before.get(key) != after.get(key):
                changes[key] = {"before": before.get(key), "after": after.get(key)}
        event = {"operation_id": str(uuid.uuid4()), "time": _now(), "revision": revision + 1,
                 "operations": self.events, "materials": changes}
        history = self.directory / HISTORY
        _atomic(self.directory / PENDING_TX, _bytes({
            "before_revision": revision, "after": self.data, "event": event,
            "offset": history.stat().st_size if history.exists() else 0}))
        _recover(self.directory)
        self.original = copy.deepcopy(self.data)
        self.events.clear()


@contextmanager
def transaction(root):
    root = _root(root)
    if load_project(root).get("structure") != "curso-v4":
        raise ValueError("El catálogo requiere un proyecto curso-v4.")
    with _writer(root) as directory:
        _recover(directory)
        tx = CatalogTransaction(directory)
        yield tx
        tx.flush()


def read_catalog(root):
    root = _root(root)
    if load_project(root).get("structure") != "curso-v4":
        raise ValueError("El catálogo requiere un proyecto curso-v4.")
    path = _safe_path(root, f"{management_dir(root)}/{CATALOG}")
    if _safe_path(root, f"{management_dir(root)}/{PENDING_TX}").exists():
        with _writer(root) as directory:
            _recover(directory)
    return _versioned(path) if path.exists() else _empty()


def _classification():
    return {"primary": None, "secondary": [], "mode": "pending", "evidence": "", "confidence": None}


def _new(kind, origin, parent, relative=None):
    return {"material_id": str(uuid.uuid4()), "path": relative, "kind": kind, "origin": origin,
            "physical_parent_id": parent, "logical_parent_id": parent, "relations": [],
            "state": "draft" if origin == "ai" else "reference", "access": "docente", "access_confirmed": False,
            "consolidation": "pending" if origin == "ai" else "consolidated",
            "presence": "present", "processing": "inventoried", "content_version": 1,
            "sha256": None, "added_at": _now(), "classification": _classification()}


def _stat_fields(st):
    return {"physical_id": {"dev": st.st_dev, "ino": st.st_ino}, "size": st.st_size,
            "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
            "birthtime_ns": getattr(st, "st_birthtime_ns", None),
            "modified_at": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()}


def refresh_stat(record, path):
    record.update(_stat_fields(Path(path).lstat()))
    record["presence"] = "present"


def _digest(path):
    initial_path = path.lstat()
    with path.open("rb") as f:
        st = os.fstat(f.fileno())
        if not stat.S_ISREG(initial_path.st_mode) or not stat.S_ISREG(st.st_mode):
            raise ValueError("El material no es un archivo regular.")
        h = hashlib.sha256()
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
        # En Windows lstat y fstat pueden expresar las fechas con distinta precisión.
        # Comparar cada observación con la misma API y comprobar la identidad por separado.
        if (not os.path.samestat(initial_path, st)
                or _stat_fields(path.lstat()) != _stat_fields(initial_path)
                or _stat_fields(os.fstat(f.fileno())) != _stat_fields(st)):
            raise ValueError(f"El archivo cambió durante la lectura: {path.name}")
    return h.hexdigest()


def _infer(path):
    result = _classification()
    if path.suffix.lower() not in {".txt", ".md"}:
        return result
    try:
        with path.open("rb") as f:
            heading = f.readline(1024).decode("utf-8-sig").strip().lstrip("# ").casefold()
    except (UnicodeError, OSError):
        return result
    for signal, category in HEADINGS.items():
        if heading == signal or heading.startswith((signal + ":", signal + " ")):
            return {"primary": category, "secondary": [], "mode": "direct", "confidence": 0.85,
                    "evidence": "Encabezado del documento: " + signal, "inferred": True}
    return result


def add_path(tx, root, relative, *, origin, parent_id=None):
    relative = _relative(str(relative))
    path = _safe_path(root, relative)
    rows = tx.data["materials"]
    if any(r.get("path") == relative for r in rows.values()):
        raise ValueError(f"Ya existe un registro para {relative}.")
    if parent_id is None:
        parent = str(PurePosixPath(relative).parent)
        parent_id = next((i for i, r in rows.items() if r.get("path") == parent), None)
    st = path.lstat()
    if unreadable_entry(st) or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
        raise ValueError(f"Tipo de material no admitido o sin acceso local: {relative}")
    row = _new("folder" if stat.S_ISDIR(st.st_mode) else "file", origin, parent_id, relative)
    row.update(_stat_fields(st))
    if row["kind"] == "file":
        row["sha256"] = _digest(path)
        row["classification"] = _infer(path)
    rows[row["material_id"]] = row
    return row


def _selection(config, scope):
    spaces = config["spaces"]
    roots = {p: origin for role, origin in (("sources", "teacher"), ("generated", "ai"))
             for p in spaces[role]}
    excluded = [*spaces["submissions"], *MANAGEMENT_NAMES, "_datos_internos_proyecto",
                *config.get("sources", {}).get("exclude", [])]
    if config.get("map"):
        excluded.append(config["map"])
    if scope is None:
        return roots, excluded
    requested = [scope] if isinstance(scope, str) else scope
    selected = {}
    for path in requested:
        p = _relative(path)
        origin = next((v for key, v in roots.items() if _within_relative(p, key)), None)
        if origin is None or any(_under(p, x) for x in excluded) or any(x in SKIP or x.startswith(".") for x in PurePosixPath(p).parts):
            raise ValueError("El ámbito solicitado queda fuera de los espacios inventariables.")
        selected[p] = origin
    return selected, excluded


def unreadable_entry(st):
    """Evitar descargar contenido remoto o leer un archivo con otros nombres desconocidos."""
    return (stat.S_ISREG(st.st_mode) and st.st_nlink > 1
            or bool(getattr(st, "st_flags", 0) & getattr(stat, "SF_DATALESS", 0x40000000))
            or bool(getattr(st, "st_file_attributes", 0) & (0x1000 | 0x400000)))


def _scan(root, roots, excluded, spaces):
    entries, unavailable = {}, []
    def scan(relative, origin, *, descend=True):
        path = root / relative
        if relative in entries or any(_under(relative, x) for x in excluded):
            return
        if path.name.startswith(".") or path.name in SKIP or reserved(relative):
            return
        try:
            st = path.lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(path, "is_junction", lambda: False)():
                return
            if not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):
                return
            if unreadable_entry(st):
                unavailable.append(relative)
                return
            entries[relative] = (origin, "folder" if stat.S_ISDIR(st.st_mode) else "file", _stat_fields(st))
            if descend and stat.S_ISDIR(st.st_mode):
                for child in sorted(path.iterdir()):
                    scan(relative + "/" + child.name, origin)
        except FileNotFoundError:
            pass
        except (PermissionError, OSError):
            unavailable.append(relative)
    for relative, origin in roots.items():
        _safe_path(root, relative)
        scan(relative, origin)
    # Un ámbito parcial incorpora los antecesores necesarios para registrar sus
    # unidades, sin abrir documentos ni recorrer las carpetas hermanas.
    for relative, origin in roots.items():
        for parent in PurePosixPath(relative).parents:
            name = parent.as_posix()
            if not any(_within_relative(name, base) for base in spaces):
                break
            scan(name, origin, descend=False)
    return entries, unavailable


def _physical(fields):
    fid = fields.get("physical_id") or {}
    return (fid.get("dev"), fid.get("ino")) if fid.get("ino") else None


def _inherit(rows):
    # Una unidad homogénea se infiere de evidencias del contenido de sus hijos
    # lógicos. Las raíces físicas pueden agrupar todo un curso y quedan pendientes.
    children = defaultdict(list)
    for row in rows.values():
        parent = row.get("logical_parent_id")
        if parent:
            children[parent].append(row)
    inferred = set()
    def summarize(key, visiting):
        if key in inferred:
            return
        if key in visiting:
            raise ValueError("Ciclo en las agrupaciones lógicas.")
        members = children[key]
        for child in members:
            summarize(child["material_id"], visiting | {key})
        row = rows[key]
        c = row["classification"]
        if row["kind"] == "folder" and row.get("logical_parent_id") and (
                c["mode"] in ("pending", "inherited") or c.get("basis") == "children"):
            primary = {m["classification"]["primary"] if m["classification"]["mode"] in
                       ("direct", "confirmed") else None for m in members}
            if len(primary) == 1 and None not in primary:
                row["classification"] = {"primary": primary.pop(), "secondary": [], "mode": "direct",
                                         "evidence": "Contenido homogéneo de la unidad lógica.",
                                         "confidence": 0.8, "basis": "children"}
            elif c.get("basis") == "children":
                row["classification"] = _classification()
        inferred.add(key)
    for key in rows:
        summarize(key, set())
    # Las decisiones directas y confirmadas prevalecen sobre cualquier ancestro.
    done = set()
    def resolve(key, visiting):
        if key in done:
            return
        if key in visiting:
            raise ValueError("Ciclo en las agrupaciones lógicas.")
        record = rows[key]
        parent_id = record.get("logical_parent_id")
        if parent_id is not None:
            resolve(parent_id, visiting | {key})
        c = record["classification"]
        if c["mode"] in ("pending", "inherited"):
            ancestor = rows[parent_id]["classification"] if parent_id else None
            if ancestor and ancestor["primary"]:
                record["classification"] = {**ancestor, "mode": "inherited", "from": parent_id}
            else:
                record["classification"] = _classification()
        done.add(key)
    for key in rows:
        resolve(key, set())


def classify(root, material_id, *, primary, secondary=None, confirmed=True, evidence="", confidence=None, access=None):
    if access is not None and (not confirmed or access not in ("estudiante", "docente")):
        raise ValueError("Confirmar el acceso docente o estudiante para el material.")
    secondary = list(secondary or [])
    if primary not in CATEGORIES or any(x not in CATEGORIES or x == primary for x in secondary):
        raise ValueError("Categoría desconocida o repetida como principal y secundaria.")
    if confidence is not None and not (0 <= confidence <= 1):
        raise ValueError("Confianza fuera de [0, 1].")
    if not confirmed and not evidence.strip():
        raise ValueError("Una clasificación inferida requiere evidencia.")
    with transaction(root) as tx:
        row = tx.data["materials"][material_id]
        if row["classification"]["mode"] == "confirmed" and not confirmed:
            raise ValueError("La decisión confirmada del docente tiene prioridad.")
        if access is not None:
            row.update(access=access, access_confirmed=True)
        row["classification"] = {"primary": primary, "secondary": list(dict.fromkeys(secondary)),
                                 "mode": "confirmed" if confirmed else "direct",
                                 "evidence": evidence, "confidence": confidence}
        _inherit(tx.data["materials"])
        if tx.original != tx.data:
            tx.event("classification", material_id=material_id)
    return row


def create_group(root, title, *, parent_id=None):
    if not title.strip():
        raise ValueError("Se requiere un nombre para la agrupación.")
    with transaction(root) as tx:
        rows = tx.data["materials"]
        if parent_id and (parent_id not in rows or rows[parent_id]["kind"] == "file"):
            raise ValueError("Padre lógico no válido.")
        row = _new("group", "teacher", None)
        row.update(title=title, logical_parent_id=parent_id)
        rows[row["material_id"]] = row
        _inherit(rows)
        tx.event("create_group", material_id=row["material_id"])
    return row


def regroup(root, material_id, parent_id):
    with transaction(root) as tx:
        rows = tx.data["materials"]
        if parent_id is not None and (parent_id not in rows or rows[parent_id]["kind"] == "file"):
            raise ValueError("Padre lógico no válido.")
        rows[material_id]["logical_parent_id"] = parent_id
        _inherit(rows)
        if tx.original != tx.data:
            tx.event("regroup", material_id=material_id)
    return rows[material_id]


def _stable_metadata(old, new):
    return all(old.get(k) == new.get(k) for k in ("size", "mtime_ns"))


def reconcile(root, *, scope=None):
    """Inventariar los espacios indicados. Nunca identificar una copia solo por su ruta."""
    root = _root(root)
    report = {"status": "ok", "created": [], "modified": [], "moves": [], "pending": []}
    with transaction(root) as tx:
        if any(op.get("status", op.get("state")) == "moving"
               for plan in tx.data.get("organization_plans", {}).values()
               for op in plan.get("operations", [])):
            raise ValueError("Hay un movimiento interrumpido. Reanuda el plan antes de reconciliar.")
        config = load_project(root)
        policy = corpus_policy(root, config, refresh=True)
        config = {**config, "sources": policy}
        report["pending"].extend({"path": path, "material_id": None, "reason": "corpus_policy", "candidates": []}
                                 for path in policy["review"])
        roots, excluded = _selection(config, scope)
        entries, unavailable = _scan(root, roots, excluded, config["spaces"]["sources"] + config["spaces"]["generated"])
        rows = tx.data["materials"]
        questions = tx.data.setdefault("identity_questions", {})
        known = {row["path"]: key for key, row in rows.items() if row.get("path")}
        initial = set(known.values())
        physical = defaultdict(list)
        observed = defaultdict(list)
        for key in initial:
            physical[_physical(rows[key])].append(key)
        for path, (_, _, fields) in entries.items():
            observed[_physical(fields)].append(path)
        assigned = {}
        ambiguous = {}
        used = set()
        digest_cache = {}
        def digest(path):
            if path not in digest_cache:
                digest_cache[path] = _digest(root / path)
            return digest_cache[path]
        def assign(path, key):
            assigned[path] = key
            used.add(key)
        # Primero las identidades que siguen en su ruta. Después los traslados
        # reconocibles por volumen e inode, incluidos intercambios de nombres.
        for path, (_, kind, fields) in entries.items():
            token = _physical(fields)
            candidates = physical[token]
            key = known.get(path)
            if not token:
                continue
            same = key in candidates
            if not same:
                if len(candidates) != 1 or len(observed[token]) != 1:
                    continue
                key = candidates[0]
                prior = root / rows[key]["path"]
                if rows[key]["path"] not in entries and prior.exists():
                    continue  # enlace duro u otro nombre fuera de este ámbito
            row = rows[key]
            if row["kind"] != kind or row.get("birthtime_ns") != fields["birthtime_ns"]:
                continue
            if not same and not fields["birthtime_ns"] and not _stable_metadata(row, fields) and kind == "file":
                ambiguous[path] = [key]
                continue  # el SO puede haber reutilizado el inode
            assign(path, key)
        # La huella solo identifica un traslado si hay una relación uno a uno
        # con un registro desaparecido, incluso en una consulta de ámbito parcial.
        hashes = defaultdict(list)
        missing_sizes = set()
        for key in initial - used:
            row = rows[key]
            if row["kind"] != "file" or not row.get("sha256"):
                continue
            old_path = row["path"]
            if any(_under(old_path, x) for x in excluded + unavailable):
                continue
            if old_path not in entries:
                try:
                    (root / old_path).lstat()
                except FileNotFoundError:
                    pass
                except OSError:
                    continue
                else:
                    continue
            hashes[row["sha256"]].append(key)
            missing_sizes.add(row.get("size"))
        new_hashes = defaultdict(list)
        for path, (_, kind, fields) in entries.items():
            if path in assigned or kind != "file":
                continue
            if fields["size"] in missing_sizes:
                try:
                    new_hashes[digest(path)].append(path)
                except (OSError, ValueError):
                    unavailable.append(path)
        for fingerprint, paths in new_hashes.items():
            matches = hashes[fingerprint]
            if len(matches) == 1 and len(paths) == 1:
                assign(paths[0], matches[0])
            elif matches:
                ambiguous.update({path: matches for path in paths})

        # Un traslado entre volúmenes puede cambiar todos los inodes. Una unidad
        # física desaparecida se reconoce por el conjunto completo de sus hijos
        # identificados, nunca por el nombre de la carpeta ni por una muestra.
        old_children, new_children = defaultdict(set), defaultdict(set)
        for key in initial:
            row = rows[key]
            if row.get("presence") == "present" and row.get("physical_parent_id"):
                old_children[row["physical_parent_id"]].add(key)
        for path in entries:
            new_children[str(PurePosixPath(path).parent)].add(path)
        for path in sorted(new_children, key=lambda name: -name.count("/")):
            if path in assigned or path not in entries or entries[path][1] != "folder":
                continue
            children = {assigned.get(child) for child in new_children[path]}
            if None in children:
                continue
            candidates = {rows[k].get("physical_parent_id") for k in children}
            if len(candidates) != 1:
                continue
            candidate = candidates.pop()
            if (candidate and candidate not in used and old_children[candidate] == children
                    and rows[candidate].get("path") and not (root / rows[candidate]["path"]).exists()):
                assign(path, candidate)

        # Incorporar primero las carpetas para asignar la unidad lógica inicial.
        # La ubicación de un material existente nunca modifica esa unidad.
        for path in sorted(entries, key=lambda p: (p.count("/"), p)):
            if any(_under(path, x) for x in unavailable):
                continue
            origin, kind, fields = entries[path]
            key = assigned.get(path)
            if key is None:
                candidates = ambiguous.get(path, []).copy()
                if known.get(path) in initial and known[path] not in used:
                    candidates = list(dict.fromkeys(candidates + [known[path]]))
                if candidates:
                    questions[path] = {"path": path, "reason": "identity", "candidates": sorted(candidates),
                                       "material_id": None, "stat": fields}
                    report["pending"].append(questions[path].copy())
                    continue
            physical_parent = str(PurePosixPath(path).parent)
            parent_id = assigned.get(physical_parent, known.get(physical_parent))
            if key is None:
                row = _new(kind, origin, parent_id, path)
                key = row["material_id"]
            else:
                row = rows[key]
            is_new = key not in rows
            changed = (is_new or not _stable_metadata(row, fields) or _physical(row) != _physical(fields)
                       or (path == row["path"] and row.get("ctime_ns") != fields["ctime_ns"]))
            new_hash = None
            if changed and kind == "file":
                try:
                    new_hash = digest(path)
                except (OSError, ValueError):
                    unavailable.append(path)
                    continue
            if is_new:
                rows[key] = row
                report["created"].append(key)
                assign(path, key)
            elif path != row["path"]:
                report["moves"].append({"material_id": key, "before": row["path"], "after": path})
            if new_hash and row["sha256"] != new_hash:
                if not is_new:
                    report["modified"].append(key)
                    row["content_version"] += 1
                    row["processing"] = "needs_review"
                row["sha256"] = new_hash
                if row["classification"]["mode"] in ("pending", "inherited") or row["classification"].get("inferred"):
                    row["classification"] = _infer(root / path)
            row.update(fields, path=path, physical_parent_id=parent_id, presence="present")
            questions.pop(path, None)
        for key in initial:
            row = rows[key]
            path = row["path"]
            if any(_under(path, x) for x in excluded):
                continue
            blocked = any(_under(path, x) for x in unavailable)
            uncertain = path in questions
            if blocked or uncertain or (path not in entries and any(_under(path, x) for x in roots)):
                row["presence"] = "inaccessible" if blocked else ("ambiguous" if uncertain else "missing")
                report["pending"].append({"path": path, "material_id": key, "reason": row["presence"],
                                          "candidates": []})
        for path in set(unavailable) - known.keys():
            report["pending"].append({"path": path, "material_id": None, "reason": "inaccessible", "candidates": []})
        for path in list(questions):
            if (path not in entries and any(_within_relative(path, r) for r in roots)
                    and not any(_under(path, u) for u in unavailable)):
                questions.pop(path)
        _inherit(rows)
        incidents = tx.data.setdefault("incidents", {})
        prior = dict(incidents)
        observed_incidents = {item["path"] for item in report["pending"]}
        for path in list(incidents):
            if path in observed_incidents or any(_within_relative(path, base) for base in roots):
                del incidents[path]
        for item in report["pending"]:
            key = item["path"]
            details = {k: item[k] for k in ("reason", "material_id", "candidates")}
            incidents.setdefault(key, []).append(details)
        if tx.original != tx.data:
            tx.event("reconcile", scope=list(roots), moves=report["moves"], created=report["created"],
                     modified=report["modified"], incidents={k: v for k, v in incidents.items() if prior.get(k) != v},
                     resolved=sorted(prior.keys() - incidents.keys()))
        tx.flush()
        report["revision"] = tx.data["revision"]
    return report


def resolve_identity(root, path, *, material_id=None):
    """Resolver una coincidencia ambigua explícitamente como traslado o incorporación."""
    root = _root(root)
    relative = _relative(path)
    config = load_project(root)
    selected, _ = _selection({**config, "sources": corpus_policy(root, config)}, relative)
    with transaction(root) as tx:
        questions = tx.data.get("identity_questions", {})
        dispute = questions.get(relative)
        if not dispute:
            raise ValueError("La ruta no tiene una identidad pendiente.")
        target = _safe_path(root, relative)
        if _stat_fields(target.lstat()) != dispute["stat"]:
            raise ValueError("La ruta ha cambiado. Reconcilia el ámbito antes de decidir.")
        rows = tx.data["materials"]
        if material_id is not None and material_id not in dispute["candidates"]:
            raise ValueError("El material indicado no es un candidato pendiente.")
        old = next((r for r in rows.values() if r.get("path") == relative), None)
        if old and old["material_id"] != material_id:
            old.update(last_path=relative, path=None, presence="missing")
        if material_id is None:
            row = add_path(tx, root, relative, origin=selected[relative])
        else:
            row = rows[material_id]
            if row.get("path") and row["path"] != relative and (root / row["path"]).exists():
                raise ValueError("El original sigue presente. Revisa la posible copia.")
            if row["kind"] != ("folder" if target.is_dir() else "file"):
                raise ValueError("Los tipos físicos del material y el candidato no coinciden.")
            if row["kind"] == "file":
                sha = _digest(target)
                if row["sha256"] != sha:
                    row.update(sha256=sha, content_version=row["content_version"] + 1, processing="needs_review")
            parent = str(PurePosixPath(relative).parent)
            row.update(path=relative, physical_parent_id=next(
                (k for k, r in rows.items() if r.get("path") == parent), None))
            refresh_stat(row, target)
        questions.pop(relative)
        _inherit(rows)
        tx.event("resolve_identity", path=relative, material_id=row["material_id"])
    return row
