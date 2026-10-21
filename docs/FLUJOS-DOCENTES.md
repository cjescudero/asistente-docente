# Continuidad entre tareas docentes

El profesor puede conversar sin conocer los nombres de las skills. El agente
utiliza por defecto español claro en las respuestas y los documentos, salvo que
se haya indicado otro idioma o estilo. Conserva rigor, términos, citas y
restricciones; esta preferencia no autoriza a traducir textos literales.

## Recorridos

```text
Iniciar el curso → Crear el mapa → Consultar o visualizar → Elegir un recorrido

Actividad → Evaluar entregas → Revisar notas y comentarios para Moodle
Banco de preguntas → Modelos impresos y GIFT → Feedback de la evaluación

Apuntes y diapositivas visuales individuales: opciones complementarias
```

Las flechas expresan opciones de continuidad. No autorizan a ejecutar tareas
que el profesor no haya pedido. Un encargo que ya incluye varios pasos permite
completarlos sin preguntar de nuevo; comunicar después los siguientes pasos
pendientes, sin repetir sugerencias durante cada suboperación interna. La
visualización que forma parte de crear el mapa sigue siendo parte de ese encargo.

Un mapa es recomendable para recuperar conocimiento, pero no es requisito para
una tarea con adjuntos suficientes. Respetar la decisión de trabajar sin fuentes
o sin mapa; no insistir en una opción que el profesor ya haya descartado.

## Qué comprobar antes de recomendar

Consultar la conversación, la configuración y únicamente los índices o registros
pertinentes. Una carpeta existente, su nombre, una fecha o la palabra «final» no
acreditan un resultado completo. No leer recursivamente el curso ni abrir
entregas personales solo para orientar.

| Resultado posible | Evidencia mínima útil para la recomendación |
| --- | --- |
| Curso preparado | Configuración legible, estructura declarada e instrucciones presentes; distinguir fuentes pendientes. |
| Mapa existente | Índice registrado y accesible; consultar incidencias y registro para saber si necesita actualización. |
| Actividad preparada | Registro de actividad con versión y archivos asociados existentes; estado común coherente con el alcance. |
| Banco utilizable | Entrada del catálogo, GIFT y metadatos localizados; validación y revisión suficientes para lo que se propone. |
| Modelos preparados | Manifiesto del cuestionario, modelos y snapshots correspondientes; un HTML no acredita PDF disponible. |
| Lote recibido | Lote e identificación explícitos; no darlo por corregido porque exista `correccion/`. |
| Corrección o feedback generado | Informe de ejecución e incidencias, archivos resultantes y correspondencia con actividad, convocatoria o manifiesto. Un CSV no prueba importación en Moodle. |

El estado común no demuestra por sí solo calidad didáctica, vigencia ni identidad
entre versiones. Si solo hay un indicio, comprobar el registro o archivo mínimo
que resuelva la duda; si no se puede comprobar, presentar la opción como
condicional. No afirmar ausencia simplemente porque no se haya consultado algo.

## Cierre de cada encargo

Después de entregar el resultado, proponer de uno a tres pasos pertinentes. Cada
propuesta debe relacionarse con lo que se acaba de hacer e incluir, si falta, la
entrada necesaria y una petición breve que el profesor pueda usar. Mantener las
sugerencias fuera de los documentos que se van a entregar al alumnado. En una
corrección breve, basta una frase final; no añadir un menú completo.

- **Tras iniciar:** si faltan fuentes, completar su selección. Con fuentes,
  recomendar crear el mapa. Con mapa válido, ofrecer consultarlo o visualizarlo.
- **Tras crear, consultar o visualizar el mapa:** ofrecer la actividad o el banco
  pertinente; apuntes y diapositivas visuales individuales son otras opciones.
- **Tras una actividad:** «Cuando tengas las entregas, evalúalas con esta versión
  del enunciado y la rúbrica». Si ya hay un lote identificado, ofrecer corregirlo.
  Para notas importables se necesitan también la hoja Moodle y sus columnas.
- **Tras un banco:** ofrecer modelos impresos, indicando los datos que falten:
  título, cobertura, número de preguntas y modelos, tipos y dificultad.
- **Tras los modelos:** ofrecer revisar la impresión y configuración Moodle.
  Después de la evaluación, proponer feedback a partir del detalle por pregunta,
  el manifiesto y la hoja de calificaciones. Una nota global no basta.
- **Tras corregir o generar feedback:** priorizar incidencias y revisión del CSV
  para importación manual. Si ayuda, ofrecer materiales o actividades de refuerzo
  a partir de dificultades agregadas, sin trasladar datos personales a la wiki.
- **Tras apuntes o imágenes:** proponer una actividad, un banco o el complemento
  pertinente. Si solo se produjo un prompt, indicar antes la imagen pendiente.

Cuando exista una salida válida para el mismo objetivo y versión, ofrecer usarla,
revisarla o actualizarla en lugar de sugerir crear otra. La existencia de un banco
sobre otro tema o de modelos de otra convocatoria no completa el flujo actual.
Evitar proponer de nuevo pasos que ya estén incluidos en el encargo en curso.

Las diapositivas de este plugin son imágenes visuales individuales producidas
por `infografias-didacticas-creacion`. No prometer una presentación editable. Apuntes,
PDF e imágenes dependen de las capacidades disponibles y deben comunicarse según
lo realmente generado y revisado.

## Casos de revisión del comportamiento

Estos casos sirven para revisar las instrucciones; no son pruebas reales de un
anfitrión ni garantizan por sí solos el comportamiento de un modelo.

| Situación | Cierre esperado |
| --- | --- |
| Curso nuevo, fuentes elegidas, mapa vacío | Recomendar crear el mapa; no afirmar que ya existe ni ejecutarlo automáticamente. |
| Mapa registrado y actividad completa, sin entregas | Ofrecer consultar el mapa o preparar la evaluación cuando haya entregas; explicar las entradas pendientes. |
| `correccion/` existe pero está vacía | No dar por corregido el lote; verificar el informe mínimo o decir que la corrección no está comprobada. |
| Banco válido y modelos de la misma versión presentes | Ofrecer revisar esos modelos; con resultados detallados, manifiesto y hoja, ofrecer feedback. |
| Solo una nota global y un PDF antiguo | Explicar que faltan detalle y correspondencia con manifiesto antes del feedback conceptual. |
| Profesor pide una actividad y después su banco | Completar ambos pasos autorizados; sugerir modelos al final sin pedir repetir el encargo. |
| Profesor pide gallego y ya hay apuntes | Respetar idioma y ofrecer revisar los apuntes pertinentes; no traducirlos automáticamente a español. |
