"""Preparación portable de cursos y selección explícita de sus fuentes.

Las exclusiones son rutas exactas de archivos o árboles de directorios, nunca
patrones glob. Estas utilidades no crean una wiki ni leen contenido docente.
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

CONFIG_NAME = "proyecto-docente.json"
PROJECT_DIRECTORIES = (
    "alumnado/materiales", "alumnado/actividades", "alumnado/conocimientos",
    "docente/fuentes", "docente/evaluaciones", "docente/soluciones",
    "docente/rubricas", "docente/borradores", "docente/mapa-docente",
    "docente/resultados", "archivo",
)
PERMANENT_EXCLUSIONS = (
    "docente/resultados", "docente/borradores", "docente/mapa-docente",
)
IGNORED_FILENAMES = {".gitkeep", ".DS_Store"}
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
START_MARKER = "<!-- asistente-docente:proyecto:inicio -->"
END_MARKER = "<!-- asistente-docente:proyecto:fin -->"
AGENTS_BLOCK = f"""{START_MARKER}
## Proyecto docente

- Consultar `proyecto-docente.json` para conocer la estructura, las fuentes
  elegidas y sus exclusiones. La selección no declara documentos leídos ni
  autoriza su publicación. No ampliar las fuentes a carpetas vecinas.
- Redactar los textos en español con la skill `redactar-espanol-claro`, salvo
  indicación distinta del docente; conservar rigor, terminología y atribuciones.
- Preparar nuevos materiales en `docente/borradores/`. Llevarlos a `alumnado/`
  cuando el encargo incluya su entrega, manteniendo una única ubicación por
  material. Reservar evaluaciones, soluciones y rúbricas en `docente/`.
- Mantener entregas, calificaciones y feedback en `docente/resultados/`, fuera
  del corpus de la wiki. `alumnado/conocimientos/` contiene aclaraciones útiles,
  no una copia de la wiki. Incorporar `archivo/` solo si se elige expresamente.
- Comprobar las entradas que requiere cada encargo; una carpeta vacía no bloquea
  trabajos que ya tengan contexto o adjuntos suficientes.
- Respetar estas instrucciones y consultar conflictos antes de modificarlas.
  Iniciar el proyecto no crea el Mapa docente ni invoca su creación.
{END_MARKER}"""
LEEME_CONTENT = """# Mi proyecto docente

Trabaja con el agente en esta carpeta. Las instrucciones están en `AGENTS.md` y
la selección de fuentes se guarda en `proyecto-docente.json`.

| Carpeta | Uso |
| --- | --- |
| `alumnado/materiales/` | Materiales preparados para estudiantes. |
| `alumnado/actividades/` | Enunciados y actividades para estudiantes. |
| `alumnado/conocimientos/` | Dudas frecuentes y aclaraciones útiles. |
| `docente/fuentes/` | Fuentes de referencia elegidas por el profesor. |
| `docente/evaluaciones/` | Bancos, exámenes y criterios reservados. |
| `docente/soluciones/` | Soluciones y orientaciones del docente. |
| `docente/rubricas/` | Rúbricas de evaluación. |
| `docente/borradores/` | Nuevos materiales todavía en preparación. |
| `docente/mapa-docente/` | Wiki, lector y grafo cuando se creen. |
| `docente/resultados/` | Entregas, calificaciones y feedback; fuera de la wiki. |
| `archivo/` | Material apartado; solo se usa si se selecciona expresamente. |

Puedes pedir «Prepara una actividad a partir de estos apuntes», «Revisa este
texto» o «Evalúa estas entregas con esta rúbrica». Indica las fuentes y el
destino cuando el encargo no los deje claros. El agente preguntará únicamente
por la información que falte.

La puesta en marcha deja la carpeta del mapa vacía. Crear el Mapa docente es un
encargo posterior y explícito; las fuentes seleccionadas pueden revisarse antes.
No es necesario duplicar la wiki en las carpetas del alumnado.

