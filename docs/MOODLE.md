# Actividades, cuestionarios y feedback en Moodle

El plugin prepara archivos para dos recorridos docentes:

- **Actividades:** enunciado y criterios → entregas descargadas → corrección con
  evidencias → copia de la hoja de calificaciones con nota y feedback.
- **Cuestionarios:** bancos GIFT → modelos impresos y manifiesto → cuestionarios
  ofuscados → puntuación de Moodle → comentarios de mejora.

La importación y su comprobación son manuales. El plugin no conecta con Moodle
ni cambia la configuración del curso. Los ejemplos sintéticos y las validaciones
locales no equivalen a una importación real.

## Entregas de actividades

Descargar las entregas y la hoja de calificaciones correspondientes a la actividad
y convocatoria. Guardar los originales en
`resultados/<actividad>/<convocatoria>/recibidos/`, con la identificación
explícita correspondiente. Guardar notas y feedback nuevos en `correccion/`. El lote queda fuera
de la wiki.

La corrección usa el enunciado aplicado, la rúbrica y la guía o resolución
disponibles. El registro `actividad.json` permite comprobar su versión. Cada
puntuación se sustenta en evidencias de la entrega; una solución orientativa no
excluye respuestas alternativas válidas. Si faltan criterios suficientes,
proponerlos al profesor antes de asignar notas definitivas.

Elegir explícitamente una de estas vías según la tarea y el método configurados:

| Vía | Identificación y revisión |
| --- | --- |
| Hoja de calificación sin conexión de una tarea | Conservar su identificador de participante, que no es el ID de usuario. Comprobar que la tarea admite esta vía. |
| CSV del libro de calificaciones | Seleccionar el identificador y el elemento de calificación correctos; revisar las consecuencias de importar notas y comentarios. |

