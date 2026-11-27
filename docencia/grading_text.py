"""Assessment diagnostic translations. Moodle headers, identifiers and evidence are data."""

from .language_context import current_language

_ENGLISH = {
    "Perfil Moodle":
        "Moodle profile",
    "Versión de perfil Moodle no compatible.":
        "Unsupported Moodle profile version.",
    "profile debe ser worksheet o gradebook.":
        "profile must be worksheet or gradebook.",
    "Las columnas configuradas deben ser distintas.":
        "Each configured column must be distinct.",
    "grade_max debe ser positivo; esta versión admite escalas numéricas desde cero.":
        "grade_max must be positive. Numeric scales start at zero.",
    "decimals debe ser un entero entre 0 y 8.":
        "decimals must be an integer from 0 to 8.",
    "grade_max no se puede representar con los decimales declarados.":
        "grade_max cannot be represented with the specified number of decimal places.",
    "rounding debe ser half_up, half_even o down.":
        "rounding must be half_up, half_even or down.",
    "decimal_separator debe ser punto o coma.":
        "decimal_separator must be a period or a comma.",
    "advanced_grading debe ser un booleano.":
        "advanced_grading must be a boolean.",
    "El perfil worksheet debe declarar advanced_grading explícitamente.":
        "A worksheet profile must explicitly declare advanced_grading.",
    "Ruta de documento de actividad":
        "Activity document path",
    "Los documentos de actividad deben usar rutas relativas portables.":
        "Activity documents must use portable relative paths.",
    "El registro o un documento de actividad sale de la raíz del curso, también mediante enlaces.":
        "The activity record or a linked document points outside the course.",
    "El registro de actividad debe usar schema_version: 1.":
        "The activity record requires schema_version 1.",
    "Identificador del registro de actividad":
        "Activity record identifier",
    "Versión del registro de actividad":
        "Activity record version",
    "activity_version de la evaluación":
        "Assessment activity_version",
    "La identidad o versión de la actividad no coincide con el registro utilizado para corregir.":
        "The activity identifier or version does not match the record used for marking.",
    "El registro de actividad necesita files.":
        "The activity record requires files.",
    "files.templates debe ser una lista.":
        "files.templates must be a list.",
    "Evaluación":
        "Assessment",
    "Versión de evaluación no compatible.":
        "Unsupported assessment version.",
    "sources debe ser una lista de localizadores de los criterios docentes.":
        "sources must list the locations of the teacher's criteria.",
    "Se necesita una rúbrica no vacía para calcular notas.":
        "A rubric with at least one criterion is required to calculate grades.",
    "Criterio":
        "Criterion",
    "Identificador de criterio":
        "Criterion identifier",
    "La rúbrica contiene criterios repetidos.":
        "The rubric contains duplicate criteria.",
    "Máximos y pesos de criterios deben ser positivos.":
        "Criterion maxima and weights must be positive.",
    "Los pesos de la rúbrica deben sumar exactamente 100.":
        "Rubric weights must add up to exactly 100.",
    "evaluations debe ser una lista no vacía.":
        "evaluations must be a nonempty list.",
    "Valoración":
        "Assessment entry",
    "La valoración debe ser individual o de un grupo explícito.":
        "Each assessment must refer to an individual or an explicitly identified group.",
    "El grupo debe declarar sus identificadores de miembros.":
        "The group must list its member identifiers.",
    "Identificador de miembro":
        "Member identifier",
    "Un grupo contiene miembros repetidos.":
        "A group contains duplicate members.",
    "Estado de valoración desconocido.":
        "Unknown assessment status.",
    "Justificación":
        "Justification",
    "Una entrega pendiente, ausente o ilegible no puede incluir puntuaciones.":
        "A pending, absent or unreadable submission cannot have scores.",
    "feedback debe ser texto.":
        "feedback must be text.",
    "Feedback para el estudiante":
        "Student feedback",
    "La valoración evaluada debe incluir evidencias y puntuaciones por criterio.":
        "A marked submission needs evidence and scores for each criterion.",
    "Valoración de criterio":
        "Criterion assessment",
    "La valoración contiene un criterio desconocido o duplicado.":
        "The assessment contains an unknown or duplicate criterion.",
    "La puntuación de un criterio queda fuera de su intervalo.":
        "A criterion score is outside its permitted range.",
    "Cada criterio necesita evidencias textuales no vacías con su localización.":
        "Each criterion needs written evidence and its location.",
    "Faltan criterios de la rúbrica en la valoración.":
        "The assessment is missing one or more rubric criteria.",
    "total_points no coincide con la suma de puntuaciones por criterio.":
        "total_points does not match the sum of criterion scores.",
    "La nota redondeada queda fuera de la escala declarada.":
        "The rounded grade falls outside the declared scale.",
    "La salida debe estar fuera del paquete instalado.":
        "Choose an output folder outside the installed package.",
    "La actividad o convocatoria de la evaluación no coincide con el perfil Moodle.":
        "The assessed activity or assessment period does not match the Moodle profile.",
    "Faltan columnas declaradas del perfil Moodle.":
        "The CSV is missing columns specified in the Moodle profile.",
    "El CSV no contiene filas de participantes.":
        "The CSV has no participant rows.",
    "El mismo grupo tiene varias valoraciones para esta convocatoria.":
        "A group has multiple assessments for this period.",
    "Un participante tiene varias valoraciones individuales o grupales.":
        "A participant has multiple individual or group assessments.",
    "Identificador del CSV":
        "CSV identifier",
    "Identificador repetido para la misma actividad y convocatoria.":
        "Duplicate identifier for the same activity and assessment period.",
    "Fila conservada: no hay valoración de esta entrega.":
        "Row preserved because this submission has no assessment.",
    "No hay una fila Moodle inequívoca para la valoración.":
        "No unique Moodle row matches the assessment.",
    "Ya existe el archivo de salida; no se sobrescribe.":
        "The output file already exists. Choose another destination.",
    "La salida coincide con una entrada; no se modifica.":
        "The destination is an input file. Choose another destination.",
    "No queda un nombre libre para el informe de evaluación.":
        "No unused filename is available for the assessment report.",
    "No se exportan calificaciones: ":
        "Could not export grades: ",
    "No se encontró proyecto-docente.json en los antecesores del perfil. Se comprobaron archivos y versiones, pero no el confinamiento a una raíz de curso.":
        "No course configuration was found above the profile. File and version checks ran, but the course boundary could not be verified.",
    "Sin activity_record: se comprobaron actividad y convocatoria del lote, pero no la versión ni los documentos de un registro de actividad.":
        "No activity_record was provided. The activity and assessment period were checked. The version and linked documents could not be verified.",
    "Moodle no permite subir notas y feedback mediante la hoja sin conexión con rúbrica o guía de evaluación avanzada activada. Conserva el análisis y acuerda el procedimiento con el docente; no se cambia a libro de calificaciones.":
        "An offline worksheet cannot import grades and feedback when advanced grading uses a rubric or marking guide. Keep the assessment and agree the import procedure with the teacher.",
    "{label} debe ser un objeto JSON.":
        "{label} must be a JSON object.",
    "{label}: campos ausentes {missing}; campos desconocidos {extra}.":
        "{label}: missing fields {missing}, unknown fields {extra}.",
    "{label} debe ser un texto no vacío.":
        "{label} must be nonempty text.",
    "{label} tiene espacios externos; confirma el identificador exacto.":
        "{label} has leading or trailing whitespace. Confirm the exact identifier.",
    "No se pudo guardar el informe de evaluación: {exc}":
        "Could not save the assessment report: {exc}",
    "No existe un archivo regular para el documento registrado: {relative}.":
        "The registered document is missing or is not a regular file: {relative}.",
    "El documento {label} necesita la audiencia {audience}.":
        "Document {label} requires audience {audience}.",
    "No se puede crear la carpeta de salida: {exc}":
        "Could not create the output folder: {exc}",
    "Se conservan nota y comentario para una entrega {status}.":
        "Grade and comment preserved for a submission marked {status}.",
    "calificaciones":
        "grades",
}


def message(text):
    return _ENGLISH[text] if current_language() == "en" else text
