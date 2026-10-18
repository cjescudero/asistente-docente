# Examen en papel y devolución de feedback en Moodle

El recorrido es: banco GIFT docente → modelos impresos y manifiesto → GIFT ofuscado para recoger respuestas → exportación de resultados → comentarios individuales → importación manual del feedback. El mismo manifiesto conserva la correspondencia durante todo el recorrido.

GIFT es un formato de texto para preguntas de Moodle; no es el formato de imagen GIF. Un GIFT ofuscado reduce el contenido visible a números de pregunta y etiquetas de respuesta. El archivo contiene claves y pesos necesarios para corregir: conservarlo como material docente.

## Preparar y comprobar los modelos

Generar papel, solucionario y GIFT desde la misma selección ordenada mediante `build-exams`. Conservar `manifest.json` y su snapshot del banco. Si después se corrige el banco de trabajo, no sustituir el snapshot del examen aplicado.

Revisar todos los modelos antes de imprimir. La pregunta 1 y la opción A del papel deben corresponder a la pregunta 1 y opción A de Moodle, aunque la correcta sea C. Verdadero/falso se representa como dos opciones de selección única, respetando su posición. Las numéricas conservan campo numérico y tolerancia. Emparejamiento no se usa en el flujo ofuscado de esta versión.

## Importación y configuración manual

1. Importar el GIFT de cada modelo en la categoría correspondiente. Revisar nombres, cantidad, tipo y pesos con el manifiesto. No importar el banco con enunciados completos en el cuestionario destinado a recoger respuestas del papel.
2. Crear el cuestionario y añadir las preguntas concretas en el orden del manifiesto. No usar selección aleatoria de categorías ni confiar en que el orden del archivo importado determine el del cuestionario.
3. Desactivar la mezcla de preguntas y la mezcla de respuestas, tanto en el cuestionario como donde corresponda a las preguntas. Comprobar el comportamiento efectivo; un nombre numerado no impide que Moodle baraje opciones.
4. Configurar la disponibilidad y los intentos según la decisión del profesor. Durante la evaluación y el periodo en que deba mantenerse reservada, desactivar las opciones de revisión que revelen respuestas, corrección, solución, feedback específico, general o global. No habilitar vistas previas de soluciones para estudiantes.
5. Probar con vista o cuenta de estudiante cada modelo: numeración, etiquetas, orden, selección única o múltiple, entrada numérica y comportamiento al enviar. La vista docente puede mostrar información que el alumnado no ve.
6. Entregar el PDF de estudiante de su modelo y utilizar Moodle para que registre las respuestas según el procedimiento del curso. No entregar el solucionario, el manifiesto ni el GIFT como material de examen al alumnado.

La ofuscación no garantiza por sí sola ausencia de consultas externas. Su función aquí es mantener la correspondencia papel–respuesta y limitar el contenido mostrado en la pantalla.

## Exportar los resultados

Obtener un CSV que permita identificar de forma inequívoca a cada estudiante, el modelo aplicado, el estado del intento y las puntuaciones por pregunta. Conservar también las respuestas elegidas si se solicita feedback detallado. El CSV del libro de calificaciones puede no contener el detalle por pregunta necesario: comprobarlo antes de procesar.

Si el CSV de un cuestionario no incluye modelo, añadirlo explícitamente en una copia de trabajo a partir del cuestionario cuya correspondencia con el manifiesto se haya comprobado. No inferirlo por parecido del nombre ni mezclar modelos antes de resolver esa correspondencia.

Usar identificadores institucionales estables como texto y preservar ceros iniciales. No usar nombres como clave si existe un identificador fiable. Conservar el archivo original y documentar separador, codificación y escala de cada columna. La herramienta admite coma, punto y coma y tabulador; un decimal no debe confundirse con el separador CSV.

## Configurar el procesamiento

El JSON de configuración describe los encabezados reales. Este ejemplo sintético corresponde a un examen de dos preguntas con un punto máximo por pregunta:

```json
{
  "schema_version": 1,
  "identifier_column": "id_estudiante",
  "model_column": "modelo",
  "status_column": "estado",
  "feedback_column": "comentarios",
  "absent_values": ["No presentado"],
  "blank_values": ["Sin respuesta"],
  "question_columns": {"1": "P1", "2": "P2"},
  "max_scores": {"1": 1, "2": 1},
  "delimiter": ";"
}
```

Adaptar encabezados y máximos a la exportación real. `blank_values` contiene tokens que el profesor declara como respuesta en blanco; no incluir una celda vacía sin haber comprobado su significado. `absent_values` se aplica al estado del intento. Una columna ausente es un error de datos, no una respuesta fallada.

Los mapas `question_columns`, `max_scores` y `answer_columns` pueden configurarse por modelo dentro de `models`; los mapas de un modelo sustituyen a los generales. Los identificadores de modelo deben ser exactamente los del manifiesto. Véase [CONTRATOS](CONTRATOS.md) para el formato vigente.

## Generar y revisar el feedback

Ejecutar `build-feedback` con el manifiesto oficial, los CSV y la configuración. Leer primero el informe: identificadores ausentes, duplicados, modelos desconocidos, columnas faltantes o notas incompatibles bloquean la exportación. Resolverlos en la fuente o en la configuración y repetir. No escoger una entrega duplicada ni convertir un dato faltante en cero automáticamente.

El modo normal agrupa dificultades por conceptos y ofrece orientaciones de repaso procedentes de los metadatos. No enumera letras correctas ni reproduce preguntas reservadas. Si faltan metadatos, declarar la limitación en lugar de inventar una explicación. No concluir que un estudiante «no comprende» un tema únicamente por una respuesta: describir qué conviene revisar según la evidencia disponible.

Los no presentados mantienen feedback vacío. Las notas originales no cambian. Se generan CSV por modelo y un informe; el consolidado es opcional. Antes de importar, comprobar identificadores, conteo, acentos, columnas y casos representativos de cada estado. El modo detallado solo se usa si el profesor lo pide y la política de publicación de la evaluación lo permite.

## Reimportar comentarios

Antes de importar, conservar una exportación reciente del libro de calificaciones y contrastar que las notas del CSV siguen vigentes. La documentación oficial advierte que importar feedback puede sobreescribir las notas vinculadas y recomienda incluir y mapear también la nota de la actividad. Por tanto, no asumir que mapear solo comentarios es inocuo: mantener la nota original sin recalcularla y comprobar el comportamiento de la instancia. Véase [importación de calificaciones](https://docs.moodle.org/en/Grade_import).

Elegir el identificador estable y el elemento de calificación correcto. Mapear el comentario y, cuando lo requiera el importador, la nota original conservada de ese mismo elemento. No mapear columnas ajenas ni crear elementos nuevos por defecto. Si las notas han cambiado desde la exportación, obtener datos vigentes y recomponer la salida; no forzar una importación antigua. Revisar la vista previa y comprobar después tanto comentarios como notas de una muestra.

Si la configuración del Moodle concreto no admite ese destino de feedback o exige otra exportación, detener esa parte y registrar la limitación. No asegurar compatibilidad solo porque el CSV sea válido. El plugin prepara los archivos; la importación real y su comprobación son manuales.

Referencias oficiales: [formato GIFT](https://docs.moodle.org/en/GIFT_format), [ajustes del cuestionario](https://docs.moodle.org/en/Quiz_settings) e [importación de calificaciones](https://docs.moodle.org/en/Grade_import).
