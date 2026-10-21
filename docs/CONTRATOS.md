# Contratos de datos, versión 1

Los contratos usan JSON UTF-8 y declaran su versión. Las rutas incluidas en un
manifiesto son relativas a su carpeta, salvo que su contrato indique otra base.
Los módulos Python usan diccionarios JSON. El contrato independiente de
`proyecto-docente.json` y sus rutas relativas al curso está en
[Proyecto docente](PROYECTO-DOCENTE.md); `fuentes.json` conserva la versión 2
descrita en [Mapa docente](MAPA-DOCENTE.md).

## Actividad y calificación

El registro documental `actividad.json` utiliza `schema_version: 1`, identificador
estable, versión, título, objetivos, fuentes y archivos por audiencia. Relaciona
enunciado, plantillas, rúbrica y guía docente disponibles. El contrato y la
plantilla se describen en [Actividades](ACTIVIDADES.md).

La corrección estructurada de entregas y su perfil Moodle tienen un contrato
distinto, descrito en [Calificaciones](CALIFICACIONES.md). La utilidad verifica
cálculos y correspondencias y exporta sobre una copia del CSV; no determina la
valoración académica ni modifica Moodle.

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

Los metadatos históricos opcionales del banco son
`{schema_version: 1, questions: {id: {concepts: [...], objective: ..., guidance:
...}}, concepts: {concept: {label: ..., guidance: ...}}}`. No se inventan
consejos ni conceptos cuando no están disponibles.

Los bancos nuevos asociados a materiales usan el [catálogo de bancos](BANCOS.md)
y los metadatos de procedencia, localizadores, conceptos, objetivos, dificultad
y repaso allí especificados. El catálogo enlaza GIFT, metadatos y originales
mediante rutas relativas. Un banco anterior sin estos datos sigue siendo
legible; no basta para prometer una selección equilibrada por información ausente.

## Cuestionario

El manifiesto contiene `schema_version`, `title`, `seed`, `bank_sha256`,
`bank_snapshot` (ruta), `metadata` (copia del objeto anterior), `models`.
Cada modelo tiene `id`, `questions`, `files` y `pdf_status`.
Cada pregunta tiene `number`, `source_id`, `source_category`, `concepts`, `type`,
`prompt`, `format`; opcionalmente `options` o `numerical`.
Cada opción: `{label, text, weight, source_index}`. En verdadero/falso se conserva
`type: truefalse`, pero Moodle recibe dos opciones de selección única.
`files`: `student_html`, `teacher_html`, `gift`, y PDF solo si se generaron.
La representación de preguntas ordenadas es la única fuente de todas las salidas.

La composición desde catálogo amplía esa procedencia para distinguir banco y
pregunta original, conserva los bancos y metadatos utilizados y registra
cobertura, dificultad y reutilización. Sus campos y selección están documentados
en [Bancos](BANCOS.md). La entrada de un solo GIFT y la lectura de manifiestos
anteriores se mantienen.

## Feedback

`build-feedback` recibe manifiesto, resultados detallados, configuración y
carpeta de salida; admite detalle solicitado y consolidado opcional. Devuelve
un informe JSON.
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

La configuración admite `feedback_priority: {max_concepts: 3,
marked_threshold: 0.5, min_evidence: 2}`. Ordena los conceptos por la proporción
de puntos perdidos y las evidencias disponibles. El umbral es estricto: con
los valores predeterminados, menos del 50 % y al menos dos preguntas permite
describir una dificultad acusada; un fallo aislado se presenta como aspecto
a revisar. Las recomendaciones para estudiantes no deben contener recursos
reservados ni soluciones.

El argumento opcional `--gradebook` permite escribir comentarios sobre una copia
de la exportación del libro de calificaciones, cruzada por identificadores
explícitos con el detalle. Se conservan las notas existentes; una nota global
no sustituye las puntuaciones por pregunta ni permite inferir conceptos fallados.
El perfil de este cruce se documenta en [Calificaciones](CALIFICACIONES.md).