Los nombres de las carpetas organizan los contenidos: no configuran permisos.
Una carpeta sincronizada con OneDrive o SharePoint sigue usando sus permisos y
su sincronización existentes. Comprueba que el agente haya leído `AGENTS.md`;
si su aplicación no lo carga, pídele expresamente que lo lea.
"""


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _root(root) -> Path:
    candidate = Path(root).expanduser()
    if candidate.is_symlink():
        raise ValueError("La raíz del proyecto no puede ser un enlace simbólico.")
    path = candidate.resolve()
    if _inside(path, PLUGIN_ROOT):
        raise ValueError("El proyecto docente debe estar fuera de la instalación del plugin.")
    if path.exists() and not path.is_dir():
        raise ValueError("La raíz del proyecto debe ser una carpeta.")
    return path


def _relative(value, *, label="ruta") -> str:
    if not isinstance(value, str) or not value.strip() or "\\" in value or "\x00" in value:
        raise ValueError(f"{label}: se requiere una ruta relativa con separadores '/'.")
    path = PurePosixPath(value)
    if path.is_absolute() or PureWindowsPath(value).drive or ".." in path.parts or str(path) == ".":
        raise ValueError(f"{label}: la ruta debe permanecer dentro del proyecto.")
    if any(character in value for character in ("*", "?")):
        raise ValueError(f"{label}: no se admiten patrones glob; indica rutas exactas.")
    return path.as_posix()


def _has_symlink(root: Path, path: Path) -> bool:
    if not _inside(path, root):
        return True
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            return True
    return False


def _safe_path(root: Path, relative: str) -> Path:
    path = root / relative
    for parent in path.parents:
        if parent == root:
            break
        if _inside(parent, root) and parent.exists() and not parent.is_dir():
            raise ValueError(f"Colisión con un archivo en la ruta: {relative}")
    if _has_symlink(root, path) or not _inside(path.resolve(), root):
        raise ValueError(f"Ruta insegura o enlace simbólico: {relative}")
    return path


def _paths(values, label) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"{label} debe ser una lista de rutas relativas.")
    paths = [_relative(value, label=label) for value in values]
    if len(paths) != len(set(paths)):
        raise ValueError(f"{label} contiene rutas duplicadas.")
    return paths


def _within_relative(path: str, parent: str) -> bool:
    return path == parent or path.startswith(parent + "/")


def _validate_config(root: Path, data: dict) -> dict:
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("schema_version debe ser 1.")
    if data.get("structure") != "curso-v1":
        raise ValueError("structure debe ser 'curso-v1'.")
    sources = data.get("sources")
    if not isinstance(sources, dict) or type(sources.get("selected")) is not bool:
        raise ValueError("sources.selected debe ser true o false.")
    include = _paths(sources.get("include"), "sources.include")
    exclude = _paths(sources.get("exclude"), "sources.exclude")
    if not sources["selected"] and (include or exclude):
        raise ValueError("Una selección pendiente debe tener include y exclude vacíos.")
    if "map" not in data:
        raise ValueError("La configuración debe declarar map (null cuando no existe).")
    map_path = data["map"]
    if map_path is not None:
        map_path = _relative(map_path, label="map")
        index = _safe_path(root, map_path + "/index.md")
        if not index.is_file():
            raise ValueError("map debe señalar una carpeta con un index.md real existente.")
    excluded = list(PERMANENT_EXCLUSIONS) + ([map_path] if map_path else [])
    for relative in include:
        if relative == "docente":
            raise ValueError("No se puede seleccionar docente en bloque; elige carpetas concretas.")
        if any(_within_relative(relative, reserved) for reserved in excluded):
            raise ValueError(f"La carpeta {relative} está excluida permanentemente del corpus.")
        folder = _safe_path(root, relative)
        if folder.exists() and not folder.is_dir():
            raise ValueError(f"La fuente seleccionada debe ser una carpeta: {relative}")
    for relative in exclude:
        _safe_path(root, relative)
    result = copy.deepcopy(data)
    result["sources"]["include"] = include
    result["sources"]["exclude"] = exclude
    result["map"] = map_path
    return result


def _unique_json(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Clave JSON duplicada: {key}")
        result[key] = value
    return result


def load_project(root) -> dict:
    """Leer y validar la configuración sin recorrer ni leer las fuentes."""
    path = _root(root)
    config_file = _safe_path(path, CONFIG_NAME)
    try:
        data = json.loads(config_file.read_text(encoding="utf-8"), object_pairs_hook=_unique_json)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se puede leer {CONFIG_NAME}: {exc}") from exc
    return _validate_config(path, data)


def find_project(path) -> Path | None:
    """Encontrar la configuración más cercana en la ruta o sus antecesores."""
    candidate = Path(path).expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in (candidate, *candidate.parents):
        control = parent / CONFIG_NAME
        if control.exists() or control.is_symlink():
            return parent
    return None


def source_allowed(root, config: dict, file) -> bool:
    """Comprobar solo la ruta: no abre el contenido ni declara una lectura."""
    try:
        root = _root(root)
        candidate = Path(file)
        if candidate.name in IGNORED_FILENAMES:
            return False
        if ".." in candidate.parts:
            return False
        if not candidate.is_absolute():
            candidate = root / _relative(str(candidate), label="fuente")
        candidate = Path(os.path.abspath(candidate))
        if not _inside(candidate, root):
            # macOS exposes /var and /tmp through system aliases. Resolve only
            # an ancestor matching the project root, preserving symlinks below it.
            for ancestor in candidate.parents:
                if ancestor.resolve() == root:
                    candidate = root / candidate.relative_to(ancestor)
                    break
        if not _inside(candidate, root) or _has_symlink(root, candidate):
            return False
        resolved = candidate.resolve()
        if not _inside(resolved, root):
            return False
        relative = candidate.relative_to(root).as_posix()
        sources = config["sources"]
        if sources["selected"] is not True:
            return False
        excluded = list(PERMANENT_EXCLUSIONS) + sources["exclude"]
        if config.get("map"):
            excluded.append(config["map"])
        if any(_within_relative(relative, item) for item in excluded):
            return False
        return any(_within_relative(relative, item) for item in sources["include"])
    except (ValueError, TypeError, KeyError, OSError):
        return False


def _proposal(content: str) -> dict | None:
    if AGENTS_BLOCK in content and content.count(START_MARKER) == content.count(END_MARKER) == 1:
        return None
    starts, ends = content.count(START_MARKER), content.count(END_MARKER)
    if starts == ends == 1 and content.index(START_MARKER) < content.index(END_MARKER):
        start = content.index(START_MARKER)
        end = content.index(END_MARKER) + len(END_MARKER)
        proposed = content[:start] + AGENTS_BLOCK + content[end:]
        reason = "Actualizar exclusivamente el bloque del proyecto; revisar conflictos con instrucciones existentes."
    elif starts or ends:
        return {"path": "AGENTS.md", "reason": "Marcadores incompletos o duplicados: resolver el conflicto con el docente.",
                "proposed_content": None, "block": AGENTS_BLOCK}
    else:
        proposed = content.rstrip() + "\n\n" + AGENTS_BLOCK + "\n"
        reason = "Incorporar el bloque del proyecto respetando el contenido existente; consultar conflictos."
    return {"path": "AGENTS.md", "reason": reason, "proposed_content": proposed,
            "block": AGENTS_BLOCK}


def _write_new(path: Path, content: str):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def _replace_config(path: Path, content: str):
    """Sustituir únicamente la configuración cuya modificación se pidió."""
    if path.is_symlink():
        raise ValueError(f"No se puede sustituir un enlace simbólico: {path.name}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=".proyecto-docente-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def initialize_project(root, *, include=None, exclude=None, dry_run=False) -> dict:
    """Preparar el curso; nunca modificar AGENTS/LEEME preexistentes.

    ``include=None`` conserva la selección actual; ``include=[]`` expresa una
    selección explícita sin fuentes. ``dry_run`` no crea siquiera la raíz.
    """
    root = _root(root)
    controls = {}
    for name in (CONFIG_NAME, "AGENTS.md", "LEEME.md"):
        path = _safe_path(root, name)
        if path.exists() and not path.is_file():
            raise ValueError(f"Colisión: {name} existe y no es un archivo.")
        controls[name] = path
    directories = [_safe_path(root, name) for name in PROJECT_DIRECTORIES]
    for path in directories:
        if path.exists() and not path.is_dir():
            raise ValueError(f"Colisión con un archivo: {path.relative_to(root)}")
    previous = load_project(root) if controls[CONFIG_NAME].exists() else None
    config = copy.deepcopy(previous) if previous is not None else {
        "schema_version": 1, "structure": "curso-v1",
        "sources": {"selected": False, "include": [], "exclude": []}, "map": None,
    }
    if isinstance(include, (str, bytes)) or isinstance(exclude, (str, bytes)):
        raise ValueError("include y exclude deben ser listas de rutas, no cadenas.")
    if include is not None:
        config["sources"] = {"selected": True, "include": list(include),
                             "exclude": list(exclude) if exclude is not None else config["sources"]["exclude"]}
    elif exclude is not None:
        if not config["sources"]["selected"]:
            raise ValueError("Elige include antes de establecer exclusiones.")
        config["sources"]["exclude"] = list(exclude)
    config = _validate_config(root, config)
    proposals = []
    if controls["AGENTS.md"].exists():
        proposal = _proposal(controls["AGENTS.md"].read_text(encoding="utf-8"))
        if proposal:
            proposals.append(proposal)
    if controls["LEEME.md"].exists() and controls["LEEME.md"].read_text(encoding="utf-8") != LEEME_CONTENT:
        proposals.append({"path": "LEEME.md", "reason": "Conservar la guía existente; integrar esta propuesta solo tras revisión.",
                          "proposed_content": LEEME_CONTENT})
    create = [path.relative_to(root).as_posix() + "/" for path in directories if not path.exists()]
    new_files = {}
    if not controls["AGENTS.md"].exists():
        new_files["AGENTS.md"] = "# Instrucciones del proyecto docente\n\n" + AGENTS_BLOCK + "\n"
    if not controls["LEEME.md"].exists():
        new_files["LEEME.md"] = LEEME_CONTENT
    config_content = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    if previous is None:
        new_files[CONFIG_NAME] = config_content
    create += list(new_files)
    updated = [CONFIG_NAME] if previous is not None and previous != config else []
    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)
        for path in directories:
            _safe_path(root, path.relative_to(root).as_posix()).mkdir(parents=True, exist_ok=True)
        for name, content in new_files.items():
            _write_new(_safe_path(root, name), content)
        if updated:
            _replace_config(_safe_path(root, CONFIG_NAME), config_content)
    return {"status": "dry_run" if dry_run else "pending_approval" if proposals else "ok",
            "root": str(root), "config": config, "created": [] if dry_run else create,
            "would_create": create if dry_run else [], "updated": [] if dry_run else updated,
            "would_update": updated if dry_run else [], "proposals": proposals,
            "wiki_created": False,
            "warnings": (["La selección de fuentes está pendiente."] if not config["sources"]["selected"] else [])}


def _readable(path: Path, directory=False) -> bool:
    try:
        mode = path.stat().st_mode
        if os.name != "nt" and (not mode & 0o444 or directory and not mode & 0o111):
            return False
        return os.access(path, os.R_OK | (os.X_OK if directory else 0))
    except OSError:
        return False


def _scan_source(root: Path, config: dict, relative: str) -> dict:
    folder = root / relative
    report = {"path": relative, "status": "ok", "files": [], "inaccessible": [], "excluded_entries": 0}
    if not folder.exists():
        report["status"] = "missing"
        return report
    seen_files = 0

    def walk(directory):
        nonlocal seen_files
        if not _readable(directory, directory=True):
            report["inaccessible"].append(directory.relative_to(root).as_posix())
            return
        try:
            with os.scandir(directory) as entries:
                entries = sorted(entries, key=lambda entry: entry.name)
        except OSError:
            report["inaccessible"].append(directory.relative_to(root).as_posix())
            return
        for entry in entries:
            if entry.name in IGNORED_FILENAMES:
                continue
            path = Path(entry.path)
            if not source_allowed(root, config, path):
                report["excluded_entries"] += 1
                continue
            try:
                if entry.is_dir(follow_symlinks=False):
                    walk(path)
                elif entry.is_file(follow_symlinks=False):
                    seen_files += 1
                    if _readable(path):
                        report["files"].append(path.relative_to(root).as_posix())
                    else:
                        report["inaccessible"].append(path.relative_to(root).as_posix())
                else:
                    report["inaccessible"].append(path.relative_to(root).as_posix())
            except OSError:
                report["inaccessible"].append(path.relative_to(root).as_posix())

    if source_allowed(root, config, folder):
        walk(folder)
    else:
        report["excluded_entries"] += 1
    if report["inaccessible"]:
        report["status"] = "inaccessible"
    elif not report["files"]:
        report["status"] = "no_selected_files" if seen_files or report["excluded_entries"] else "empty"
    return report


def check_project(root) -> dict:
    """Diagnóstico de estructura y corpus; no bloquea otras tareas del agente."""
    report = {"status": "ok", "errors": [], "warnings": [], "sources": [],
              "selected_files": [], "selection_status": "pending", "missing_directories": []}
    try:
        root = _root(root)
        report["root"] = str(root)
        if not (root / CONFIG_NAME).exists() and not (root / CONFIG_NAME).is_symlink():
            report["status"] = "incomplete"
            report["warnings"].append(f"Falta {CONFIG_NAME}; inicia el proyecto o proporciona las entradas del encargo.")
            return report
        config = load_project(root)
        report["config"] = config
        for relative in PROJECT_DIRECTORIES:
            path = _safe_path(root, relative)
            if not path.is_dir():
                report["missing_directories"].append(relative)
        for name in ("AGENTS.md", "LEEME.md"):
            path = _safe_path(root, name)
            if not path.is_file():
                report["warnings"].append(f"Falta {name}.")
        if report["missing_directories"]:
            report["warnings"].append("Faltan carpetas de la estructura del curso.")
        if not config["sources"]["selected"]:
            report["warnings"].append("La selección de fuentes está pendiente.")
        else:
            report["selection_status"] = "selected" if config["sources"]["include"] else "none"
            for relative in config["sources"]["include"]:
                report["sources"].append(_scan_source(root, config, relative))
            report["selected_files"] = sorted({file for source in report["sources"] for file in source["files"]})
            if not config["sources"]["include"]:
                report["warnings"].append("Se ha elegido no incorporar fuentes: no_selected_files.")
            labels = {"missing": "carpeta inexistente", "empty": "carpeta vacía",
                      "no_selected_files": "sin archivos seleccionados", "inaccessible": "archivos o carpetas no accesibles"}
            for source in report["sources"]:
                if source["status"] != "ok":
                    report["warnings"].append(f"{source['path']}: {labels[source['status']]}.")
        if report["warnings"]:
            report["status"] = "incomplete"
    except (ValueError, OSError, UnicodeError) as exc:
        report["status"] = "invalid"
        report["errors"].append(str(exc))
    return report


def plan_migration(root, moves) -> dict:
    """Entrada común para la propuesta no mutante de migración."""
    from .migration import plan_migration as prepare
    return prepare(root, moves)
