# Actualizar un curso a 0.8.0

La actualización conserva `proyecto-docente.json` con versión 1 y estructura
`curso-v1`, los mapas existentes, el formato del registro de fuentes y la entrada
de exámenes con un único GIFT. No modifica las copias instaladas del plugin.

1. Comprueba qué versión está disponible en GitHub e instálala desde tu
   marketplace. Un paquete preparado localmente todavía no es una publicación.
2. Abre el curso y pide «Actualiza la organización de mi proyecto a 0.8,
   conservando mis instrucciones». El agente puede previsualizar la actualización.
3. Se añade `docente/resultados/entregas/` si falta. No se mueven entregas antiguas:
   se acuerdan sus destinos por actividad y convocatoria antes de reorganizarlas.
4. Se propone actualizar `AGENTS.md` y `LEEME.md` para ofrecer orientación y
   recomendar el mapa. El ayudante conserva los archivos existentes y devuelve
   una propuesta; el agente integra solo lo autorizado y consulta conflictos.
5. Pide «¿Qué puedo hacer ahora?». La nueva skill `orientar-docente` se añade
   a las doce existentes, sin cambiar sus nombres.

## Bancos anteriores

Un GIFT con sus metadatos anteriores sigue funcionando con `build-exams BANCO`.
Para combinarlo por procedencia y dificultad, completar los datos que falten y
registrarlo en el [catálogo](BANCOS.md). No inventar procedencia a partir del título.
Las rutas enlazan los originales: no copiar materiales junto a cada banco.

La composición con catálogo utiliza `--catalog`, `--selection` y, si hace falta,
`--project`. Conserva bancos congelados, procedencia y un informe de cobertura.
Los manifiestos anteriores siguen siendo válidos para feedback; su versión 1
admite los campos nuevos sin exigir que existan en exámenes antiguos.

## Actividades y resultados

Las actividades nuevas asocian enunciado, plantillas, rúbrica y versión mediante
[actividad.json](ACTIVIDADES.md). En actividades anteriores, localizar los
documentos vigentes antes de corregir; no reemplazar criterios retroactivamente.

La [exportación de calificaciones](CALIFICACIONES.md) necesita una evaluación
estructurada y un perfil explícito de columnas. El profesor elige hoja de tarea
o libro de calificaciones. La rúbrica local no activa ni sustituye una rúbrica
nativa de Moodle. La importación sigue siendo manual.

El feedback de exámenes prioriza hasta tres dificultades. Sin detalle por
pregunta no se deducen conceptos fallados. La nota original se conserva, tanto
en la salida habitual como al cruzar con un libro de calificaciones separado.
Revisar las [precauciones de importación en Moodle](MOODLE.md) antes de importar.
