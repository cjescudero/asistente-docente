---
name: proyecto-docente-inicializacion-adaptacion
description: "Use for course setup and adaptation, including requests to reorganise the course or to move or rename an original course file or folder. Reply in the user's language from the first message. Show exact paths and wait for approval before moving originals. “Set up my course” starts in English and keeps originals in place. Usar para iniciar o adaptar un curso, asignar carpetas, habilitar notas y cuando se pida reorganizar, mover o renombrar originales del curso. Responder en el idioma de la petición desde el primer mensaje y esperar confirmación explícita de las rutas de cada traslado."
---

# Proyecto docente: inicialización y adaptación

## First response and original files

Choose the conversation language from the teacher's request before sending any visible text. Follow an explicit language preference from the teacher if one applies. “Set up my course” means English from the first progress update through questions, proposals and the final response, even when the course files, filenames or skill instructions are in Spanish. Carry the chosen language into related skills. Apply the [language settings](../../docs/LANGUAGES.md) separately to generated materials.

Setup keeps original files and folders at their current paths. Before moving or renaming any original, display the exact source and destination for each proposed move, ask for explicit approval and end the turn. Do this even when the initial request supplies both paths. Apply only the moves covered by the teacher's subsequent reply. If the teacher changes a destination, show the revised move and wait for approval of that move.

Elige el idioma a partir de la petición antes de enviar el primer mensaje visible. Úsalo también en los avisos de progreso, las preguntas y el cierre. El idioma de las fuentes y de los nombres de carpeta puede ser distinto. «Inicia mi proyecto docente» empieza en español. Para mover o renombrar cualquier original, muestra los orígenes y destinos exactos, pregunta si los aprueba y termina el turno. Ejecuta solo los traslados que cubra la respuesta posterior.

With Python available, use `init-project --dry-run --language en|es` to preview the actual course folders and instructions in the working language. Use the preview's folder names when presenting the proposal. Apply the agreed setup with `init-project` in the same language. Pass a requested persistent material preference via `--output-language en|es`. Use the [English course profile](../../templates/en/course-profile.md) when appropriate.

Guiar al profesor ante «Inicia mi proyecto docente» o «Adapta mi curso existente»
hasta un proyecto preparado para trabajar. No exigir comandos ni una ficha completa. Esta skill prepara la
estructura y las instrucciones; no inicia otro flujo docente.

Combinar este encargo con [español conciso](../espanol-conciso-redaccion/SKILL.md) solo si el docente pide esa skill o el estilo de español simplificado, incluido un encargo expreso para todo el curso.

Ante dudas sobre el uso, flujo, archivos o resultados del plugin, o preguntas
sobre siguientes pasos y posibilidades, invocar
[Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) antes de responder.
Transferirle el objetivo, las decisiones conocidas y los resultados de esta tarea;
tras resolver la duda, retomar el encargo ya autorizado.

## Reconocer el curso y acordar los espacios

1. Leer las instrucciones existentes e identificar la raíz de la asignatura. Preguntar solo por lo que falte. Comprobar qué carpetas existen mediante inspección superficial antes de proponer destinos. Pedir al docente que identifique material de referencia, producción de IA y entregas cuando su función sea ambigua.
2. Aplicar el [contrato de organización](../../docs/PROYECTO-DOCENTE.md). En una carpeta vacía preparar los tres espacios, la carpeta de gestión y `AGENTS.md`. En un curso existente asignar una o varias raíces por función y conservar la estructura interna del profesor. Presentar una previsualización. Mantener las instrucciones previas y consultar conflictos. Al iniciar un curso nuevo, la utilidad crea la carpeta de gestión en el idioma de trabajo y la oculta en macOS y Windows. Reutilizar la carpeta de gestión existente, con su nombre y visibilidad actuales. `AGENTS.md` recoge reglas, objetivos y contexto, y el catálogo e historial recogen los datos operativos.
3. Acordar las raíces y exclusiones que podrán alimentar la wiki. Admitir la selección aplazada. En todos los recorridos, incluso por enlaces, mantener fuera las notas de trabajo del profesor, entregas, correcciones, datos personales, gestión y salidas pendientes de consolidación. Una tarea puntual puede utilizar un material generado como entrada expresa sin incorporarlo a la wiki.
4. Para un inventario solicitado, reconciliar con `catalog-sync`. Analizar agrupaciones temáticas completas antes que archivos sueltos. Comprobar solo lo necesario, anotar la evidencia, usar `catalog-classify` con `--inferred` para inferencias y reservar las confirmaciones para decisiones reales del usuario. Emplear agrupaciones y herencia lógicas. Consultar identidades dudosas y respetar contenidos ilegibles. Inventariar no acredita lectura completa.

