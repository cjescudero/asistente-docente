---
name: proyecto-docente-inicializacion-adaptacion
description: Inicializar o adaptar un proyecto docente, revisando primero sus contenidos y proponiendo su organización. Usar al iniciar un curso, reorganizar materiales o ajustar configuración e instrucciones existentes; preguntar por datos, destinos ambiguos y conflictos. Mover solo según una propuesta concreta aprobada. Recomendar el mapa sin crearlo automáticamente.
---

# Proyecto docente: inicialización y adaptación

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
2. Aplicar el [contrato de organización](../../docs/PROYECTO-DOCENTE.md). En una carpeta vacía preparar los tres espacios y `AGENTS.md`. En un curso existente asignar una o varias raíces por función y conservar la estructura interna del profesor. Presentar una previsualización. Mantener las instrucciones previas y consultar conflictos. Usar `Gestión del proyecto/` al necesitar persistencia. `AGENTS.md` recoge reglas, objetivos y contexto, y el catálogo e historial recogen los datos operativos.
3. Acordar las raíces y exclusiones que podrán alimentar la wiki. Admitir la selección aplazada. En todos los recorridos, incluso por enlaces, mantener fuera entregas, correcciones, datos personales, gestión y salidas pendientes de consolidación. Una tarea puntual puede utilizar un material generado como entrada expresa sin incorporarlo a la wiki.
4. Para un inventario solicitado, reconciliar con `catalog-sync`. Analizar agrupaciones temáticas completas antes que archivos sueltos. Comprobar solo lo necesario, anotar la evidencia, usar `catalog-classify` con `--inferred` para inferencias y reservar las confirmaciones para decisiones reales del usuario. Emplear agrupaciones y herencia lógicas. Consultar identidades dudosas y respetar contenidos ilegibles. Inventariar no acredita lectura completa.

## Organizar, reclasificar y consolidar

Mantener la organización física por defecto. Si se pide cambiarla, distinguir tres posibilidades: mantener las carpetas, crear categorías vacías o proponer una reorganización. Usar las operaciones del contrato. Preparar un plan por identidad, con destinos, número de documentos, agrupaciones, colisiones, dudas y excepciones. Mostrar los detalles de movimientos que se soliciten. Aceptar «solo estas prácticas» o cambios de destino en lenguaje natural y traducirlos a operaciones explícitas. Ejecutar exclusivamente la selección acordada. Comprobar el informe, los enlaces, el catálogo y las operaciones pendientes. Reanudar una operación interrumpida con su mismo plan.

Solo promover material generado por decisión expresa del docente. Mantener el origen IA y el identificador. Comprobar la selección y actualizar los derivados que correspondan. Si ya existe una wiki, revisar los cambios pendientes según la [skill del mapa](../mapa-docente-creacion-visualizacion/SKILL.md). Ante un nuevo original preservar su árbol, identificarlo en el catálogo y revisar únicamente las síntesis que lo requieran.

## Cierre y anfitriones

Si se solicita la adopción de un curso anterior, explicar las correspondencias y preservar los originales, instrucciones y cuestionarios congelados. Tras aceptar la propuesta usar `--adopt-v3` y reconciliar el catálogo. Repetir la inicialización sin esa decisión conserva el curso.

Comprobar que el anfitrión puede leer las instrucciones de la carpeta. En Codex y Claude Code puede pedirse su lectura explícita. En ChatGPT Work y Claude Cowork verificar acceso a la carpeta. Cuando no esté disponible Python, se pueden acordar los espacios, preparar instrucciones y hacer una propuesta mediante las herramientas de archivos. Dejar pendientes las operaciones que requieran garantías transaccionales hasta disponer de las utilidades.

Indicar las carpetas asignadas, lo ya comprobado y las decisiones que faltan. Invocar la ayuda inline para orientar el cierre. Recomendar crear el mapa si procede y esperar el encargo antes de crearlo.
