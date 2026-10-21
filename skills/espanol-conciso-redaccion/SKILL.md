---
name: espanol-conciso-redaccion
description: Redactar, explicar o reescribir materiales docentes en español claro sin perder precisión, y elegir texto o recursos visuales según la dificultad del lector. Usar por defecto en los flujos de Asistente docente salvo que el profesor indique otro idioma o estilo, y al pedir español técnico simplificado o reducción de ambigüedad. No usar para desarrollo web sin finalidad explicativa.
---

# Español conciso: redacción

Redactar por defecto en español claro en los flujos de este plugin; respetar un idioma o estilo distinto pedido por el profesor. No traducir citas literales ni identificadores por esta preferencia. Aplicar principios de claridad inspirados en ASD-STE100 con criterios propios adecuados al español y a cualquier disciplina. Priorizar exactitud del significado, comprensión del lector y concisión, en ese orden. Simplificar la expresión sin rebajar el rigor ni infantilizar el contenido.

Si hace falta identificar el enfoque, describirlo como «español técnico simplificado basado en ASD-STE100». Es una adaptación editorial propia: no es certificación, traducción oficial ni equivalencia normativa. Las pautas de longitud no proceden de un diccionario español aprobado.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

Al revisar un documento existente, conservar su ubicación y alcance. Para un
material nuevo en `curso-v2`, usar el destino de su tipo según el contrato común;
una redacción autónoma va en `creados/materiales/<id>/`. Crear o actualizar el
registro de material y su estado cuando se entrega un conjunto de archivos,
sin exigir carpetas ni registros para una corrección breve en la conversación.

## Alcance e intensidad

- Respetar propósito, audiencia, extensión y formato. Explicar, resumir y reescribir son tareas diferentes; simplificar no autoriza a omitir información.
- Inferir el nivel del lector con el contexto disponible. Usar por defecto un registro adulto y claro; preguntar solo si el nivel cambia sustancialmente la explicación.
- Conservar términos y notación precisos que conozca la audiencia. Explicar un tecnicismo cuando resulte necesario para comprenderlo.
- Usar por defecto un modo natural, con conectores y variación sintáctica normales. En modo estricto, reducir incisos y separar más los pasos, manteniendo condiciones y matices.
- Interpretar «80 % de ASD-STE100» como claridad con flexibilidad, sin calcular porcentajes ni afirmar cumplimiento normativo.

## Elegir el formato

Respetar el formato pedido. Si no se ha indicado, elegir el más sencillo que resuelva la dificultad, sin generar todas las modalidades. Aplicar estas reglas también a títulos, etiquetas, narración y subtítulos.

| Dificultad del lector | Formato inicial |
| --- | --- |
| Comprender una definición breve | Texto claro |
| Comparar valores o criterios exactos | Tabla o gráfico |
| Relacionar componentes, causas o decisiones | Diagrama |
| Explorar qué cambia con una variable | HTML interactivo |
| Observar una transformación temporal | Animación controlable |
| Seguir una explicación guiada y compartible | Vídeo con narración y subtítulos |

Para cualquier recurso visual, interactivo o audiovisual, leer [formatos y comprobaciones](references/formatos.md). Descubrir las herramientas disponibles en el anfitrión; esta skill determina la explicación, no garantiza herramientas de producción. No cambiar silenciosamente el formato si falta una capacidad.

## Flujo

1. Identificar tarea y lector. Leer la fuente completa necesaria. En una reescritura, respetar su alcance; en una explicación, añadir solo contexto pertinente y comprobado.
2. Identificar lo que debe conservarse: sujetos, acciones, relaciones, condiciones, excepciones, cifras y certeza. Marcar ambigüedades sin resolverlas mediante supuestos. Mantener una terminología local estable.
3. Determinar qué debe comprender, predecir o comprobar el lector y elegir formato e intensidad. En peticiones sencillas, resolver sin mostrar un plan innecesario.
4. Ordenar desde la respuesta o relación principal hacia mecanismo, condiciones y ejemplo. En una secuencia audiovisual, preparar escenas antes de producirlas.
5. Redactar aplicando las reglas siguientes. Consultar [ejemplos delicados](references/ejemplos.md) cuando haya ambigüedad, incertidumbre o riesgo de cambiar el significado.
6. Comparar resultado y fuente. Verificar exactitud, representación y funcionamiento real. Entregar el artefacto solicitado, no el análisis interno.

## Frases, párrafos y términos

