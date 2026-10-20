---
name: preparar-examenes-papel-moodle
description: Seleccionar preguntas de un banco GIFT para modelos de examen en papel y producir PDF, solucionario, GIFT de respuestas ofuscadas y manifiesto coherentes para Moodle. No usar para inventar un banco completo, importar automáticamente en Moodle ni generar feedback de resultados.
---

# Preparar exámenes en papel y Moodle

Generar todos los derivados desde una única representación ordenada del modelo: pregunta impresa, opción visible, puntuación y correspondencia Moodle deben coincidir.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

En un curso inicializado, preparar nuevos materiales en `docente/borradores/`
salvo destino explícito. Pasarlos a `alumnado/` requiere un encargo que incluya
esa entrega; mantener soluciones y criterios docentes separados.

## Flujo

1. Validar el banco y leer objetivos, reglas de selección y metadatos. Acordar número de modelos, preguntas, cobertura y restricciones si faltan. No asumir cuatro modelos ni una cantidad fija por asignatura.
2. Comprobar que el banco permite ese reparto. Evitar repetición entre modelos cuando haya fondo suficiente y mantener cobertura comparable. Si no es posible cumplir la selección, comunicar el motivo sin relajar cuotas silenciosamente.
3. Preparar una salida nueva fuera del plugin. Ejecutar `python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-exams banco.gift --metadata metadatos.json --output examen --title "Evaluación de fuentes" --models 2 --questions 5 --seed 42`. Localizar la raíz instalada en `ASISTENTE_DOCENTE` y resolver las entradas en el espacio del curso. `--metadata` es opcional; la semilla permite reproducir la selección. Usar `--per-category` según la ayuda para cuotas explícitas.
4. Conservar banco congelado, huella y manifiesto junto con los modelos. El manifiesto registra identificadores, categorías, numeración, orden de opciones y pesos; no reconstruir estos datos por semejanza de texto o leyendo solo un PDF.
5. Revisar cada modelo: número y orden de preguntas, letras, unidades, fórmulas, saltos de página y legibilidad. Contrastar papel, solucionario y GIFT con el manifiesto. La respuesta correcta debe permanecer en su posición, también en verdadero/falso y selección múltiple.
6. Entregar PDF de estudiante y solucionario en archivos claramente separados, GIFT ofuscado y manifiesto. Los HTML son derivados útiles para inspección; `--html-only` no completa una petición de PDF.
7. Explicar la importación y configuración manual de [Moodle](../../docs/MOODLE.md): sin barajar preguntas ni respuestas, y sin revelar soluciones o feedback durante la evaluación. Verificar el cuestionario con una cuenta o vista de estudiante antes de usarlo.

## Límites que conservar

- El GIFT ofuscado muestra únicamente números y etiquetas de respuesta. El archivo sigue conteniendo pesos y claves para Moodle; es material docente, no un archivo para entregar a estudiantes.
- En verdadero/falso se generan dos opciones de selección única en el orden impreso. En preguntas numéricas se conserva entrada numérica, valor esperado y tolerancia; no inventar letras para ellas.
- Emparejamiento queda fuera del flujo ofuscado de esta versión. Revisar y comunicar los identificadores excluidos antes de dar la selección por válida.
- Tras aplicar el examen, el feedback debe usar su manifiesto y snapshot, aunque el banco de trabajo haya cambiado.
- La ofuscación reduce la información mostrada en pantalla; no demuestra por sí sola ausencia de consulta externa o de uso de IA.

Consultar [uso](../../docs/USO.md) para rutas, dependencias y comprobaciones. Para resultados posteriores, usar [generar feedback](../generar-feedback-evaluaciones/SKILL.md).
