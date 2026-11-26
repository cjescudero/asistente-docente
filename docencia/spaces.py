"""Espacios configurables e incorporación voluntaria de cursos, sin mover documentos."""
from __future__ import annotations

import copy
import json
import os
import stat
import unicodedata
from functools import lru_cache
from pathlib import PurePosixPath

from . import project as p

RESERVED = frozenset({".agents", ".git", ".venv", "venv", "__pycache__", "node_modules",
                      ".pytest_cache", ".codex", ".claude", p.INTERNAL_PROJECT_DIR,
                      p.INTERNAL_MATERIAL_DIR, *p.MANAGEMENT_NAMES})


def key(value):
    """Comparación conservadora en volúmenes con distinta normalización o uso de mayúsculas."""
    return unicodedata.normalize("NFC", value).casefold()


def under(relative, parent):
    return p._within_relative(key(relative), key(parent))


def reserved(relative):
    blocked = {key(part) for part in RESERVED}
    return any(key(part) in blocked for part in PurePosixPath(relative).parts)


def defaults():
    return {"schema_version": 1, "structure": "curso-v4", "spaces": copy.deepcopy(p.DEFAULT_SPACES),
            "sources": {"selected": False, "include": [], "exclude": []}, "map": None}


def validate_config(root, data):
    result = copy.deepcopy(data)
    spaces = result.get("spaces")
    required = set(p.DEFAULT_SPACES)
    if not isinstance(spaces, dict) or not required <= spaces.keys() <= required | {"notes"}:
        raise ValueError("spaces requiere sources, generated y submissions; notes es opcional.")
    roots = []
    for role, values in spaces.items():
        paths = p._paths(values, role)
        if not paths:
            raise ValueError(f"Elegir al menos una carpeta para el espacio {role}.")
        for relative in paths:
            if reserved(relative) or key(relative.split("/")[0]) in {"agents.md", "leeme.md", key(p.CONFIG_NAME)}:
                raise ValueError(f"Espacio reservado: {relative}")
            if any(under(relative, other) or under(other, relative) for other in roots):
                raise ValueError(f"Las raíces de los espacios deben ser independientes: {relative}")
            path = p._safe_path(root, relative)
            if path.exists() and not path.is_dir():
                raise ValueError(f"Colisión con un archivo: {relative}")
            roots.append(relative)
        spaces[role] = paths
    sources = result.get("sources")
    if not isinstance(sources, dict) or type(sources.get("selected")) is not bool:
        raise ValueError("La selección del corpus requiere sources.selected.")
    for field in ("include", "exclude"):
        sources[field] = p._paths(sources.get(field), f"sources.{field}")
        for relative in sources[field]:
            path = p._safe_path(root, relative)
            if field == "include" and (
                reserved(relative) or not any(p._within_relative(relative, r) for r in spaces["sources"])
                or (path.exists() and not path.is_dir())
            ):
                raise ValueError(f"Seleccionar solo carpetas del espacio de material de la asignatura: {relative}")
    bindings = result.get("source_bindings", {})
    if not isinstance(bindings, dict) or set(bindings) - {"include", "exclude"}:
        raise ValueError("Identidades de selección del corpus no válidas.")
    for value in bindings.values():
        if not isinstance(value, dict):
            raise ValueError("Se esperaba un registro de identidades por ruta.")
        for name, token in value.items():
            if p._relative(name) != name:
                raise ValueError("Ruta de identidad no normalizada.")
            if (not isinstance(token, list) or len(token) != 4 or type(token[0]) is not int
                or type(token[1]) is not int or token[1] <= 0
                or not (token[2] is None or type(token[2]) is int) or token[3] not in ("file", "dir")):
                raise ValueError("Identificador físico de selección no válido.")
    if not sources["selected"] and (sources["include"] or sources["exclude"]):
        raise ValueError("La selección pendiente requiere listas vacías.")
    if "map" not in result:
        raise ValueError("Falta el estado de mapa del curso.")
    if result["map"] is not None:
        m = p._relative(result["map"])
        # Solo los mapas ya existentes procedentes de v3 pueden quedar fuera del espacio generado.
        legacy_map = result.get("adopted_from") == p.CONFIG_V3 and m == result.get("adopted_map")
        outside_map = spaces["sources"] + spaces["submissions"] + spaces.get("notes", [])
        if reserved(m) or any(under(m, r) or under(r, m) for r in outside_map):
            raise ValueError("La wiki no puede solaparse con las fuentes, las entregas ni las notas del curso.")
        if not legacy_map and not any(p._within_relative(m, r) and m != r for r in spaces["generated"]):
            raise ValueError("La wiki debe ubicarse dentro del espacio generado.")
        if not p._safe_path(root, m + "/index.md").is_file():
            raise ValueError("map requiere un índice real.")
        result["map"] = m
    return result