- Expresar una idea principal por frase. Mantener juntas las partes de una condición cuando separarlas dificulte entenderla.
- Preferir frases de unas 12–20 palabras y revisar las que superen 25. Son criterios editoriales flexibles, no límites mecánicos.
- Usar orden natural, verbos directos y voz activa cuando el agente sea conocido. Admitir pasiva refleja e impersonal; no inventar sujetos para evitarlas.
- Formar párrafos conectados, normalmente de dos a cinco frases. No convertir cada frase en un párrafo ni una explicación completa en una lista.
- Usar conectores que reflejen la relación real. No convertir una sucesión temporal en una causa.
- Preferir palabras habituales con igual precisión: «usar» en lugar de «hacer uso de». Mantener sustantivos técnicos que designen conceptos propios.
- Usar un término por concepto dentro del texto. No alternar sinónimos técnicos por variedad ni fusionar conceptos diferentes.
- Repetir el nombre si el referente está confirmado y un pronombre genera dudas. Si hay varias interpretaciones razonables, señalar la ambigüedad; no elegir la más cercana por comodidad.
- Definir siglas si la audiencia puede desconocerlas. Conservar nombres oficiales, etiquetas, comandos, identificadores y citas literales.
- Evitar metáforas decorativas, dobles negaciones y adjetivos vagos. Mantener una negación si expresa una prohibición o condición esencial.

## Precisión conceptual

- Conservar cifras, signos, unidades, fórmulas, comparaciones y restricciones. Distinguir correlación y causa, condición necesaria y suficiente, porcentaje y puntos porcentuales.
- Mantener cuantificadores y certeza: «algunos», «todos», «solo», «al menos», «puede» o «suele». No convertir una posibilidad en un hecho ni una recomendación en obligación.
- Si importa distinguir posibilidad, capacidad y permiso en «puede», hacerlo cuando la fuente lo permita; en otro caso, conservar la incertidumbre.
- Mantener condiciones y excepciones junto a la afirmación que limitan, aunque alarguen el texto.
- Conservar citas literales. Si se reformulan, presentarlas como paráfrasis y mantener atribución.
- No añadir datos, causas, conclusiones o fuentes inexistentes. Verificar afirmaciones nuevas actuales o especializadas; no buscar fuentes nuevas para una mera edición con contenido suficiente.
- No reproducir un error verificable como hecho. Corregirlo y señalar brevemente el cambio; si no puede verificarse, marcar la duda sin cambiar silenciosamente la tesis.

## Adaptar al encargo

**Explicaciones y docencia.** Presentar primero la idea central; explicar después cómo o por qué. Separar descripción, causa y consecuencia. Introducir términos antes de usarlos. Añadir un ejemplo o analogía solo si reduce una dificultad concreta y señalar sus límites cuando puedan inducir errores. Explicar símbolos y condiciones de una fórmula sin desarrollar pasos no pedidos. Conservar la profundidad para lectores expertos.

**Procedimientos.** Usar pasos numerados cuando exista secuencia, una acción principal por paso e imperativos directos. Situar condiciones y advertencias necesarias antes de la acción. Indicar resultados esperados solo cuando se conozcan; no inventar mensajes de éxito de una interfaz.

**Reescrituras.** Mantener contenido, alcance y estructura exigida. Reordenar únicamente para mejorar la comprensión. Si una ambigüedad bloquea una parte, identificar qué falta y completar las partes independientes. Entregar por defecto la versión reescrita, con comentarios solo cuando se pidan o exista una corrección sustantiva.

## Comprobar y entregar

Revisar sujetos, condiciones, negaciones, cantidades, certeza y coherencia de términos. Comprobar que las frases se entienden a la primera y que la extensión responde al encargo. Para visuales, verificar escalas, flechas, unidades, colores, movimiento y controles; señalar esquemas no proporcionales y simplificaciones relevantes. Código generado no equivale a resultado renderizado y verificado.

Entregar en el formato solicitado, con la mínima explicación necesaria. Añadir alternativa textual accesible cuando corresponda. No publicar un recurso por haberlo creado ni llamar vídeo a un guion. Para documentos docentes sin formato indicado, usar Markdown y PDF cuando pueda producirse y revisarse; véase [uso](../../docs/USO.md).

La [FAQ del STEMG](https://asd-ste100.org/STE_faq.html) es la referencia sobre el estándar de inglés técnico. La skill original también tomó como inspiración el [post de Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479) aportado por el propietario: escritura simplificada y explicaciones mediante diagramas, HTML y vídeos personalizados. La tabla, modos y comprobaciones anteriores son criterios editoriales propios, no resultados experimentales atribuidos a Karpathy. Véase [procedencia](../../docs/PROCEDENCIA.md).

## Sugerir el siguiente paso

Aplicar el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md):
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Adaptar las sugerencias al documento revisado: continuar el flujo de su actividad, banco, cuestionario o material. En una corrección breve, mantener la sugerencia breve y fuera del texto que el profesor va a reutilizar.
