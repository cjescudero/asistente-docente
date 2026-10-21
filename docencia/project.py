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
PROJECT_DIRECTORIES_V1 = (
    "alumnado/materiales", "alumnado/actividades", "alumnado/conocimientos",
    "docente/fuentes", "docente/evaluaciones", "docente/soluciones",
    "docente/rubricas", "docente/borradores", "docente/mapa-docente",
    "docente/resultados", "docente/resultados/entregas", "archivo",
)
PERMANENT_EXCLUSIONS_V1 = (
    "docente/resultados", "docente/borradores", "docente/mapa-docente",
)
IGNORED_FILENAMES = {".gitkeep", ".DS_Store"}
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
START_MARKER = "<!-- asistente-docente:proyecto:inicio -->"
END_MARKER = "<!-- asistente-docente:proyecto:fin -->"
AGENTS_BLOCK_V1 = f"""{START_MARKER}
## Proyecto docente

- Consultar `proyecto-docente.json` para conocer la estructura, las fuentes
  elegidas y sus exclusiones. La selección no declara documentos leídos ni
  autoriza su publicación. No ampliar las fuentes a carpetas vecinas.
- Redactar los textos en español con la skill `espanol-conciso-redaccion`, salvo
  indicación distinta del docente; conservar rigor, terminología y atribuciones.
- Preparar nuevos materiales en `docente/borradores/`. Llevarlos a `alumnado/`
  cuando el encargo incluya su entrega, manteniendo una única ubicación por
  material. Reservar evaluaciones, soluciones y rúbricas en `docente/`.
- Mantener entregas, calificaciones y feedback en `docente/resultados/`, fuera
  del corpus de la wiki. Organizar cada lote en
  `docente/resultados/entregas/<actividad>/<convocatoria>/`, conservando originales,
  identificación y corrección separados. `alumnado/conocimientos/` contiene aclaraciones útiles,
  no una copia de la wiki. Incorporar `archivo/` solo si se elige expresamente.
- Comprobar las entradas que requiere cada encargo; una carpeta vacía no bloquea
  trabajos que ya tengan contexto o adjuntos suficientes.
- Respetar estas instrucciones y consultar conflictos antes de modificarlas.
  Iniciar el proyecto no crea el Mapa docente ni invoca su creación.
- Al finalizar la puesta en marcha, ofrecer `proyecto-docente-ayuda` y recomendar
  crear el mapa con las fuentes elegidas, o consultarlo si ya existe. Esperar
  un encargo del profesor antes de iniciar cualquiera de esas tareas.
  Si la selección está pendiente, ayudar a concretarla; si se eligió trabajar
  sin fuentes, respetarlo y ofrecer tareas con adjuntos sin insistir en el mapa.
{END_MARKER}"""
LEEME_CONTENT_V1 = """# Mi proyecto docente

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
| `docente/resultados/entregas/` | Un lote por actividad y convocatoria, con originales, identificación y corrección separados. |
| `archivo/` | Material apartado; solo se usa si se selecciona expresamente. |

## Qué hacer ahora

Pide **«¿Qué puedo hacer ahora con mi asignatura?»**. El agente consultará la
configuración y los índices disponibles para orientarte sin leer todo el curso
ni iniciar tareas por su cuenta.

El primer paso recomendado es **«Crea el mapa docente con las fuentes que he
elegido»**. Después puedes pedir «Consulta el mapa para localizar materiales de
este tema», «Muéstrame su grafo» o «Actualiza el mapa con los cambios autorizados».
Si aún no has elegido fuentes, el agente te ayudará a concretarlas.
Si has decidido trabajar sin fuentes, puedes usar adjuntos para cada encargo
sin necesidad de crear el mapa.

| Petición de ejemplo | Qué necesita el agente |
| --- | --- |
| «Diseñemos una actividad sobre estos conocimientos» | Materiales, nivel, objetivos y condiciones. El diálogo termina con enunciado, plantillas y rúbrica docente reservada. |
| «Crea un banco para estos apuntes y esta actividad» | Fuentes actuales; ejemplos anteriores opcionales para calibrar dificultad. |
| «Prepara dos modelos de examen sobre estos temas» | Bancos, cobertura, título, cantidad de preguntas y dificultad; PDF y GIFT ofuscado para importar manualmente en Moodle. |
| «Evalúa estas entregas con los criterios de la actividad» | Enunciado, rúbrica o criterios, entregas e identificación explícita, y hoja Moodle para devolver nota y feedback. |
| «Añade recomendaciones a estas calificaciones» | Detalle por pregunta, manifiesto del examen y hoja Moodle; se conservan las notas y se priorizan hasta tres dificultades. |
| «Prepara apuntes», «Haz una infografía» o «Aclara este texto» | Fuentes y destinatarios. Infografías o diapositivas visuales individuales, apuntes y español claro inspirado en ASD-STE100. |

Indica las fuentes y el destino cuando el encargo no los deje claros. El agente
preguntará únicamente por la información que falte. Los bancos se registran en
`docente/evaluaciones/bancos/` cuando se incorporen al catálogo. Las rúbricas
completas y soluciones permanecen en `docente/`; el enunciado comunica criterios
generales. La rúbrica local no configura la calificación avanzada de Moodle.

La puesta en marcha deja la carpeta del mapa vacía. Crear el Mapa docente es un
encargo posterior y explícito; las fuentes seleccionadas pueden revisarse antes.
No es necesario duplicar la wiki en las carpetas del alumnado.

Los nombres de las carpetas organizan los contenidos: no configuran permisos.
Una carpeta sincronizada con OneDrive o SharePoint sigue usando sus permisos y
su sincronización existentes. Comprueba que el agente haya leído `AGENTS.md`;
si su aplicación no lo carga, pídele expresamente que lo lea.
"""


