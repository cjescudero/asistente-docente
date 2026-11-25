---
name: actividades-evaluacion
description: Evaluar actividades, trabajos, informes o notebooks descargados de Moodle con su enunciado, rúbrica y resolución disponibles; generar puntuaciones justificadas y feedback en un CSV para importar en Moodle. No usar para crear materiales, procesar cuestionarios ofuscados ni atribuir uso de IA sin pruebas.
---

# Actividades: evaluación

Aplicar los criterios del profesor a evidencias de cada entrega. No deducir una política de evaluación ni una sanción a partir del estilo del texto o de una respuesta inesperada.

Combinar este encargo con [español conciso](../espanol-conciso-redaccion/SKILL.md) solo si el docente pide esa skill o el estilo de español simplificado, incluido un encargo expreso para todo el curso.

## Contexto del proyecto

Resolver las rutas desde los espacios asignados del curso. Los nombres de carpeta de los ejemplos corresponden a la configuración inicial. Si hay varias raíces posibles, reutilizar la decisión del encargo o preguntar por el destino. Consultar el catálogo por identidad y versión cuando el trabajo dependa de materiales persistentes.

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

Ante dudas sobre el uso, flujo, archivos o resultados del plugin, o preguntas
sobre siguientes pasos y posibilidades, invocar
[Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) antes de responder.
Transferirle el objetivo, las decisiones conocidas y los resultados de esta tarea;
tras resolver la duda, retomar el encargo ya autorizado.


