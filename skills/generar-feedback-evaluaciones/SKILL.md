---
name: generar-feedback-evaluaciones
description: Generar feedback conceptual individual y CSV para reimportar en Moodle desde resultados de cuestionarios, el manifiesto del examen y sus metadatos. No usar para corregir ensayos o notebooks, cambiar calificaciones sin autorización, crear bancos ni reconstruir modelos sin manifiesto.
---

# Generar feedback de evaluaciones

Convertir resultados del examen en orientaciones de aprendizaje trazables. Por defecto, explicar qué conceptos conviene repasar sin revelar preguntas, letras correctas ni soluciones del examen.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

Guardar entregas, notas e informes individuales en `docente/resultados/` del
curso cuando esté inicializado; esos datos quedan fuera de la wiki. No usar
la exclusión del corpus para impedir la evaluación expresamente solicitada.

## Entradas y comprobaciones

Leer el manifiesto oficial, su snapshot y los metadatos conceptuales. Leer encabezados y filas necesarias de los CSV exportados para identificar las columnas; no inspeccionar datos de estudiantes ajenos al encargo. Revisar el [contrato de feedback](../../docs/CONTRATOS.md) y la [guía Moodle](../../docs/MOODLE.md).

La configuración JSON debe identificar la columna de estudiante, modelo, estado y feedback, y mapear preguntas a columnas y máximos. Si distintos modelos usan encabezados o escalas diferentes, usar los mapas por modelo. No deducir el identificador, la escala ni el modelo por el nombre del archivo cuando los datos sean ambiguos.

## Flujo

1. Comprobar integridad del manifiesto y correspondencia de los modelos con la exportación. Usar el banco congelado del examen, no el banco actual del curso.
2. Configurar identificadores como texto, separador y significado de valores vacíos y ausencias. Distinguir cero, respuesta en blanco, no presentado, columna ausente y archivo no legible.
3. Revisar duplicados, estudiantes en varios modelos, columnas necesarias y valores fuera de escala. Registrar incidencias; no elegir silenciosamente una fila ni convertir datos ausentes en errores del estudiante.
4. Ejecutar `python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-feedback examen/manifest.json --input resultados.csv --config feedback.json --output comentarios`. Repetir `--input` para varios archivos. Localizar la raíz instalada en `ASISTENTE_DOCENTE` y resolver las entradas y salidas en el espacio del curso conforme a [uso](../../docs/USO.md).
5. Revisar el informe de incidencias antes de usar un CSV. Los datos obligatorios ambiguos o incompletos impiden exportar CSV; resolver la fuente o la configuración y repetir, sin parchear comentarios a ciegas. En modo detallado, una selección individual vacía o no interpretable genera un aviso y conserva el feedback conceptual, sin inventar una respuesta.
6. Comprobar comentarios de casos representativos: acierto total, fallo parcial, blanco, no presentado y conceptos sin metadatos. No atribuir una causa específica a un fallo si solo se conoce la puntuación.
7. Entregar CSV por modelo, informe de ejecución y, solo si se solicita, consolidado mediante `--consolidated`. El modo `--detailed` requiere petición expresa y datos suficientes; no activarlo por defecto.

## Criterios de salida

Conservar notas, identificadores y columnas ajenas al feedback. Dejar vacío el comentario de no presentados. Cuando falten conceptos u orientaciones, señalar la limitación y no inventar consejos específicos. Los comentarios deben ser respetuosos, breves y accionables, sin incluir información de otras personas.

La importación final es manual: revisar el identificador, la columna de comentarios y la conservación de las notas conforme a la guía Moodle; algunos flujos de importación requieren mapear también la nota original. Generar un CSV no prueba que Moodle lo haya aceptado. Para valorar trabajos abiertos con rúbrica, usar [evaluar entregas](../evaluar-entregas/SKILL.md).
