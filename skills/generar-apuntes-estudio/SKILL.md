---
name: generar-apuntes-estudio
description: Crear o revisar apuntes teóricos, guías de estudio y síntesis conceptuales a partir de materiales de una asignatura de cualquier disciplina. No usar para resolver evaluaciones reservadas, redactar enunciados, corregir entregas ni generar bancos GIFT.
---

# Generar apuntes de estudio

Producir un documento autónomo que ayude a comprender y relacionar los conceptos del bloque pedido. El nivel y la profundidad proceden del curso y del encargo, no de una disciplina predeterminada.

Esta skill crea materiales de aprendizaje para el alumnado. Cuando exista un Mapa docente, usarlo para localizar las fuentes pertinentes y contrastar con ellas la explicación. No crear ni mantener aquí el inventario, la wiki o el grafo del curso; esas tareas corresponden a [crear el Mapa docente](../crear-mapa-docente/SKILL.md).

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

1. Delimitar tema, audiencia y fuentes. Leer los materiales necesarios completos y, si existen, apuntes de la misma serie para conservar notación y continuidad. Priorizar fuentes vigentes autorizadas frente a bancos o exámenes anteriores.
2. Extraer conceptos, definiciones, relaciones, supuestos, fórmulas y controversias pertinentes. Distinguir conocimientos de la materia, ejemplos y opiniones atribuidas.
3. Organizar la explicación desde una idea central: propósito del tema, desarrollo por conceptos y relaciones con conocimientos previos. Añadir un glosario solo si reduce una dificultad real.
4. Respetar el idioma del encargo o del curso. Para textos en español, aplicar [español claro](../redactar-espanol-claro/SKILL.md). Explicar nuevos símbolos y condiciones de validez; conservar el rigor adecuado al lector. Un apunte de filosofía puede necesitar argumentos y objeciones; uno de química, modelos, unidades y límites.
5. Incorporar ejemplos breves que resuelvan dificultades concretas. Si las fuentes son prácticas evaluadas, extraer la teoría sin copiar soluciones reservadas ni convertir el apunte en una secuencia para superar esa evaluación.
6. Revisar cobertura, atribuciones, consistencia de términos y exactitud contra las fuentes. Mantener referencias suficientes para comprobar afirmaciones especializadas o citas; no inventar bibliografía.
7. Entregar Markdown y PDF por defecto mediante `python "$ASISTENTE_DOCENTE/scripts/docencia.py" render-markdown apuntes.md --output salida`. Localizar la raíz instalada del plugin en `ASISTENTE_DOCENTE` y resolver entradas y salidas en el espacio del curso; consultar [uso](../../docs/USO.md). Identificar cualquier PDF pendiente de renderizar o revisar.

## Alcance y calidad

- Simplificar lenguaje no autoriza a convertir una reescritura completa en un resumen ni a eliminar excepciones.
- Respetar una estructura solicitada; si no la hay, preferir pocos apartados que sigan el razonamiento. No añadir instrucciones dirigidas a agentes dentro de los apuntes del estudiante.
- Mantener el mismo término y símbolo para un concepto. Diferenciar correlación y causa, hipótesis y evidencia, modelo y realidad.
- No añadir prompts, casillas de entrega, soluciones de evaluación o metadiscusión sobre el material fuente salvo petición expresa.
- Si el encargo requiere una demostración o un ejemplo resuelto de aprendizaje, puede incluirse cuando no revele una evaluación reservada y forme parte del alcance.

Para un apoyo visual complementario, consultar [infografías didácticas](../crear-infografias-didacticas/SKILL.md), sin sustituir por una imagen el documento solicitado.
