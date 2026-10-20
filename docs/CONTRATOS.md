# Contratos de datos, versión 1

Los contratos de banco, examen y feedback usan JSON UTF-8 y `schema_version: 1`.
Las rutas incluidas en un manifiesto son relativas a su carpeta. Los módulos
Python usan diccionarios JSON. El contrato independiente de
`proyecto-docente.json` y sus rutas relativas al curso está en
[Proyecto docente](PROYECTO-DOCENTE.md); `fuentes.json` conserva la versión 2
descrita en [Mapa docente](MAPA-DOCENTE.md).

## Banco

`docencia.gift.parse_gift(text)` devuelve una lista de preguntas. Cada pregunta
tiene `id` (título GIFT único), `category`, `prompt`, `format` y `type`.
Tipos: `single`, `multiple`, `truefalse`, `numerical`, `matching`.
Opciones: `options: [{text, weight, feedback}]`, peso porcentual numérico.
Verdadero/falso: `true_answer: bool`. Numéricas: `numerical: [{value, tolerance,
weight, feedback}]` o `{min, max, weight, feedback}` para intervalos.
Emparejamiento: `matches: [{left, right}]`. `feedback` general es opcional.
Los textos se devuelven con escapes GIFT decodificados. Los errores usan
`GiftError(ValueError)`. `escape_gift(text)` protege caracteres GIFT especiales.

Los metadatos opcionales del banco son
`{schema_version: 1, questions: {id: {concepts: [...], objective: ..., guidance:
...}}, concepts: {concept: {label: ..., guidance: ...}}}`. No se inventan
consejos ni conceptos cuando no están disponibles.

## Examen

El manifiesto contiene `schema_version`, `title`, `seed`, `bank_sha256`,
`bank_snapshot` (ruta), `metadata` (copia del objeto anterior), `models`.
Cada modelo tiene `id`, `questions`, `files` y `pdf_status`.
Cada pregunta tiene `number`, `source_id`, `source_category`, `concepts`, `type`,
`prompt`, `format`; opcionalmente `options` o `numerical`.
Cada opción: `{label, text, weight, source_index}`. En verdadero/falso se conserva
`type: truefalse`, pero Moodle recibe dos opciones de selección única.
`files`: `student_html`, `teacher_html`, `gift`, y PDF solo si se generaron.
La representación de preguntas ordenadas es la única fuente de todas las salidas.

## Feedback

`docencia.feedback.build_feedback(manifest_path, input_paths, config_path,
output_dir, *, detailed=False, consolidated=False)` devuelve un informe JSON.
La configuración JSON contiene `identifier_column`, `model_column`,
`feedback_column`, `status_column`, `absent_values`, `blank_values`,
`question_columns` (mapa de número como cadena a nombre de columna),
`max_scores` (mapa de número a máximo), y opcionalmente `answer_columns`.
Las puntuaciones pueden ser específicas de modelo mediante `models: {id:
{question_columns, max_scores, answer_columns}}`, que sustituye esos mapas.
Estado no presentado y celda vacía son distintos de columna ausente.
`blank_values` contiene únicamente tokens de celda de puntuación declarados
expresamente como respuesta en blanco; su valor predeterminado es `[]`. Una
celda vacía sigue siendo dato ausente aunque el intento figure terminado,
salvo que el docente incluya expresamente `""` en `blank_values`.
`delimiter` es opcional; se detecta coma, punto y coma o tabulador. Las notas
originales y las columnas no relacionadas se conservan. No se resuelven
silenciosamente duplicados entre archivos/modelos.
El informe tiene `status`, `outputs`, `incidents`, `students`, `manifest_sha256`.
Datos obligatorios ambiguos o incompletos impiden exportar CSV; siempre se guarda el informe.
El detalle requiere `answer_columns` para cada pregunta. Una selección vacía o
no interpretable produce aviso y conserva feedback conceptual; no se inventa
una elección. Los consolidados requieren mismas columnas, orden y dialecto.
Las salidas son `modelo_<id>_CORREGIDO.csv`, opcionalmente
`CONSOLIDADO_CORREGIDO.csv`, y `feedback-report.json` (con sufijo si ya existe).
