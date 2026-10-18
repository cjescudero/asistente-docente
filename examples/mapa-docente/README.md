# Ejemplo de Mapa docente

Todo el contenido es sintético. Abrir el [índice](mapa-docente/index.md) para
ver la separación entre materiales del estudiante y referencias reservadas.
Los originales del ejemplo son Markdown breves, no una prueba de extracción de
PowerPoint o PDF. No contienen datos de estudiantes reales.

Abrir el [lector de la wiki](mapa-docente/index.html), el [grafo docente](mapa-docente/grafo-docente.html) o la
[vista del estudiante](mapa-docente/grafo-estudiante.html) en el navegador.

Se usan dos carpetas elegidas para esta demostración: `materiales-docentes/` y
`archivo-evaluaciones/`. El mapa vive en `mapa-docente/` y enlaza mediante rutas
relativas. Los nombres no se imponen a los proyectos del profesor.

Las siete fuentes comprenden un programa, una presentación, apuntes, una
práctica, un taller, un examen histórico y una lista pendiente. Hay cinco
lecturas completas, una parcial y una pendiente. La consulta de ejemplo está
[documentada aquí](consulta-ejemplo.md).

## Reproducir en el espacio del curso

Copiar esta carpeta completa fuera del plugin para hacer pruebas. Configurar
`ASISTENTE_DOCENTE` con la raíz instalada del plugin y pasar rutas explícitas:

```sh
python "$ASISTENTE_DOCENTE/scripts/validate_library.py" /ruta/copia/mapa-docente
python "$ASISTENTE_DOCENTE/scripts/build_graph.py" /ruta/copia/mapa-docente --output /ruta/copia/mapa-docente/grafo-docente.html --wiki-output /ruta/copia/mapa-docente/index.html
python "$ASISTENTE_DOCENTE/scripts/build_graph.py" /ruta/copia/mapa-docente --output /ruta/copia/mapa-docente/grafo-estudiante.html --audience estudiante
```

El grafo docente tiene enlaces a las páginas y originales; evaluaciones aparece
como filtro desmarcado al abrirlo. El archivo completo es de uso interno.
El grafo del estudiante contiene solo datos compartibles y no enlaza a archivos.
No confundir estos filtros con permisos de acceso.

## Comprobar el comportamiento

- Arrastrar un nodo, desplazar el fondo, usar zoom, buscar «media» y filtrar talleres.
- Tras filtrar, pulsar «Reorganizar»: cambian las posiciones de los visibles,
  sin restablecer los filtros. «Ajustar» solo modifica el encuadre.
- Seleccionar un nodo y abrir sus documentos en el lector o en Markdown.
- En el lector, recorrer índice → concepto → ficha → volver con el navegador.
- Activar evaluaciones en la vista docente y abrir una ficha reservada.
- Comprobar que «Examen histórico y solución» no está en el HTML estudiantil,
  ni como título, ruta o nodo oculto. Tampoco aparece la síntesis que depende de él.
- Cambiar un original en una copia de prueba: debe detectarse su huella distinta.
- Preguntar por la rúbrica actual: no aplicar los pesos del examen antiguo.
- Preguntar por el apéndice: consultar su original antes de ampliar la respuesta,
  respetando que la lectura registrada del mapa es parcial.

Las instalaciones e invocaciones reales en cada anfitrión se verifican aparte.