# Los proyectos existentes conservan su estructura hasta una migración explícita.
PROJECT_DIRECTORIES_V2_LEGACY = (
    "fuentes/teoria", "fuentes/actividades", "fuentes/evaluaciones/examenes",
    "fuentes/evaluaciones/bancos", "creados/materiales", "creados/actividades",
    "creados/bancos", "creados/examenes", "mapa-docente", "resultados", "archivo",
)
PROJECT_DIRECTORIES = (
    "fuentes/teoria", "fuentes/actividades", "fuentes/evaluaciones/cuestionarios",
    "fuentes/evaluaciones/bancos", "creados/materiales", "creados/actividades",
    "creados/bancos", "creados/cuestionarios", "mapa-docente", "resultados", "archivo",
)
QUESTIONNAIRE_PATHS = {"sources": "fuentes/evaluaciones/cuestionarios",
                       "created": "creados/cuestionarios"}
PERMANENT_EXCLUSIONS = (*PERMANENT_EXCLUSIONS_V1, "resultados", "mapa-docente")
MATERIAL_RECORD_NAME = "material-docente.json"
MATERIAL_TYPES = frozenset({"material", "actividad", "banco", "examen", "cuestionario", "apuntes",
                            "diapositivas", "infografia"})
MATERIAL_STATUSES = frozenset({"borrador", "revisado", "listo-para-entregar"})
CORPUS_MATERIAL_STATUSES = frozenset({"revisado", "listo-para-entregar"})
AGENTS_BLOCK = f"""{START_MARKER}
## Proyecto docente

- Consultar `proyecto-docente.json` para conocer la estructura, las fuentes
  elegidas y sus exclusiones. La selección no declara documentos leídos ni
  autoriza su publicación. No ampliar las fuentes a carpetas vecinas.
- Redactar los textos en español con la skill `espanol-conciso-redaccion`, salvo
  indicación distinta del docente; conservar rigor, terminología y atribuciones.
- Conservar el material aportado en `fuentes/` y crear las nuevas producciones
  en `creados/materiales/`, `creados/actividades/`, `creados/bancos/` o
  `creados/cuestionarios/`, en una carpeta estable por resultado. Separar documentos
  del alumnado y documentos docentes dentro de cada actividad o evaluación.
- Registrar cada producción con `material-docente.json` y mostrar su estado
  en `LEEME.md`: borrador, revisado o listo-para-entregar. El estado no cambia
  su ubicación. Conservar una única ubicación por material, también cuando
  sirva como entrada de otro encargo. No trasladar originales sin autorización.
- Incorporar producciones al corpus solo si se seleccionan expresamente y su
  registro indica revisado o listo-para-entregar. No incorporar borradores,
  producciones sin registro válido, resultados ni el propio mapa. Incorporar
  `archivo/` solo si se elige expresamente. Respetar exclusiones incluso por enlaces.
- Mantener las entregas y exportaciones Moodle originales en
  `resultados/<actividad>/<convocatoria>/recibidos/` y las valoraciones, copias
  de calificaciones y feedback en `correccion/` del mismo lote, fuera de la wiki.
  Los nombres de las carpetas no gestionan permisos.
- Comprobar las entradas que requiere cada encargo; una carpeta vacía no bloquea
  trabajos que ya tengan contexto o adjuntos suficientes.
- Respetar estas instrucciones y consultar conflictos antes de modificarlas.
  Iniciar el proyecto no crea el Mapa docente ni invoca su creación.
- Al terminar cada tarea, consultar registros, archivos e índices pertinentes
  para sugerir el siguiente paso pendiente. Una carpeta o nombre de archivo
  por sí solos no acreditan un resultado terminado; señalar indicios no verificados.
  No iniciar otra tarea ni leer todo el curso para formular la sugerencia.
- Tras la puesta en marcha, recomendar crear el mapa con las fuentes elegidas;
  si ya existe y está registrado, ofrecer consultarlo o visualizarlo y elegir
  un flujo. Si la selección está pendiente, ayudar a concretarla; si se eligió
  trabajar sin fuentes, respetarlo y ofrecer tareas con los adjuntos disponibles.
- Para cuestionarios, usar cuatro modelos salvo otra indicación. Proponer cantidad
  de preguntas principales según conceptos y objetivos y explicar el reparto;
  las variantes no cuentan como cobertura adicional. Proponer también duración
  estimada ajustable. No incluir dos variantes de una principal en el mismo modelo.
- El mapa explica conceptos y relaciones con evidencia, condiciones, ejemplos y
  límites; usar originales para profundizar o verificar, sin tratarlos como lectura
  obligatoria de toda consulta cuando la wiki ya aporta evidencia suficiente.
- Flujos: actividad → evaluación de entregas cuando existan entregas identificadas
  y criterios; banco → modelos impresos cuando haya preguntas utilizables;
  modelos → feedback cuando haya resultados por pregunta y manifiesto.
  Si falta una entrada, explicar cuál y no dar por completada la fase anterior.
  Ofrecer también apuntes y diapositivas visuales individuales o infografías.
  No repetir fases ya acreditadas salvo petición de revisión o actualización.
{END_MARKER}"""
LEEME_CONTENT = """# Mi proyecto docente

Trabaja con el agente en esta carpeta. Las instrucciones están en `AGENTS.md` y
la selección de fuentes se guarda en `proyecto-docente.json`.

| Carpeta | Uso |
| --- | --- |
| `fuentes/teoria/` | Apuntes, diapositivas y referencias aportados. |
| `fuentes/actividades/` | Actividades aportadas, actuales o de otros cursos. |
| `fuentes/evaluaciones/cuestionarios/` | Cuestionarios aportados, identificando curso y vigencia. |
| `fuentes/evaluaciones/bancos/` | Bancos aportados; se enlazan sin copiarlos. |
| `creados/materiales/` | Apuntes, infografías y diapositivas visuales creados. |
| `creados/actividades/` | Una carpeta por actividad con documentos del alumnado y del docente separados. |
| `creados/bancos/` | Nuevos bancos y el catálogo que enlaza los bancos utilizables. |
| `creados/cuestionarios/` | Una carpeta por cuestionario, con modelos y archivos docentes separados. |
| `mapa-docente/` | Wiki, lector y grafo cuando se creen. |
| `resultados/` | Un lote por actividad y convocatoria: recibidos originales y corrección; siempre fuera de la wiki. |
| `archivo/` | Material apartado; solo se usa si se selecciona expresamente. |

Los materiales aportados permanecen en `fuentes/`. Cada producción nueva tiene
una carpeta estable en `creados/`, un registro `material-docente.json` y un
`LEEME.md` que muestra su estado: **borrador**, **revisado** o
**listo para entregar**. Cambiar de estado no mueve los documentos.
Un documento creado puede alimentar otra tarea sin copiarlo a `fuentes/`.
Las rúbricas completas y soluciones quedan separadas de los documentos estudiantiles.
Seleccionar un material para la wiki no autoriza su entrega al alumnado.

## Qué hacer ahora

Pide **«¿Qué puedo hacer ahora con mi asignatura?»**. El agente consultará la
configuración, los índices y los resultados pertinentes para sugerir el siguiente
paso pendiente. No iniciará tareas por su cuenta ni leerá todo el curso.

El recorrido recomendado es **iniciar el proyecto → crear el mapa docente →
elegir un flujo de trabajo**. Pide «Crea el mapa con las fuentes que he elegido».
Si ya existe, puedes consultarlo, visualizarlo o pedir que se actualice.
Si aún no has elegido fuentes, el agente te ayudará a concretarlas. Si has
preferido trabajar sin fuentes, puedes usar adjuntos sin necesidad de crear el mapa.

| Flujo o petición | Entradas para avanzar |
| --- | --- |
| «Diseñemos una actividad» → «Evalúa las entregas» | Materiales, conocimientos y condiciones para diseñar; enunciado, criterios, entregas identificadas y hoja Moodle para corregir. |
| «Crea un banco» → «Prepara modelos impresos» | Materiales y objetivos para el banco; bancos válidos, cobertura, cantidad de preguntas, modelos y dificultad para el cuestionario. |
| «Prepara modelos» → «Genera observaciones sobre las calificaciones» | Resultados detallados por pregunta, manifiesto de los modelos y hoja Moodle; una nota global no permite inferir dificultades conceptuales. |
| «Prepara apuntes», «Crea diapositivas visuales» o «Haz una infografía» | Fuentes, propósito y destinatarios; las diapositivas son visuales individuales, no presentaciones editables. |

Para los cuestionarios, el punto de partida son cuatro modelos. El agente
propondrá cantidad de preguntas y tiempo aproximado según los conceptos y tipos
de respuesta; puedes ajustar ambas cosas. Las variantes no son conceptos nuevos.

Al finalizar cada tarea, el agente propondrá pasos adecuados a los resultados
comprobados. Si solo encuentra indicios, los señalará y verificará lo necesario;
una carpeta vacía no demuestra que una fase esté hecha. Si faltan entregas o
respuestas, explicará qué debes aportar antes de corregir o generar feedback.
Por defecto redactará en español claro, inspirado en ASD-STE100, salvo que indiques otra preferencia.

Las entregas y exportaciones originales de Moodle se guardan en
`resultados/<actividad>/<convocatoria>/recibidos/`; los informes, las copias de
calificaciones y el feedback se guardan en `correccion/` del mismo lote.
No se alteran las descargas originales ni se importan resultados automáticamente.
La rúbrica local no configura la calificación avanzada de Moodle.

La puesta en marcha deja la carpeta del mapa vacía. La wiki solo incorpora
materiales seleccionados; las producciones requieren un registro válido y estado
revisado o listo para entregar. Borradores, resultados y el propio mapa quedan fuera.

Los nombres de las carpetas organizan los contenidos: no configuran permisos.
Una carpeta sincronizada con OneDrive o SharePoint sigue usando sus permisos y
su sincronización existentes. Comprueba que el agente haya leído `AGENTS.md`;
si su aplicación no lo carga, pídele expresamente que lo lea.
"""