En `curso-v4`, organizar el lote en `Entregas/<actividad>/<convocatoria>/`,
con el mismo identificador y nombre de carpeta que la actividad. Guardar los
trabajos en `recibidos/entregas/`, la hoja Moodle original en `recibidos/` y las
correspondencias explícitas, cuando sean necesarias, en `recibidos/identificacion/`.
`correccion/` contiene evaluaciones, CSV modificados, auditoría e incidencias.
Reutilizar el lote preparado y su LEEME; si falta, prepararlo dentro del encargo
de evaluación según [Recepción y corrección](../../docs/ACTIVIDADES.md#recepción-y-corrección).
La convocatoria distingue entrega ordinaria, recuperación u otros lotes acordados.
Conservar originales intactos y distinguir entrada de salida. Respetar los destinos explícitos. Todo el lote queda fuera de la wiki;
esa exclusión no impide la evaluación expresamente solicitada.

## Preparar la evaluación

Usar el enunciado definitivo y las modificaciones comunicadas por el profesor. Respetar el formato libre cuando se haya acordado. Un plan preliminar, una herramienta opcional o el formato de la solución no añaden requisitos. Leer el enunciado utilizado, la rúbrica, las restricciones y la resolución o guía
disponibles. Si existe `actividad.json`, comprobar su versión y los archivos
asociados conforme al [registro de actividad](../../docs/ACTIVIDADES.md).
Confirmar la identidad mediante identificadores explícitos, sin emparejar personas
por parecido de nombres. Para grupos, requerir la correspondencia grupo–miembros
y la regla docente para repartir la calificación. Examinar solo el lote solicitado.

Si no existe rúbrica suficiente, proponer criterios antes de asignar calificaciones definitivas. Se puede avanzar con un análisis cualitativo explícitamente provisional. Usar la [referencia de evaluación](references/evaluacion.md) para extracción, evidencias y casos ambiguos.

## Formato de entrada y entrega para Moodle

Entregar un CSV importable con las notas y el feedback cuando el destino sea Moodle. Preparar un Excel adicional únicamente si el docente lo pide para revisión.

Partir de la exportación original de Moodle para la vía elegida. Si el único
original disponible es Excel, aprovechar una copia convertida a CSV cuando
se puedan verificar filas, identificadores, encabezados, ceros iniciales y
valores. Mantener la vía acordada. Si falta una correspondencia verificable,
dejar pendiente la exportación afectada y continuar el análisis cualitativo.

Para el libro de calificaciones, preferir el correo de la exportación vigente
cuando esté disponible y sea único en el lote. Conservar el valor exacto y
comprobar su correspondencia con la entrega. La hoja sin conexión de una tarea
usa su propio identificador de participante.

## Flujo

1. Inventariar las entregas y la exportación Moodle elegida: hoja de calificación sin conexión de una tarea o CSV del libro de calificaciones. Distinguir su identificador de participante del ID de usuario; no intercambiarlos. Resolver correspondencias con archivos explícitos cuando proceda. Separar ausencias, archivos ilegibles y entregas válidas; una falla de extracción no es una respuesta incorrecta.
2. Leer contenido y anexos pertinentes. En notebooks, examinar texto, código y salidas; no ejecutar automáticamente código de estudiantes. Una respuesta puede estar en un bloque de código o junto al texto de la pregunta.
3. Evaluar por criterio, registrando evidencia concreta: sección, página, celda o fragmento breve. Reconocer alternativas correctas aunque no coincidan con la solución docente.
4. Calcular la nota solo con la escala y ponderación establecidas. Comprobar sumas, máximos, penalizaciones autorizadas y coherencia entre casos comparables. No recalibrar notas por una distribución esperada sin instrucción del profesor.
5. Revisar cada descuento y cada máxima calificación con el mismo criterio. Preparar un informe reservado por actividad y sintetizar sus motivos en el comentario individual que acompañará a la nota en Moodle. Aplicar las pautas y el ejemplo de la [referencia de evaluación](references/evaluacion.md#revisar-las-calificaciones).
6. Guardar la evaluación estructurada con evidencias por criterio y preparar el perfil de columnas según [Calificaciones de actividades](../../docs/CALIFICACIONES.md). El agente y el profesor valoran las evidencias; la utilidad comprueba cálculos, correspondencias y exportación, sin corregir los trabajos por sí misma.
7. Generar la copia CSV con nota y comentario de los casos evaluados, preservando filas, identificadores y columnas ajenas. En el CSV, escribir los comentarios nuevos en una sola línea sin recortar el contenido y verificar que el archivo se relee con la codificación y el separador indicados. Registrar valor anterior, valor nuevo y justificación. Los datos obligatorios inconsistentes o correspondencias ambiguas bloquean la exportación; conservar el análisis cualitativo para resolverlas. No transformar entregas ausentes, ilegibles o pendientes en cero.
8. Entregar evaluación por criterio, CSV, registro de cambios e incidencias para revisión docente. Indicar qué codificación y separador usar. En el libro, explicar los dos desplegables de identificación y el destino de cada par de columnas. Si se usa correo, elegir la columna «Dirección de correo» en «Mapa desde» y el campo «Dirección de correo» en «Mapa a». Vincular «(Real)» con la actividad existente y «(Retroalimentación)» con «Retroalimentación para» esa misma actividad. Seguir la [guía de importación](../../docs/MOODLE.md#importar-notas-y-comentarios-en-el-libro) para revisar los valores por defecto, la vista previa y el resultado. Si se usa la hoja sin conexión, comprobar las restricciones de calificación avanzada descritas en la [guía Moodle](../../docs/MOODLE.md#entregas-de-actividades).

## Cierre

Entregar una tabla de evaluación por criterio o el formato pedido, comentarios individuales y un resumen de dificultades del grupo sin exponer datos innecesarios. Distinguir notas calculadas, casos pendientes y comprobaciones no realizadas. Para informes extensos, entregar Markdown y PDF cuando el entorno permita verificarlo.

Para feedback de cuestionarios ya puntuados con un manifiesto, usar
[generar feedback](../cuestionarios-observaciones-calificaciones-alumnado/SKILL.md). Esa tarea conserva
las notas existentes; la corrección de entregas usa las puntuaciones justificadas
de esta evaluación.

## Sugerir el siguiente paso

Invocar [Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) para preparar
el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md), una sola vez
por respuesta y reutilizando el contexto y las comprobaciones disponibles:
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Priorizar revisar incidencias y preparar la importación manual del CSV ya generado. Si resulta útil, ofrecer una actividad o material de refuerzo basado en dificultades agregadas, sin incorporar datos personales a la wiki.
