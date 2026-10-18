# Plantilla de mapa docente

Solicitar al profesor las carpetas de origen y la ubicación del mapa. Crear la
carpeta de documentación en su proyecto, fuera del plugin, sin mover originales.
Copiar `index.md`, `LEEME.md`, `fuentes.json`, `incidencias.md` y `log.md`.
Adaptar el contexto y rellenar `source_roots` con las rutas relativas elegidas:
la plantilla no presupone una carpeta de materiales.

Crear bajo `contenidos/` las secciones de conceptos, presentaciones, apuntes,
prácticas y talleres que hagan falta. Poner material docente, reservado o de
acceso desconocido en `reservado/`, separado por evaluaciones, soluciones u
otros tipos. Usar `ficha-fuente.md` y `ficha-tema.md` como modelos, no copiarlos
como páginas ya procesadas. Registrar cada página en `pages` con sus fuentes.

Usar enlaces Markdown normales. No hacen falta propiedades de Notion,
frontmatter ni enlaces de sintaxis propia de una aplicación wiki.
Al terminar, validar y generar `index.html` y `grafo-docente.html` con
`build_graph.py --wiki-output`; la salida para estudiantes
solo se añade cuando se pide y nunca contiene datos reservados.

El [contrato del mapa](../../docs/MAPA-DOCENTE.md) define el inventario y el flujo.