def project_directories(config: dict) -> tuple[str, ...]:
    """Directorios de la versión declarada; no infiere ni aplica migraciones."""
    if config["structure"] == "curso-v1":
        return PROJECT_DIRECTORIES_V1
    if "questionnaire_paths" not in config:
        return PROJECT_DIRECTORIES_V2_LEGACY
    paths = config["questionnaire_paths"]
    return tuple(paths["sources"] if name == QUESTIONNAIRE_PATHS["sources"]
                 else paths["created"] if name == QUESTIONNAIRE_PATHS["created"]
                 else name for name in PROJECT_DIRECTORIES)


def _permanent_exclusions(config: dict) -> tuple[str, ...]:
    return PERMANENT_EXCLUSIONS_V1 if config["structure"] == "curso-v1" else PERMANENT_EXCLUSIONS


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
    if data.get("structure") not in ("curso-v1", "curso-v2"):
        raise ValueError("structure debe ser 'curso-v1' o 'curso-v2'.")
    if "questionnaire_paths" in data:
        paths = data["questionnaire_paths"]
        if (data["structure"] != "curso-v2" or not isinstance(paths, dict)
                or set(paths) != {"sources", "created"}):
            raise ValueError("questionnaire_paths requiere sources y created en curso-v2.")
        for key, parent in (("sources", "fuentes/evaluaciones/"), ("created", "creados/")):
            relative = _relative(paths[key], label=f"questionnaire_paths.{key}")
            if not relative.startswith(parent) or relative == parent.rstrip("/"):
                raise ValueError(f"questionnaire_paths.{key} debe estar bajo {parent}.")
            _safe_path(root, relative)
        if any(_within_relative(paths["created"], reserved) for reserved in ("creados/materiales", "creados/actividades", "creados/bancos")):
            raise ValueError("questionnaire_paths.created colisiona con otro tipo de material.")
        if _within_relative(paths["sources"], "fuentes/evaluaciones/bancos"):
            raise ValueError("questionnaire_paths.sources colisiona con bancos aportados.")
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
    excluded = list(_permanent_exclusions(data)) + ([map_path] if map_path else [])
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