La [documentación de tareas de Moodle](https://docs.moodle.org/en/Using_Assignment)
indica que la carga de una hoja de calificación sin conexión no se admite con
rúbricas o guías de evaluación nativas. Una rúbrica local usada para revisar
entregas es un documento de criterios; no activa por sí sola ese método de
calificación avanzada en Moodle. Si la tarea lo tiene activado, comprobar un
procedimiento compatible con el profesor. No cambiar el método ni pasar al libro
de calificaciones automáticamente.

La utilidad `export-grades` recibe la evaluación estructurada, el archivo Moodle
y un perfil de columnas. Conserva filas, identificadores y columnas ajenas;
actualiza la nota y el comentario de los casos evaluados, y registra los valores
anteriores, los nuevos y su justificación. El
[contrato de calificaciones](CALIFICACIONES.md) detalla las entradas y salidas.

Duplicados, correspondencias ambiguas o datos obligatorios inconsistentes
bloquean la exportación. Un trabajo ausente, ilegible o pendiente no se convierte
automáticamente en cero. Para grupos, aportar la relación explícita de miembros
y la regla de nota común o individual. No emparejar por semejanza de nombres.
Antes de importar, revisar los cambios y los casos pendientes en una muestra.

## Cuestionarios en papel y cuestionarios ofuscados

GIFT es un formato de texto para preguntas de Moodle; no es el formato de imagen GIF. Un GIFT ofuscado reduce el contenido visible a números de pregunta y etiquetas de respuesta. El archivo contiene claves y pesos necesarios para corregir: conservarlo como material docente.

## Preparar y comprobar los modelos

Generar papel, solucionario y GIFT desde la misma selección ordenada mediante
`build-cuestionarios --layout curso-v3` en cursos nuevos. Se puede combinar el [catálogo de bancos](BANCOS.md) por materiales,
actividades y dificultad tras acordar el reparto. Conservar `manifest.json`,
los bancos utilizados congelados y sus metadatos en la subcarpeta `_datos_internos/`.
Los documentos imprimibles están en `alumnado/`; no mover sus archivos a mano.
Si después se corrige un banco
de trabajo, no sustituir el snapshot del cuestionario aplicado.

Revisar todos los modelos antes de imprimir. La pregunta 1 y la opción A del papel deben corresponder a la pregunta 1 y opción A de Moodle, aunque la correcta sea C. Verdadero/falso se representa como dos opciones de selección única, respetando su posición. Las numéricas conservan campo numérico y tolerancia. Emparejamiento no se usa en el flujo ofuscado de esta versión.

## Importación y configuración manual

1. Importar el GIFT de cada modelo en la categoría correspondiente. Revisar nombres, cantidad, tipo y pesos con el manifiesto. No importar el banco con enunciados completos en el cuestionario destinado a recoger respuestas del papel.
2. Crear el cuestionario y añadir las preguntas concretas en el orden del manifiesto. No usar selección aleatoria de categorías ni confiar en que el orden del archivo importado determine el del cuestionario.
3. Desactivar la mezcla de preguntas y la mezcla de respuestas, tanto en el cuestionario como donde corresponda a las preguntas. Comprobar el comportamiento efectivo; un nombre numerado no impide que Moodle baraje opciones.
4. Configurar la disponibilidad y los intentos según la decisión del profesor. Durante la evaluación y el periodo en que deba mantenerse reservada, desactivar las opciones de revisión que revelen respuestas, corrección, solución, feedback específico, general o global. No habilitar vistas previas de soluciones para estudiantes.
5. Probar con vista o cuenta de estudiante cada modelo: numeración, etiquetas, orden, selección única o múltiple, entrada numérica y comportamiento al enviar. La vista docente puede mostrar información que el alumnado no ve.
6. Entregar el PDF de estudiante de su modelo y utilizar Moodle para que registre las respuestas según el procedimiento del curso. No entregar el solucionario, el manifiesto ni el GIFT como material de cuestionario al alumnado.

La ofuscación no garantiza por sí sola ausencia de consultas externas. Su función aquí es mantener la correspondencia papel–respuesta y limitar el contenido mostrado en la pantalla.

## Exportar los resultados

Obtener un CSV que permita identificar de forma inequívoca a cada estudiante, el modelo aplicado, el estado del intento y las puntuaciones por pregunta. Conservar también las respuestas elegidas si se solicita feedback detallado. El CSV del libro de calificaciones puede no contener el detalle por pregunta necesario: comprobarlo antes de procesar.

Una nota global no permite determinar qué conceptos necesita repasar el estudiante.
Si el destino del feedback es el libro de calificaciones, exportarlo además y
cruzarlo explícitamente con el detalle del cuestionario. Aportarlo mediante
`--gradebook` no sustituye los resultados detallados de `--input`.

Si el CSV de un cuestionario no incluye modelo, añadirlo explícitamente en una copia de trabajo a partir del cuestionario cuya correspondencia con el manifiesto se haya comprobado. No inferirlo por parecido del nombre ni mezclar modelos antes de resolver esa correspondencia.

Usar identificadores institucionales estables como texto y preservar ceros iniciales. No usar nombres como clave si existe un identificador fiable. Conservar el archivo original y documentar separador, codificación y escala de cada columna. La herramienta admite coma, punto y coma y tabulador; un decimal no debe confundirse con el separador CSV.

## Configurar el procesamiento

El JSON de configuración describe los encabezados reales. Este ejemplo sintético corresponde a un cuestionario de dos preguntas con un punto máximo por pregunta:

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
  "feedback_priority": {
    "max_concepts": 3,
    "marked_threshold": 0.5,
    "min_evidence": 2
  },
  "delimiter": ";"
}
```

Adaptar encabezados y máximos a la exportación real. `blank_values` contiene tokens que el profesor declara como respuesta en blanco; no incluir una celda vacía sin haber comprobado su significado. `absent_values` se aplica al estado del intento. Una columna ausente es un error de datos, no una respuesta fallada.

Los mapas `question_columns`, `max_scores` y `answer_columns` pueden configurarse por modelo dentro de `models`; los mapas de un modelo sustituyen a los generales. Los identificadores de modelo deben ser exactamente los del manifiesto. Véase [CONTRATOS](CONTRATOS.md) para el formato vigente.

## Generar y revisar el feedback

Ejecutar `build-feedback` con el manifiesto oficial, los CSV y la configuración. Leer primero el informe: identificadores ausentes, duplicados, modelos desconocidos, columnas faltantes o notas incompatibles bloquean la exportación. Resolverlos en la fuente o en la configuración y repetir. No escoger una entrega duplicada ni convertir un dato faltante en cero automáticamente.

El modo normal prioriza hasta tres conceptos según la proporción de puntos
perdidos y la cantidad de evidencias. Con los valores predeterminados, menos del
50 % en un concepto con al menos dos preguntas indica una dificultad acusada;
un fallo aislado se presenta como aspecto a revisar. Se puede ajustar el objeto
`feedback_priority` del perfil. No atribuir una causa específica al error sin
evidencia.

Las orientaciones proceden de los metadatos y solo recomiendan materiales
accesibles al estudiante. No reproducen preguntas reservadas, letras correctas
ni enlaces a soluciones o rúbricas docentes. Si faltan conceptos u orientaciones,
declarar la limitación en lugar de inventarlos.

Los no presentados mantienen feedback vacío. Las notas originales no cambian. Se generan CSV por modelo y un informe; el consolidado es opcional. Antes de importar, comprobar identificadores, conteo, acentos, columnas y casos representativos de cada estado. El modo detallado solo se usa si el profesor lo pide y la política de publicación de la evaluación lo permite.

## Reimportar comentarios

Antes de importar, conservar una exportación reciente del libro de calificaciones y contrastar que las notas del CSV siguen vigentes. La documentación oficial advierte que importar feedback puede sobreescribir las notas vinculadas y recomienda incluir y mapear también la nota de la actividad. Por tanto, no asumir que mapear solo comentarios es inocuo: mantener la nota original sin recalcularla y comprobar el comportamiento de la instancia. Véase [importación de calificaciones](https://docs.moodle.org/en/Grade_import).

La importación al libro equivale a una edición manual de la calificación
(*override*): la documentación indica que una nota importada de una actividad
deja de poder editarse desde la página de entregas. Revisar esta consecuencia
antes de elegir la vía; no presentarla como equivalente a cargar la hoja de una
tarea.

Elegir el identificador estable y el elemento de calificación correcto. Mapear el comentario y, cuando lo requiera el importador, la nota original conservada de ese mismo elemento. No mapear columnas ajenas ni crear elementos nuevos por defecto. Si las notas han cambiado desde la exportación, obtener datos vigentes y recomponer la salida; no forzar una importación antigua. Revisar la vista previa y comprobar después tanto comentarios como notas de una muestra.

Si la configuración del Moodle concreto no admite ese destino de feedback o exige otra exportación, detener esa parte y registrar la limitación. No asegurar compatibilidad solo porque el CSV sea válido. El plugin prepara los archivos; la importación real y su comprobación son manuales.

Referencias oficiales: [uso de tareas](https://docs.moodle.org/en/Using_Assignment),
[formato GIFT](https://docs.moodle.org/en/GIFT_format),
[ajustes del cuestionario](https://docs.moodle.org/en/Quiz_settings) e
[importación de calificaciones](https://docs.moodle.org/en/Grade_import).

## Categorías de los modelos

Cada GIFT incluye, por ejemplo:

```gift
$CATEGORY: $course$/top/RespuestasCuestionariosOffline/Talleres 5-8/Modelo 01
```

El título identifica el cuestionario y `Modelo 01`, `Modelo 02`… sus modelos.
El manifiesto guarda `name` y `moodle_category` en cada modelo, junto a su ID,
archivos, preguntas originales, opciones, pesos y tolerancias. Los IDs técnicos
A, B… siguen identificando archivos y cruces de resultados; el nombre visible
se muestra en el PDF y en la categoría. El LEEME explica ambas correspondencias.

Importar cada GIFT en el banco de preguntas del curso, activando el uso de las
categorías del archivo cuando Moodle ofrezca esa opción. Comprobar el árbol
`RespuestasCuestionariosOffline → título → Modelo 01` y el recuento; crear después
el cuestionario con las preguntas de ese modelo en su orden, sin barajar opciones.
Importar preguntas no crea ni configura la actividad cuestionario.
Los títulos GIFT internos conservan el ID de modelo para evitar colisiones; el
texto visible continúa siendo «Pregunta 01», «Respuesta A», etc.
