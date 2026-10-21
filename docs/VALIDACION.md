# Validación local de 0.11.0

Comprobada el 21 de octubre de 2026 en macOS con Python 3.12. Estas
comprobaciones no acreditan instalación en ChatGPT Work o Claude Cowork ni
importación real en Moodle.

- Suite automatizada: **387 pruebas correctas**, incluidas las 2 pruebas PDF
  opcionales con Chrome instalado localmente.
- Pruebas de navegador del grafo, su reorganización y el lector de la wiki:
  correctas en Chrome, con filtros, enlaces, navegación, vista móvil y 600 nodos.
- Proyecto: `curso-v3` es el único formato de curso admitido. Configuración e
  inventario se sitúan en `_datos_internos_proyecto/`; una configuración en la
  raíz o una estructura desconocida producen diagnóstico. La inicialización
  repetida conserva instrucciones y no crea el mapa automáticamente.
- Reorganización: la herramienta prepara propuestas y detecta colisiones y
  solapamientos sin mover archivos. Los cuestionarios utilizados se conservan
  como conjuntos con manifiesto y bancos congelados.
- Cuestionarios: la selección reside en su propia carpeta; modelos, GIFT,
  manifiesto y snapshots mantienen correspondencias. La salida de curso usa
  `--layout curso-v3`; también existe la salida `flat` para uso independiente.
- Recorrido sintético ejecutado fuera de la instalación: tres modelos de seis
  preguntas, calificaciones y feedback generados; originales intactos.
- Validador del plugin, manifiestos y catálogo, y validador del mapa de ejemplo:
  correctos. El validador del mapa no comprueba encabezados ni anclas Markdown.
- ZIP de OpenAI, Claude y fuente preparados desde la misma fuente y validados
  por su contenido funcional. Los hashes están en `release/SHA256SUMS`.
- `git diff --check`: correcto.

La documentación conserva el [historial de versiones](../CHANGELOG.md) como
registro del desarrollo. El uso actual del plugin se describe únicamente para
proyectos `curso-v3`; el profesor puede incorporar materiales de años anteriores
como fuentes sin que eso implique leer configuraciones de versiones previas.