def validate_material_record(path) -> dict:
    """Leer un registro de producción sin abrir los documentos asociados.

    El registro común acredita un estado declarado, no la calidad del contenido
    ni una autorización para publicar. Los registros específicos (actividad,
    banco, manifiesto) conservan sus propios contratos y comprobaciones.
    """
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Falta un registro de material regular: {path.name}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se puede leer {path.name}: {exc}") from exc
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data["schema_version"] != 1):
        raise ValueError(f"{path.name}: schema_version debe ser 1.")
    if not isinstance(data.get("id"), str) or not data["id"].strip():
        raise ValueError(f"{path.name}: id debe ser un identificador no vacío.")
    if not isinstance(data.get("type"), str) or data["type"] not in MATERIAL_TYPES:
        raise ValueError(f"{path.name}: type debe ser uno de {', '.join(sorted(MATERIAL_TYPES))}.")
    if not isinstance(data.get("status"), str) or data["status"] not in MATERIAL_STATUSES:
        raise ValueError(f"{path.name}: status debe ser borrador, revisado o listo-para-entregar.")
    return data


def enclosing_material_record(root, file, *, config=None) -> tuple[Path, dict] | None:
    """Buscar el registro más próximo dentro de creados; fallar cerrado.

    Un registro inválido o borrador en una subcarpeta prevalece sobre otro
    revisado situado por encima. No se siguen enlaces simbólicos.
    """
    root = _root(root)
    path = Path(file)
    if not path.is_absolute():
        path = root / _relative(str(path), label="material")
    created = root / "creados"
    if not _inside(path, created) or _has_symlink(root, path):
        return None
    # Los archivos aún inexistentes (p. ej. enlaces) heredan solo su carpeta.
    directory = path if path.is_dir() else path.parent
    # Un registro global en creados/ o en una categoría no acredita todas las
    # producciones de esa carpeta: cada resultado necesita su propio registro.
    while _inside(directory, created) and len(directory.relative_to(created).parts) >= 2:
        record = directory / MATERIAL_RECORD_NAME
        if record.exists() or record.is_symlink():
            if config is not None:
                relative = record.relative_to(root).as_posix()
                if any(_within_relative(relative, excluded) for excluded in config["sources"]["exclude"]):
                    return None
            return record, validate_material_record(record)
        directory = directory.parent
    return None


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


