"""Course setup, folder and source diagnostics for teachers."""

from .language_context import current_language

_ENGLISH = {
    "AGENTS.md debe ser un archivo regular.":
        "AGENTS.md must be a regular file.",
    "Cambió la asignación de fuentes durante el registro. Revisa el mapa.":
        "Source assignments changed during registration. Review the map.",
    "Cambió la selección del corpus; repetir la reconciliación.":
        "Source selection changed. Run reconciliation again.",
    "Clave JSON duplicada: {key}":
        "Duplicate JSON key: {key}",
    "Colisión con un archivo en la ruta: {relative}":
        "The path conflicts with a file: {relative}",
    "Colisión con un archivo: {relative}":
        "A file already occupies this path: {relative}",
    "Configuración del proyecto: {exc}":
        "Course configuration: {exc}",
    "Dos configuraciones sin registro de adopción: aclarar con el docente.":
        "Two configurations were found without an adoption record. Confirm the active configuration with the teacher.",
    "El destino no pertenece al espacio {role}: {destination}":
        "The destination is outside the {role} space: {destination}",
    "El espacio solicitado debe estar asignado en curso-v4: {role}.":
        "Assign the requested space in the course configuration: {role}.",
    "El mapa debe estar dentro de la raíz del curso.":
        "The map must be inside the course root.",
    "El mapa debe quedar separado de las notas del curso.":
        "Keep the course map separate from course notes.",
    "El mapa debe usar una ruta dentro del curso.":
        "Use a map path within the course.",
    "El mapa necesita un index.md real antes de registrarse.":
        "Create the map's index.md before registering it.",
    "El proyecto docente debe estar fuera de la instalación del plugin.":
        "Choose a course folder outside the installed plugin.",
    "Elegir al menos una carpeta para el espacio {role}.":
        "Choose at least one folder for the {role} space.",
    "Elige una de las carpetas para {role}: ":
        "Choose one of the folders for {role}: ",
    "Espacio reservado: {relative}":
        "Reserved space: {relative}",
    "Falta el estado de mapa del curso.":
        "The course map status is missing.",
    "Falta {CONFIG_NAME}; inicia el proyecto o indica la raíz correcta.":
        "Missing {CONFIG_NAME}. Set up the course or choose its root folder.",
    "Fuentes fuera de la selección o del acceso autorizado: ":
        "Sources outside the selection or permitted access: ",
    "Hay dos carpetas de gestión del proyecto. Aclara cuál está activa.":
        "Multiple project management folders were found. Choose which one is active.",
    "Identidades de selección del corpus no válidas.":
        "Invalid source selection identities.",
    "Identificador físico de selección no válido.":
        "Invalid physical identifier in the source selection.",
    "La raíz de fuentes {root_id} pertenece a las notas del curso.":
        "Source root {root_id} belongs to course notes.",
    "La raíz del proyecto debe ser una carpeta.":
        "The course root must be a directory.",
    "La raíz del proyecto no puede ser un enlace simbólico.":
        "The course root cannot be a symbolic link.",
    "La salida debe estar en el mismo proyecto que sus entradas.":
        "The output must be in the same course as its inputs.",
    "La selección de fuentes está pendiente; elegir el corpus antes de reutilizar el mapa.":
        "Select sources before reusing the course map.",
    "La selección del corpus requiere sources.selected.":
        "Source selection requires sources.selected.",
    "La selección pendiente requiere listas vacías.":
        "Pending source selection requires empty lists.",
    "La wiki debe ubicarse dentro del espacio generado.":
        "Place the wiki inside the generated materials space.",
    "La wiki no puede solaparse con las fuentes, las entregas ni las notas del curso.":
        "Keep the wiki separate from course materials, submissions and course notes.",
    "Las raíces de los espacios deben ser independientes: {relative}":
        "Space roots must be separate: {relative}",
    "Mapa no válido: ":
        "Invalid course map: ",
    "No se pudo ocultar la carpeta de gestión: {directory}":
        "Could not hide the management folder: {directory}",
    "No se pudo verificar la selección: ":
        "Could not verify the selected sources: ",
    "No se puede comprobar {name}: {exc}":
        "Unable to check {name}: {exc}",
    "No se puede leer {CONFIG_NAME}: {exc}":
        "Could not read {CONFIG_NAME}: {exc}",
    "No se puede sustituir un enlace simbólico: {path.name}":
        "Cannot replace a symbolic link: {path.name}",
    "Página fuera del mapa o con una identidad compartida: {name}":
        "Page outside the course map or with a shared identity: {name}",
    "Páginas pendientes de revisión antes de reutilizar: ":
        "Review these pages before reuse: ",
    "Ruta de identidad no normalizada.":
        "Identity path is not normalised.",
    "Ruta insegura o enlace simbólico: {relative}":
        "Unsafe path or symbolic link: {relative}",
    "Se esperaba un registro de identidades por ruta.":
        "Expected a record of identities for each path.",
    "Seleccionar solo carpetas del espacio de material de la asignatura: {relative}":
        "Choose a folder within the course materials space: {relative}",
    "map requiere un índice real.":
        "The course map requires an existing index.",
    "schema_version debe ser 1.":
        "schema_version must be 1.",
    "spaces debe ser un objeto con las carpetas asignadas.":
        "spaces must be an object assigning folders to roles.",
    "spaces requiere sources, generated y submissions; notes es opcional.":
        "spaces requires sources, generated and submissions. The notes space is optional.",
    "{CONFIG_NAME} en la raíz entra en conflicto con {CONFIG_V3}; aclara su función antes de iniciar el proyecto.":
        "The root file {CONFIG_NAME} conflicts with {CONFIG_V3}. Clarify its role before setting up the course.",
    "{label} contiene rutas duplicadas.":
        "{label} contains duplicate paths.",
    "{label} debe ser una lista de rutas relativas.":
        "{label} must list relative paths.",
    "{label}: la ruta debe permanecer dentro del proyecto.":
        "{label}: the path must stay inside the course.",
    "{label}: no se admiten patrones glob; indica rutas exactas.":
        "{label}: specify exact paths. Wildcards are not supported.",
    "{label}: se requiere una ruta relativa con separadores '/'.":
        "{label}: use a relative path with '/' separators.",
}


def diagnostic(text, **values):
    template = _ENGLISH[text] if current_language() == "en" else text
    return template.format(**values) if values else template
