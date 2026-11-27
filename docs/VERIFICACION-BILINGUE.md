# Comprobación de la edición bilingüe

Comprobaciones locales con Python 3.12 en macOS y materiales sintéticos. El [ejemplo reproducible](../examples/bilingual-course/README.md) usa una lectura española sobre mediciones y cabeceras españolas en Moodle.

| Recorrido | Comprobación |
| --- | --- |
| Inicialización y adaptación | Las pruebas verifican las carpetas inglesas, la persistencia de las preferencias, el uso de raíces personalizadas y la conservación de las rutas al cambiar el idioma. |
| Materiales y cuestionarios | El ejemplo crea una wiki inglesa con enlace al original, un enunciado, una rúbrica separada, un banco y modelos en inglés y español. La CLI conserva numeración y pesos en papel y GIFT. Los PDF se generaron con Playwright y Google Chrome local. Se revisaron visualmente un modelo y un solucionario en inglés. |
| Moodle | Se exportaron comentarios en los dos idiomas sobre los mismos resultados. Las pruebas comprueban cabeceras, identificadores con ceros iniciales, notas y manifiesto congelado. La importación real en Moodle queda pendiente. |
| Lector y grafo | Se ejecutaron las comprobaciones de navegador de escritorio y móvil, enlaces HTML/Markdown, búsqueda en inglés y exclusión de información reservada de la vista estudiantil. |
| OpenCode 2.x | La lista `skills` del ejemplo se contrastó con la documentación oficial. La carga de las doce skills y el primer uso en 2.x quedan pendientes de prueba en esa versión. La comprobación anterior de descubrimiento se realizó en 1.18.31. |
| Claude Code | `claude plugin validate .` aceptó el marketplace. Mostró un aviso de icono para el directorio público. La distribución del proyecto utiliza un marketplace de GitHub. |
| Paquetes | La suite comprueba que los ZIP de OpenAI y Claude comparten los mismos recursos funcionales. Incluyen la guía inglesa, los ejemplos y las plantillas. Se conserva la identidad del repositorio y del plugin. |

La suite se ejecutó con `RUN_PDF_TESTS=1` y el ejecutable de Chrome indicado mediante `ASISTENTE_DOCENTE_CHROMIUM`. Las pruebas de instalación e interacción con esta edición en ChatGPT Work, Codex y Claude Cowork, y una conversación docente en Claude Code, requieren verificación en sus respectivos anfitriones. El ejecutable de Codex CLI disponible en la terminal de prueba carecía de su binario de plataforma.