def _source_path_allowed(root, config: dict, file) -> tuple[Path, Path] | None:
    """Comprobar selección y exclusiones antes de cualquier lectura de registro."""
    try:
        root = _root(root)
        candidate = Path(file)
        if candidate.name in IGNORED_FILENAMES:
            return None
        if ".." in candidate.parts:
            return None
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
            return None
        resolved = candidate.resolve()
        if not _inside(resolved, root):
            return None
        relative = candidate.relative_to(root).as_posix()
        sources = config["sources"]
        if sources["selected"] is not True:
            return None
        excluded = list(_permanent_exclusions(config)) + sources["exclude"]
        if config.get("map"):
            excluded.append(config["map"])
        if any(_within_relative(relative, item) for item in excluded):
            return None
        if any(_within_relative(relative, item) for item in sources["include"]):
            return root, candidate
        return None
    except (ValueError, TypeError, KeyError, OSError):
        return None


def source_allowed(root, config: dict, file) -> bool:
    """Aplicar corpus y estado; solo lee metadatos de producciones seleccionadas.

    Los materiales aportados y los proyectos curso-v1 se comprueban por ruta,
    sin abrir su contenido. En curso-v2, los documentos bajo creados requieren
    un registro común válido y revisado, además de selección expresa.
    """
    paths = _source_path_allowed(root, config, file)
    if paths is None:
        return False
    root, candidate = paths
    if config["structure"] != "curso-v2" or not _inside(candidate, root / "creados"):
        return True
    if candidate.name == MATERIAL_RECORD_NAME:
        return False
    try:
        record = enclosing_material_record(root, candidate, config=config)
        return record is not None and record[1]["status"] in CORPUS_MATERIAL_STATUSES
    except (ValueError, OSError, UnicodeError):
        return False