Al proponer la estructura del curso, sitúa las carpetas de uso docente reservado directamente en `02 Organización del curso/Alumnado/` y `02 Organización del curso/Salidas de campo/`. Usa «Alumnado» para los listados, los informes de la oficina de apoyo a la diversidad (ADI) y otra documentación sobre las circunstancias del alumnado. Omite la carpeta intermedia «Datos docentes reservados». Si hay que trasladar carpetas existentes, incluye ambos destinos en la previsualización para que el docente pueda aprobar el traslado.

When proposing the reserved folders for a new English course, use “Course organisation”, “Student records” and “Field trips”. Keep the privacy exclusions and any existing paths. Present suggested folders for approval.

## Añadir un cuaderno docente a petición

Para ideas de clase, propuestas de examen o planificación personal, explicar la opción «Notas del curso». Dar de alta el espacio solo si el docente lo pide. Reutilizar el nombre y la carpeta que indique o usar `Notas del curso/` si prefiere una carpeta nueva con el nombre recomendado. En un curso configurado conservar los tres espacios existentes y la selección de fuentes. Aplicar las opciones del [contrato del curso](../../docs/PROYECTO-DOCENTE.md#guardar-ideas-y-borradores-del-profesor).

Mantener las notas accesibles para la edición del profesor y fuera del catálogo ordinario, el mapa y las vistas del alumnado. Para organizar ideas, proponer una agrupación por temas o por finalidad y conservar los archivos en su ubicación hasta recibir una petición concreta. El nombre de la carpeta expresa su uso editorial. Los permisos efectivos dependen del almacenamiento.

Si se pide consolidar una nota, identificar el documento elegido, revisar su contenido para el destino y la audiencia acordados, y comprobar colisiones antes de incorporarlo al espacio de referencia. Registrar la incorporación como material del profesor y comprobar la selección para la wiki. La promoción por identificador del catálogo corresponde a las producciones de IA ya inventariadas.

## Organizar, reclasificar y consolidar

Mantener la organización física por defecto. Si se pide cambiarla, distinguir tres posibilidades: mantener las carpetas, crear categorías vacías o proponer una reorganización. Para un traslado, reconciliar el catálogo y preparar un plan por identidad con `organize-plan`. Mostrar todos los pares origen–destino que se someten a aprobación, junto con colisiones, dudas y excepciones. La respuesta del profesor puede aprobar todos los pares o un subconjunto, por ejemplo «solo estas prácticas». Tras recibirla, ejecutar la selección correspondiente con `organize-apply`. Usar el plan para conservar el catálogo, las relaciones y el historial. Si faltan las utilidades, dejar el traslado pendiente. Comprobar el informe y los enlaces. Reanudar una operación interrumpida con su mismo plan y el alcance ya aprobado.

Solo promover material generado por decisión expresa del docente. Mantener el origen IA y el identificador. Comprobar la selección y actualizar los derivados que correspondan. Si ya existe una wiki, revisar los cambios pendientes según la [skill del mapa](../mapa-docente-creacion-visualizacion/SKILL.md). Ante un nuevo original preservar su árbol, identificarlo en el catálogo y revisar únicamente las síntesis que lo requieran.

## Cierre y anfitriones

Si se solicita la adopción de un curso anterior, explicar las correspondencias y preservar los originales, instrucciones y cuestionarios congelados. Tras aceptar la propuesta usar `--adopt-v3` y reconciliar el catálogo. Repetir la inicialización sin esa decisión conserva el curso.

Comprobar que el anfitrión puede leer las instrucciones de la carpeta. En Codex y Claude Code puede pedirse su lectura explícita. En ChatGPT Work y Claude Cowork verificar acceso a la carpeta. Cuando no esté disponible Python, se pueden acordar los espacios, preparar instrucciones y hacer una propuesta mediante las herramientas de archivos. Dejar pendientes las operaciones que requieran garantías transaccionales hasta disponer de las utilidades.

Indicar las carpetas asignadas, lo ya comprobado y las decisiones que faltan. Invocar la ayuda inline para orientar el cierre. Recomendar crear el mapa si procede y esperar el encargo antes de crearlo.

En cursos con carpetas numeradas, consultar los espacios y la selección del JSON. Localizar la carpeta de gestión existente como `Archivos de gestión del proyecto/` o `Gestión del proyecto/`, también cuando esté oculta en Finder.
