---
name: actividades-evaluacion
description: Evaluar actividades, trabajos, informes o notebooks descargados de Moodle con su enunciado, rúbrica y resolución disponibles; generar puntuaciones justificadas y feedback en una copia de la hoja Moodle. No usar para crear materiales, procesar cuestionarios ofuscados ni atribuir uso de IA sin pruebas.
---

# Actividades: evaluación

Aplicar los criterios del profesor a evidencias de cada entrega. No deducir una política de evaluación ni una sanción a partir del estilo del texto o de una respuesta inesperada.

Usar por defecto [español conciso](../espanol-conciso-redaccion/SKILL.md) en la
conversación y los documentos, salvo que el profesor indique otro idioma o estilo.
Respetar citas, identificadores y términos que deban conservarse literalmente.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

En `curso-v2`, organizar el lote en `resultados/<actividad>/<convocatoria>/`,
con `recibidos/` para originales descargados y archivos de identificación y
`correccion/` para evaluaciones, CSV modificados, auditoría e incidencias.
Conservar originales intactos y distinguir entrada de salida. Respetar las rutas
de cursos `curso-v1` y destinos explícitos. Todo el lote queda fuera de la wiki;
esa exclusión no impide la evaluación expresamente solicitada.

## Preparar la evaluación

Leer el enunciado utilizado, la rúbrica, las restricciones y la resolución o guía
disponibles. Si existe `actividad.json`, comprobar su versión y los archivos
asociados conforme al [registro de actividad](../../docs/ACTIVIDADES.md).
Confirmar la identidad mediante identificadores explícitos, sin emparejar personas
por parecido de nombres. Para grupos, requerir la correspondencia grupo–miembros
y la regla docente para repartir la calificación. Examinar solo el lote solicitado.

Si no existe rúbrica suficiente, proponer criterios antes de asignar calificaciones definitivas. Se puede avanzar con un análisis cualitativo explícitamente provisional. Usar la [referencia de evaluación](references/evaluacion.md) para extracción, evidencias y casos ambiguos.

## Flujo

1. Inventariar las entregas y la exportación Moodle elegida: hoja de calificación sin conexión de una tarea o CSV del libro de calificaciones. Distinguir su identificador de participante del ID de usuario; no intercambiarlos. Resolver correspondencias con archivos explícitos cuando proceda. Separar ausencias, archivos ilegibles y entregas válidas; una falla de extracción no es una respuesta incorrecta.
2. Leer contenido y anexos pertinentes. En notebooks, examinar texto, código y salidas; no ejecutar automáticamente código de estudiantes. Una respuesta puede estar en un bloque de código o junto al texto de la pregunta.
3. Evaluar por criterio, registrando evidencia concreta: sección, página, celda o fragmento breve. Reconocer alternativas correctas aunque no coincidan con la solución docente.
4. Calcular la nota solo con la escala y ponderación establecidas. Comprobar sumas, máximos, penalizaciones autorizadas y coherencia entre casos comparables. No recalibrar notas por una distribución esperada sin instrucción del profesor.
5. Redactar feedback breve: logro observado, dificultad sustentada y siguiente acción de mejora. No mencionar la nota dentro del comentario por defecto si ya existe una columna destinada a ella.
6. Guardar la evaluación estructurada con evidencias por criterio y preparar el perfil de columnas según [Calificaciones de actividades](../../docs/CALIFICACIONES.md). El agente y el profesor valoran las evidencias; la utilidad comprueba cálculos, correspondencias y exportación, sin corregir los trabajos por sí misma.
7. Generar una copia de la hoja elegida con nota y comentario de los casos evaluados, preservando filas, identificadores y columnas ajenas. Registrar valor anterior, valor nuevo y justificación. Los datos obligatorios inconsistentes o correspondencias ambiguas bloquean la exportación; conservar el análisis cualitativo para resolverlas. No transformar entregas ausentes, ilegibles o pendientes en cero.
8. Entregar evaluación por criterio, CSV, registro de cambios e incidencias para revisión docente. La importación es manual. Distinguir una rúbrica local de la calificación avanzada configurada en Moodle y comprobar las limitaciones de cada vía conforme a la [guía Moodle](../../docs/MOODLE.md); no cambiar de procedimiento automáticamente.

## Cierre

Entregar una tabla de evaluación por criterio o el formato pedido, comentarios individuales y un resumen de dificultades del grupo sin exponer datos innecesarios. Distinguir notas calculadas, casos pendientes y comprobaciones no realizadas. Para informes extensos, entregar Markdown y PDF cuando el entorno permita verificarlo.

Para feedback de cuestionarios ya puntuados con un manifiesto, usar
[generar feedback](../cuestionarios-observaciones-calificaciones-alumnado/SKILL.md). Esa tarea conserva
las notas existentes; la corrección de entregas usa las puntuaciones justificadas
de esta evaluación.

## Sugerir el siguiente paso

Aplicar el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md):
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Priorizar revisar incidencias y preparar la importación manual del CSV ya generado. Si resulta útil, ofrecer una actividad o material de refuerzo basado en dificultades agregadas, sin incorporar datos personales a la wiki.