def _proposal(content: str, block: str = AGENTS_BLOCK) -> dict | None:
    if block in content and content.count(START_MARKER) == content.count(END_MARKER) == 1:
        return None
    starts, ends = content.count(START_MARKER), content.count(END_MARKER)
    if starts == ends == 1 and content.index(START_MARKER) < content.index(END_MARKER):
        start = content.index(START_MARKER)
        end = content.index(END_MARKER) + len(END_MARKER)
        proposed = content[:start] + block + content[end:]
        reason = "Actualizar exclusivamente el bloque del proyecto; revisar conflictos con instrucciones existentes."
    elif starts or ends:
        return {"path": "AGENTS.md", "reason": "Marcadores incompletos o duplicados: resolver el conflicto con el docente.",
                "proposed_content": None, "block": block}
    else:
        proposed = content.rstrip() + "\n\n" + block + "\n"
        reason = "Incorporar el bloque del proyecto respetando el contenido existente; consultar conflictos."
    return {"path": "AGENTS.md", "reason": reason, "proposed_content": proposed,
            "block": block}


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
    previous = load_project(root) if controls[CONFIG_NAME].exists() else None
    config = copy.deepcopy(previous) if previous is not None else {
        "schema_version": 1, "structure": "curso-v2",
        "questionnaire_paths": dict(QUESTIONNAIRE_PATHS),
        "sources": {"selected": False, "include": [], "exclude": []}, "map": None,
    }
    directories = [_safe_path(root, name) for name in project_directories(config)]
    for path in directories:
        if path.exists() and not path.is_dir():
            raise ValueError(f"Colisión con un archivo: {path.relative_to(root)}")
    agents_block = AGENTS_BLOCK_V1 if config["structure"] == "curso-v1" else AGENTS_BLOCK
    leeme_content = LEEME_CONTENT_V1 if config["structure"] == "curso-v1" else LEEME_CONTENT
    if config["structure"] == "curso-v2":
        paths = config.get("questionnaire_paths", {
            "sources": "fuentes/evaluaciones/examenes", "created": "creados/examenes"})
        for key, default in QUESTIONNAIRE_PATHS.items():
            agents_block = agents_block.replace(default + "/", paths[key] + "/")
            leeme_content = leeme_content.replace(default + "/", paths[key] + "/")
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
        proposal = _proposal(controls["AGENTS.md"].read_text(encoding="utf-8"), agents_block)
        if proposal:
            proposals.append(proposal)
    if controls["LEEME.md"].exists() and controls["LEEME.md"].read_text(encoding="utf-8") != leeme_content:
        proposals.append({"path": "LEEME.md", "reason": "Conservar la guía existente; integrar esta propuesta solo tras revisión.",
                          "proposed_content": leeme_content})
    create = [path.relative_to(root).as_posix() + "/" for path in directories if not path.exists()]
    new_files = {}
    if not controls["AGENTS.md"].exists():
        new_files["AGENTS.md"] = "# Instrucciones del proyecto docente\n\n" + agents_block + "\n"
    if not controls["LEEME.md"].exists():
        new_files["LEEME.md"] = leeme_content
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
            if _source_path_allowed(root, config, path) is None:
                report["excluded_entries"] += 1
                continue
            try:
                if entry.is_dir(follow_symlinks=False):
                    walk(path)
                elif entry.is_file(follow_symlinks=False):
                    if not source_allowed(root, config, path):
                        report["excluded_entries"] += 1
                        continue
                    seen_files += 1
                    if _readable(path):
                        report["files"].append(path.relative_to(root).as_posix())
                    else:
                        report["inaccessible"].append(path.relative_to(root).as_posix())
                else:
                    report["inaccessible"].append(path.relative_to(root).as_posix())
            except OSError:
                report["inaccessible"].append(path.relative_to(root).as_posix())

    if _source_path_allowed(root, config, folder) is not None:
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
        for relative in project_directories(config):
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
