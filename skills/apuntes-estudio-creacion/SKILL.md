---
name: apuntes-estudio-creacion
description: Crear o revisar apuntes teóricos, guías de estudio y síntesis conceptuales a partir de materiales de una asignatura de cualquier disciplina. No usar para resolver evaluaciones reservadas, redactar enunciados, corregir entregas ni generar bancos GIFT.
---

# Apuntes estudio: creación

Producir un documento autónomo que ayude a comprender y relacionar los conceptos del bloque pedido. El nivel y la profundidad proceden del curso y del encargo, no de una disciplina predeterminada.

Esta skill crea materiales de aprendizaje para el alumnado. Cuando exista un Mapa docente, usarlo para localizar las fuentes pertinentes y contrastar con ellas la explicación. No crear ni mantener aquí el inventario, la wiki o el grafo del curso; esas tareas corresponden a [crear el Mapa docente](../mapa-docente-creacion-visualizacion/SKILL.md).

Usar por defecto [español conciso](../espanol-conciso-redaccion/SKILL.md) en la
conversación y los documentos, salvo que el profesor indique otro idioma o estilo.
Respetar citas, identificadores y términos que deban conservarse literalmente.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

En `curso-v2`, guardar los apuntes en `creados/materiales/<id>/`, con
`material-docente.json` de tipo `material` y estado visible en `LEEME.md`.
Separar notas reservadas de los documentos estudiantiles. Mantener la misma
ubicación cuando los apuntes sirvan después de fuente para otro encargo.
Respetar destinos explícitos y cursos anteriores según el contrato común.

## Flujo

1. Delimitar tema, audiencia y fuentes. Leer los materiales necesarios completos y, si existen, apuntes de la misma serie para conservar notación y continuidad. Priorizar fuentes vigentes autorizadas frente a bancos o cuestionarios anteriores.
2. Extraer conceptos, definiciones, relaciones, supuestos, fórmulas y controversias pertinentes. Distinguir conocimientos de la materia, ejemplos y opiniones atribuidas.
3. Organizar la explicación desde una idea central: propósito del tema, desarrollo por conceptos y relaciones con conocimientos previos. Añadir un glosario solo si reduce una dificultad real.
4. Respetar el idioma del encargo o del curso. Para textos en español, aplicar [español conciso](../espanol-conciso-redaccion/SKILL.md). Explicar nuevos símbolos y condiciones de validez; conservar el rigor adecuado al lector. Un apunte de filosofía puede necesitar argumentos y objeciones; uno de química, modelos, unidades y límites.
5. Incorporar ejemplos breves que resuelvan dificultades concretas. Si las fuentes son prácticas evaluadas, extraer la teoría sin copiar soluciones reservadas ni convertir el apunte en una secuencia para superar esa evaluación.
6. Revisar cobertura, atribuciones, consistencia de términos y exactitud contra las fuentes. Mantener referencias suficientes para comprobar afirmaciones especializadas o citas; no inventar bibliografía.
7. Entregar Markdown y PDF por defecto mediante `python "$ASISTENTE_DOCENTE/scripts/docencia.py" render-markdown apuntes.md --output salida`. Localizar la raíz instalada del plugin en `ASISTENTE_DOCENTE` y resolver entradas y salidas en el espacio del curso; consultar [uso](../../docs/USO.md). Identificar cualquier PDF pendiente de renderizar o revisar.

## Alcance y calidad

- Simplificar lenguaje no autoriza a convertir una reescritura completa en un resumen ni a eliminar excepciones.
- Respetar una estructura solicitada; si no la hay, preferir pocos apartados que sigan el razonamiento. No añadir instrucciones dirigidas a agentes dentro de los apuntes del estudiante.
- Mantener el mismo término y símbolo para un concepto. Diferenciar correlación y causa, hipótesis y evidencia, modelo y realidad.
- No añadir prompts, casillas de entrega, soluciones de evaluación o metadiscusión sobre el material fuente salvo petición expresa.
- Si el encargo requiere una demostración o un ejemplo resuelto de aprendizaje, puede incluirse cuando no revele una evaluación reservada y forme parte del alcance.

Para un apoyo visual complementario, consultar [infografías didácticas](../infografias-didacticas-creacion/SKILL.md), sin sustituir por una imagen el documento solicitado.

## Sugerir el siguiente paso

Aplicar el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md):
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Ofrecer una actividad, un banco o diapositivas visuales individuales apoyados en los apuntes, comprobando si ya existen resultados relacionados antes de proponer crearlos.
