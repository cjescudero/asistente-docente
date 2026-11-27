# Comprobación de la edición bilingüe

Comprobaciones locales con Python 3.12 en macOS y materiales sintéticos. El [ejemplo reproducible](../examples/bilingual-course/README.md) usa una lectura española sobre mediciones y cabeceras españolas en Moodle.

| Recorrido | Comprobación |
| --- | --- |
| Inicialización y adaptación | Las pruebas verifican las carpetas inglesas, la persistencia de las preferencias, el uso de raíces personalizadas y la conservación de las rutas al cambiar el idioma. |
| Materiales y cuestionarios | El ejemplo crea una wiki inglesa con enlace al original, un enunciado, una rúbrica separada, un banco y modelos en inglés y español. La CLI conserva numeración y pesos en papel y GIFT. Los PDF se generaron con Playwright y Google Chrome local. Se revisaron visualmente un modelo y un solucionario en inglés. |
| Moodle | Se exportaron comentarios en los dos idiomas sobre los mismos resultados. Las pruebas comprueban cabeceras, identificadores con ceros iniciales, notas y manifiesto congelado. La importación real en Moodle queda pendiente. |
| Lector y grafo | Se ejecutaron las comprobaciones de navegador de escritorio y móvil, enlaces HTML/Markdown, búsqueda en inglés y exclusión de información reservada de la vista estudiantil. |
| OpenCode 2.4.2 | El registro del anfitrión devolvió los doce identificadores con rutas a los `SKILL.md` del ZIP fuente publicado de v0.15.0. Las pruebas con la corrección local verificaron la conversación en inglés desde el primer mensaje y la confirmación previa a los traslados. |
| Claude Code | `claude plugin validate .` aceptó el marketplace. Mostró un aviso de icono para el directorio público. La distribución del proyecto utiliza un marketplace de GitHub. |
| Paquetes | La suite comprueba que los ZIP de OpenAI y Claude comparten los mismos recursos funcionales. Incluyen la guía inglesa, los ejemplos y las plantillas. Se conserva la identidad del repositorio y del plugin. |

La suite se ejecutó con `RUN_PDF_TESTS=1` y el ejecutable de Chrome indicado mediante `ASISTENTE_DOCENTE_CHROMIUM`. Las pruebas de instalación e interacción con esta edición en ChatGPT Work, Codex y Claude Cowork, y una conversación docente en Claude Code, requieren verificación en sus respectivos anfitriones. El ejecutable de Codex CLI disponible en la terminal de prueba carecía de su binario de plataforma.


## Primer uso de la versión publicada en OpenCode 2.4.2

Se descargó el ZIP fuente de la release v0.15.0 y se verificó con su SHA-256 publicado. Se configuró la ruta absoluta a su directorio de skills en dos carpetas temporales y se empleó el modelo `openai/gpt-5.4-mini`. Se compararon los identificadores y las rutas devueltos por `GET /api/skill` con los doce archivos del paquete. En ambas sesiones la única petición inicial fue **“Set up my course”** y quedó registrada la invocación de `proyecto-docente-inicializacion-adaptacion`.

| Curso sintético | Resultado observado |
| --- | --- |
| Lectura española `Mediciones.md` en la raíz | El agente respondió y creó carpetas en español. Movió el original sin esperar aprobación. Al pedir expresamente “Please continue in English” contestó en inglés y preguntó cómo continuar. |
| Lectura inglesa en `Readings/Measurement.md` | Hubo mensajes intermedios en español. El mensaje final, las carpetas y el archivo de instrucciones quedaron en inglés. Conservó la lectura en su ubicación. |

## Repetición con los ajustes de 0.15.1

Se repitieron las dos sesiones con la misma versión de OpenCode y el mismo modelo. Cada sesión comenzó en una carpeta sintética nueva con `skills` apuntando a una copia del paquete que incorporaba la corrección.

| Curso y petición | Resultado observado |
| --- | --- |
| Lectura inglesa en `Readings/Measurement.md` y “Set up my course” | Cargó la skill de inicialización. Todos los mensajes visibles fueron en inglés. Configuró el curso con `Readings/` como espacio de referencia y conservó la lectura en su ubicación. |
| Lectura española `Mediciones.md` y “Set up my course” | Cargó la misma skill y todos los mensajes visibles fueron en inglés. Presentó el origen y destino del traslado propuesto y esperó confirmación. Al pedirle que mantuviera el original en la raíz, configuró los espacios ingleses y conservó el archivo en su sitio. |
| Petición directa para mover `Readings/Measurement.md` a `Readings/Week 1/Measurement.md` | Con las instrucciones generadas por la inicialización corregida, el agente mostró ambas rutas y pidió confirmación. El original conservó su ruta, identidad y contenido durante ese turno. Tras la aprobación explícita, apareció en el destino con el mismo contenido. En esta prueba el agente siguió la regla de confirmación de `AGENTS.md` sin invocar la skill. |