class CorpusPolicy(dict):
    """Instantánea de la política efectiva para una operación de lectura."""


def _source_domain(config, name):
    roles = config["spaces"]
    return any(under(name, base) for base in roles["sources"] + roles["generated"]) and not (
        reserved(name) or any(part.startswith(".") for part in PurePosixPath(name).parts)
        or (config.get("map") and under(name, config["map"])))


def _identity(path):
    st = path.lstat()
    if not st.st_ino or stat.S_ISLNK(st.st_mode) or getattr(path, "is_junction", lambda: False)():
        return None
    if stat.S_ISREG(st.st_mode) and st.st_nlink > 1:
        return None
    if not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
        return None
    if (getattr(st, "st_file_attributes", 0) & (0x1000 | 0x400000)
        or getattr(st, "st_flags", 0) & 0x40000000
        or getattr(st, "st_reparse_tag", 0) == getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", -1)):
        return None
    birth = getattr(st, "st_birthtime_ns", None)
    if birth is None and hasattr(st, "st_birthtime"):
        birth = int(st.st_birthtime * 1e9)
    return [st.st_dev, st.st_ino, birth, "dir" if stat.S_ISDIR(st.st_mode) else "file"]


def _observe(root, config, path, *, descend, found, unavailable):
    # Esta inspección registra metadatos físicos, nunca abre el contenido.
    if path in found or not _source_domain(config, path):
        return
    try:
        parent = PurePosixPath(path).parent.as_posix()
        parent_path = root if parent == "." else p._safe_path(root, parent)
        candidate = parent_path / PurePosixPath(path).name
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            return
        token = _identity(candidate)
        if token is None:
            unavailable.add(path)
            return
        found[path] = token
        if descend and token[-1] == "dir":
            with os.scandir(candidate) as entries:
                for entry in entries:
                    _observe(root, config, f"{path}/{entry.name}", descend=True,
                             found=found, unavailable=unavailable)
    except FileNotFoundError:
        pass
    except (ValueError, OSError):
        unavailable.add(path)


def _capture(root, config, field):
    found, unavailable = {}, set()
    for path in config["sources"][field]:
        _observe(root, config, path, descend=field == "exclude", found=found, unavailable=unavailable)
    if unavailable:
        raise ValueError("No se pudo verificar la selección: " + ", ".join(sorted(unavailable)))
    return found


def corpus_policy(root, config, *, refresh=False):
    """Resolver una selección por identidad física sin abrir material docente.

    La configuración conserva lo autorizado. Los cambios de ruta solo se siguen
    dentro de los espacios ya asignados. Una exclusión perdida bloquea las
    lecturas de esos espacios hasta recuperar su identidad o revisar la selección.
    refresh incorpora metadatos de nuevos descendientes excluidos al reconciliar.
    """
    sources = config["sources"]
    if config["structure"] != "curso-v4" or isinstance(sources, CorpusPolicy):
        return sources
    bindings = config.get("source_bindings", {})
    bound_in = bindings.get("include", {})
    bound_out = bindings.get("exclude", {})
    paths_to_check = set(bound_in) | set(bound_out)
    known, unavailable = {}, set()
    renamed = {}
    for name in paths_to_check:
        _observe(root, config, name, descend=False, found=known, unavailable=unavailable)
    missing = {name for name in paths_to_check if known.get(name) != (bound_out.get(name) or bound_in[name])}
    if missing:
        inventory = {}
        for name in config["spaces"]["sources"] + config["spaces"]["generated"]:
            _observe(root, config, name, descend=True, found=inventory, unavailable=unavailable)
        candidates = {}
        for name, token in inventory.items():
            candidates.setdefault(tuple(token), []).append(name)
        for name in missing:
            matches = candidates.get(tuple(bound_out.get(name) or bound_in[name]), [])
            if len(matches) == 1:
                renamed[name] = matches[0]
    include = []
    for name in sources["include"]:
        if name not in missing:
            include.append(name)
        elif name in renamed and any(p._within_relative(renamed[name], r) for r in config["spaces"]["sources"]):
            include.append(renamed[name])
    excluded = set(sources["exclude"])
    excluded.update(renamed[name] for name in renamed if name in bound_out)
    uncertain = [name for name in missing if name in bound_out and (name not in renamed or name in known)]
    review = sorted(set(uncertain) | {name for name in missing if name in bound_in and renamed.get(name) not in include})
    if refresh:
        # Incorporar archivos añadidos a una rama excluida (también si cambió
        # de nombre) antes de permitir que se trasladen fuera de ella.
        captured = {}
        for name in excluded:
            _observe(root, config, name, descend=True, found=captured, unavailable=unavailable)
        updated = copy.deepcopy(bindings)
        out = updated.setdefault("exclude", {})
        expected = {tuple(token) for token in out.values()}
        for name, token in captured.items():
            if name not in out and tuple(token) not in expected:
                out[name] = token
                expected.add(tuple(token))
        inc = updated.setdefault("include", {})
        for name in sources["include"]:
            if name not in inc:
                _observe(root, config, name, descend=False, found=inc, unavailable=unavailable)
        if updated != bindings and (out or inc):
            destination = p._safe_path(root, p.config_v4(root))
            with destination.open(encoding="utf-8") as handle:
                active = json.load(handle, object_pairs_hook=p._unique_json)
            if active.get("source_bindings", {}) != bindings or active["sources"] != sources:
                raise ValueError("Cambió la selección del corpus; repetir la reconciliación.")
            active["source_bindings"] = updated
            p._replace_config(destination, json.dumps(active, ensure_ascii=False, indent=2) + "\n")
    if uncertain or unavailable:
        # Una copia entre volúmenes o un cambio de permisos impide garantizar
        # el destino de los archivos excluidos sin inspeccionar su contenido.
        excluded.update(config["spaces"]["sources"] + config["spaces"]["generated"])
        review = sorted(set(review) | unavailable)
    return CorpusPolicy(selected=sources["selected"], include=include,
                        exclude=sorted(excluded), review=review)


@lru_cache(maxsize=8)
def _restricted_identities(root, signature):
    """Cargar una vez por sustitución atómica del catálogo."""
    from .catalog import read_catalog
    ledger = read_catalog(root)
    paths = {key(x) for x in ledger.get("identity_questions", {})}
    physical = set()
    for record in ledger["materials"].values():
        if record.get("presence") == "present" and (
            record.get("origin") == "teacher" or record.get("consolidation") == "consolidated"
        ):
            continue
        if record.get("path"):
            paths.add(key(record["path"]))
        token = record.get("physical_id") or {}
        if token.get("ino"):
            physical.add((token.get("dev"), token["ino"]))
    return paths, physical


def admitted_identity(root, candidate):
    """Consultar incluso el inode previo si se movió un borrador sin reconciliar."""
    from .catalog import CATALOG, PENDING_TX
    try:
        metadata = candidate.lstat()
    except FileNotFoundError:
        metadata = None
    if metadata and stat.S_ISREG(metadata.st_mode) and metadata.st_nlink > 1:
        # Los demás nombres podrían pertenecer al espacio privado de Entregas.
        return False
    catalog = p._safe_path(root, f"{p.management_dir(root)}/{CATALOG}")
    if p._safe_path(root, f"{p.management_dir(root)}/{PENDING_TX}").exists():
        return False
    try:
        metadata = catalog.stat()
    except FileNotFoundError:
        return True
    paths, physical = _restricted_identities(root, (metadata.st_dev, metadata.st_ino,
                                                   metadata.st_size, metadata.st_mtime_ns))
    if not paths and not physical:
        return True
    current = candidate
    while current != root:
        if key(current.relative_to(root).as_posix()) in paths:
            return False
        if physical:
            try:
                info = current.lstat()
            except FileNotFoundError:
                pass
            else:
                if (info.st_dev, info.st_ino) in physical:
                    return False
        current = current.parent
    return True


def resolve_space(root, role, destination=None, *, config=None):
    """Elegir un destino concreto en los espacios asignados al papel solicitado."""
    root = p._root(root)
    config = p.load_project(root) if config is None else config
    if config.get("structure") != "curso-v4" or role not in config["spaces"]:
        raise ValueError(f"El espacio solicitado debe estar asignado en curso-v4: {role}.")
    choices = config["spaces"][role]
    if destination is None:
        if len(choices) != 1:
            raise ValueError(f"Elige una de las carpetas para {role}: " + ", ".join(choices))
        destination = choices[0]
    destination = p._relative(destination)
    if reserved(destination) or not any(p._within_relative(destination, folder) for folder in choices):
        raise ValueError(f"El destino no pertenece al espacio {role}: {destination}")
    return p._safe_path(root, destination)


def instructions(config):
    roles = {"sources": "Material de la asignatura", "generated": "Material generado por IA",
             "submissions": "Entregas"}
    marker = p.COURSE_MARKER if config["spaces"] == p.DEFAULT_SPACES else "<!-- asistente-docente:espacios-configurados -->"
    lines = [p.START_MARKER, marker, "## Proyecto docente", ""]
    for role, label in roles.items():
        lines.append(f"- {label}: " + ", ".join(f"`{path}/`" for path in config["spaces"][role]) + ".")
    if "notes" in config["spaces"]:
        paths = ", ".join(f"`{path}/`" for path in config["spaces"]["notes"])
        lines.extend([f"- Notas del curso: {paths}.",
                      "", "Guardar aquí las ideas y la planificación que el docente desee editar. "
                      "Mantener estas notas fuera del catálogo docente, el mapa y las vistas del alumnado. "
                      "Incorporar una nota concreta como referencia solo por encargo expreso, acordando "
                      "su destino y audiencia. La carpeta conserva sus permisos de almacenamiento."])
    lines.extend(["", """Respetar las carpetas y las decisiones del docente. Consultar en la carpeta de gestión del proyecto la selección de fuentes, el catálogo y las incidencias cuando existan. Clasificar unidades lógicas con IDs estables, conservar las agrupaciones y dar prioridad a las confirmaciones del docente. Mantener separados ubicación, procedencia, acceso y estado.

Mantener la estructura actual por defecto. Presentar las carpetas y operaciones propuestas antes de una reorganización física y aplicar solo las aceptadas. Promover material generado a referencia oficial únicamente por decisión expresa. Comprobar identidades y versiones al comenzar un trabajo que dependa del inventario. Reparar enlaces tras un movimiento y actualizar solo los contenidos derivados afectados por cambios de fuente.

Usar las carpetas de Entregas únicamente para los procesos de evaluación correspondientes. Separar recibidos y corrección por actividad y convocatoria. Excluir entregas, calificaciones y comentarios individuales del catálogo docente, búsqueda y wiki, incluso al seguir enlaces.

Aplicar `espanol-conciso-redaccion` solo a petición del docente para el encargo o cuando haya elegido ese estilo para toda la asignatura. Invocar `proyecto-docente-ayuda` ante dudas de uso y siguientes pasos. Recomendar la creación del mapa cuando proceda. Consultar un mapa real desde su índice y citar las fuentes autorizadas.

Usar subagentes cuando el anfitrión lo permita y haya trabajo independiente. Compartir solo los datos necesarios. El agente principal revisa e integra, y solo él consolida la hoja Moodle. Consultar al docente antes de cambiar a un modelo más sencillo y respetar su elección para el lote. Reservar soluciones y rúbricas completas al docente. Para cuestionarios, conservar los modelos, manifiesto y bancos congelados. Consultar conflictos antes de modificar instrucciones anteriores.""", p.END_MARKER])
    return "\n".join(lines)


def _adoption(old):
    config = defaults()
    config["spaces"] = {"sources": ["fuentes"], "generated": ["materiales_generados"],
                        "submissions": ["resultados"]}
    # Conservar las fuentes extra que sí fueron seleccionadas expresamente.
    for path in old["sources"]["include"]:
        if not any(under(path, r) for values in config["spaces"].values() for r in values):
            if reserved(path) or (old["map"] and under(path, old["map"])):
                continue
            existing = config["spaces"]["sources"]
            existing[:] = [r for r in existing if not under(r, path)]
            existing.append(path)
    config["sources"] = copy.deepcopy(old["sources"])
    config["adopted_from"] = p.CONFIG_V3
    config["map"] = old["map"]
    if old["map"]:
        config["adopted_map"] = old["map"]
    config["adoption_review"] = [r for r in config["sources"]["include"]
                                 if not any(under(r, base) for base in config["spaces"]["sources"])]
    config["sources"]["include"] = [r for r in config["sources"]["include"]
                                    if r not in config["adoption_review"]]
    return config


def _pending(root, reason, **detail):
    return {"status": "pending_approval", "root": str(root), "created": [], "updated": [],
            "would_create": [], "would_update": [], "proposals": [{"reason": reason, **detail}],
            "wiki_created": False, "warnings": []}


def initialize(root, *, spaces, notes, include, exclude, dry_run, adopt_v3):
    root = p._root(root)
    control = p.project_config_path(root)
    previous = p.load_project(root) if control or p._implicit_v4(root) else None
    v3 = previous is not None and previous["structure"] == "curso-v3"
    config = copy.deepcopy(previous) if previous else defaults()
    if v3:
        config = _adoption(previous)
    if v3 and not adopt_v3:
        return _pending(root, "Propuesta de adopción de curso-v3; confirmar antes de escribir.",
                        spaces=config["spaces"], sources=config["sources"],
                        review=config["adoption_review"], map=config["map"])
    if spaces is not None:
        if not isinstance(spaces, dict):
            raise ValueError("spaces debe ser un objeto con las carpetas asignadas.")
        assigned = copy.deepcopy(spaces)
        if "notes" in config["spaces"]:
            assigned.setdefault("notes", config["spaces"]["notes"])
        config["spaces"] = assigned
    if notes is not None:
        relative = p._relative(notes, label="notes")
        assigned_notes = p._paths(config["spaces"].get("notes", []), "notes")
        if relative not in assigned_notes:
            assigned_notes.append(relative)
        config["spaces"]["notes"] = assigned_notes
    if previous is None and root.is_dir() and spaces is None:
        allowed = {i for values in config["spaces"].values() for i in values}
        allowed.update({"AGENTS.md", "LEEME.md", *p.IGNORED_FILENAMES})
        # Mostrar nombres de primer nivel. El agente clasifica después, con el docente.
        entries = sorted(item.name for item in root.iterdir() if item.name not in allowed and not reserved(item.name))
        if entries:
            return _pending(root, "Asignar las carpetas existentes a los tres espacios antes de preparar el curso.",
                            entries=entries)
    if include is not None:
        config["sources"]["selected"] = True
        config["sources"]["include"] = include
    if exclude is not None:
        config["sources"]["exclude"] = exclude
    config = validate_config(root, config)
    for field, changed in (("include", include is not None), ("exclude", exclude is not None)):
        if changed or v3:
            config.setdefault("source_bindings", {})[field] = _capture(root, config, field)
    agents = p._safe_path(root, "AGENTS.md")
    if agents.exists() and not agents.is_file():
        raise ValueError("AGENTS.md debe ser un archivo regular.")
    block = instructions(config)
    proposal = p._proposal(agents.read_text(encoding="utf-8"), block) if agents.exists() else None
    managed = p._safe_path(root, p.config_v4(root))
    # Si el AGENTS pertenece al docente, persistir la configuración para poder descubrirla.
    persist = managed.exists() or config != defaults() or proposal is not None
    dirs = list(p.project_directories(config))
    if persist or previous is None:
        dirs.append(p.management_dir(root))
    new = [d + "/" for d in dirs if not (root / d).exists()]
    if not agents.exists():
        new.append("AGENTS.md")
    if persist and not managed.exists():
        new.append(p.config_v4(root))
    update = [p.config_v4(root)] if managed.is_file() and config != previous else []
    if not dry_run:
        for d in dirs:
            if d in p.MANAGEMENT_NAMES:
                p.ensure_management_dir(root)
                continue
            p._safe_path(root, d).mkdir(parents=True, exist_ok=True)
        if not agents.exists():
            p._write_new(agents, "# Instrucciones del proyecto docente\n\n" + block + "\n")
        if p.config_v4(root) in new or update:
            p._replace_config(managed, json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    return {"status": "dry_run" if dry_run else "pending_approval" if proposal else "ok",
            "root": str(root), "config": config, "created": [] if dry_run else new,
            "updated": [] if dry_run else update, "would_create": new if dry_run else [],
            "would_update": update if dry_run else [], "proposals": [proposal] if proposal else [],
            "wiki_created": False, "warnings": (["La selección de fuentes está pendiente."]
                                               if not config["sources"]["selected"] else [])}
