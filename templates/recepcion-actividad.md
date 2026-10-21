# Entregas y corrección: {{titulo_actividad}}

Actividad: `{{id_actividad}}` · Convocatoria: `{{convocatoria}}`.
Estado: **pendiente de entregas**. Actualizar según archivos comprobados.

<!-- El agente adapta esta plantilla al LEEME del lote. Sustituir marcadores,
verificar los enlaces relativos desde el lote y retirar esta nota. Conservar
los nombres originales de las descargas. No crear CSV ni entregas de ejemplo
en un curso real. Si el lote ya contiene archivos, indicar su estado real. -->

## Criterios de esta actividad

- [Enunciado]({{ruta_relativa_enunciado}}).
- [Rúbrica docente]({{ruta_relativa_rubrica}}).
- [Guía de corrección]({{ruta_relativa_guia}}). Omitir si no existe.

Los criterios permanecen en la carpeta de la actividad. Esta guía y los
resultados son para el profesor; no se incorporan al mapa ni a las entregas
destinadas al alumnado.

## Qué colocar aquí

1. Descarga de Moodle los trabajos de esta actividad y convocatoria y guárdalos
   en `recibidos/entregas/`, conservando la estructura e identificadores de la
   descarga. Si llegan en ZIP, conserva el archivo original; el agente podrá
   preparar una extracción de trabajo para revisarlos.
2. Descarga el CSV de calificaciones correspondiente a la vía elegida —hoja
   sin conexión de la tarea o libro de calificaciones— y guárdalo en `recibidos/`.
   No cambies identificadores, nombres de columnas ni notas anteriores.
3. Si hace falta identificar equipos o asociar trabajos a participantes, aporta
   una correspondencia explícita en `recibidos/identificacion/`. El agente
   indicará qué información falta; no basta el parecido de los nombres.

La utilidad admite CSV. Si solo tienes un `.xlsx`, indícalo: habrá que obtener
el CSV de Moodle o convertir una copia verificando sus identificadores y datos.

## Cómo pedir la corrección

«Evalúa las entregas de {{titulo_actividad}}, convocatoria {{convocatoria}},
con su enunciado y rúbrica. Prepara la hoja de Moodle con calificaciones y
feedback, e indica las incidencias». No necesitas preparar archivos JSON.

## Qué recibirás

En `correccion/`: evaluación con evidencias y puntuaciones por criterio, una
copia del CSV con notas y comentarios, y las incidencias y cambios registrados.
Los archivos originales de `recibidos/` se conservan. Los casos ausentes,
ilegibles o pendientes no reciben un cero automático; las correspondencias
ambiguas deben resolverse antes de exportar.

Revisa los resultados y después importa manualmente el CSV por la vía Moodle
elegida, comprobando la vista previa. La existencia de esta carpeta no significa
que los trabajos estén corregidos ni que se hayan importado calificaciones.
