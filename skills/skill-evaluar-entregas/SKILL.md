---
name: skill-evaluar-entregas
description: Evaluar trabajos, prácticas, informes o notebooks entregados por estudiantes con el enunciado y una rúbrica explícita, y redactar feedback basado en evidencias. No usar para crear materiales, procesar respuestas de exámenes ofuscados ni atribuir plagio o uso de IA sin pruebas.
---

# Evaluar entregas

Aplicar los criterios del profesor a evidencias de cada entrega. No deducir una política de evaluación ni una sanción a partir del estilo del texto o de una respuesta inesperada.

## Preparar la evaluación

Leer el enunciado vigente, la rúbrica, las restricciones de la actividad y, si existe, la guía docente. Confirmar la identidad mediante el identificador acordado para el encargo o el institucional disponible, sin emparejar personas por un nombre parecido. Examinar únicamente las entregas necesarias para el encargo.

Si no existe rúbrica suficiente, proponer criterios antes de asignar calificaciones definitivas. Se puede avanzar con un análisis cualitativo explícitamente provisional. Usar la [referencia de evaluación](references/evaluacion.md) para extracción, evidencias y casos ambiguos.

## Flujo

1. Inventariar las entregas incluidas y sus identificadores. Separar ausencias, archivos ilegibles y entregas válidas; una falla de extracción no es una respuesta incorrecta.
2. Leer contenido y anexos pertinentes. En notebooks, examinar texto, código y salidas; no ejecutar automáticamente código de estudiantes. Una respuesta puede estar en un bloque de código o junto al texto de la pregunta.
3. Evaluar por criterio, registrando evidencia concreta: sección, página, celda o fragmento breve. Reconocer alternativas correctas aunque no coincidan con la solución docente.
4. Calcular la nota solo con la escala y ponderación establecidas. Comprobar sumas, máximos, penalizaciones autorizadas y coherencia entre casos comparables. No recalibrar notas por una distribución esperada sin instrucción del profesor.
5. Redactar feedback breve: logro observado, dificultad sustentada y siguiente acción de mejora. No mencionar la nota dentro del comentario por defecto si ya existe una columna destinada a ella.
6. Preparar informe docente y, si se solicita, una copia del CSV de calificaciones. Conservar identificadores y columnas ajenas al cambio; modificar notas únicamente cuando la evaluación lo requiera expresamente. Registrar incidencias antes de importar.
7. Entregar resultados para revisión docente. La importación en Moodle es manual y sigue la [guía de Moodle](../../docs/MOODLE.md). El comando `build-feedback` procesa cuestionarios con manifiesto; no corrige ensayos ni aplica esta rúbrica automáticamente.

## Cierre

Entregar una tabla de evaluación por criterio o el formato pedido, comentarios individuales y un resumen de dificultades del grupo sin exponer datos innecesarios. Distinguir notas calculadas, casos pendientes y comprobaciones no realizadas. Para informes extensos, entregar Markdown y PDF cuando el entorno permita verificarlo.
