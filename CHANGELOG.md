# Historial

## 0.16.0

- Nueva skill «Inglés técnico claro / Plain Technical English», inspirada directamente en ASD-STE100. Se puede pedir por separado o al crear materiales con otra skill.
- La revisión de «Español conciso» aclara la aplicación a entregables bilingües y mejora los ejemplos sobre obligaciones, hipótesis y causalidad. Ambos estilos se aplican a petición expresa.

## 0.15.1

- La inicialización usa el idioma de la petición desde el primer mensaje, también cuando el material de referencia está en otro idioma.
- Antes de mover o renombrar un original, el agente muestra el origen y el destino y espera una confirmación explícita en un turno posterior. La inicialización incorpora esta regla a las instrucciones del curso.
- En OpenCode 2.4.2, «Set up my course» inició en inglés con una lectura en inglés y con otra en español. Una prueba adicional comprobó la confirmación antes del traslado. [Registro de pruebas](docs/VERIFICACION-BILINGUE.md).

## 0.15.0

- Recorrido docente en inglés y español, con idioma de conversación y de materiales independientes. Se conserva la identidad del plugin y de las doce skills.

## 0.14.5 — 2026-11-26

- La propuesta de estructura sitúa «Alumnado» y «Salidas de campo» directamente en «02 Organización del curso». Ambas carpetas son de uso docente reservado y quedan fuera de las fuentes del Mapa docente.

## 0.14.4 — 2026-11-26

- Los cursos nuevos crean «Archivos de gestión del proyecto» al iniciarse y la ocultan automáticamente en macOS y Windows.
- Los cursos existentes conservan el nombre y la visibilidad de su carpeta de gestión. La configuración y el catálogo se guardan cuando hacen falta.

## 0.14.3 — 2026-11-26

- La guía de instalación explica cómo cargar las skills en OpenCode 1.x y 2.x desde una copia local y comprobar el primer uso con el curso de ejemplo.

## 0.14.2 — 2026-11-26

- El plugin reconoce «Archivos de gestión del proyecto», incluso oculta en Finder, y conserva la compatibilidad con «Gestión del proyecto». Si ambas existen, solicita aclarar cuál está activa.
- La documentación explica cómo trabajar con espacios docentes numerados y conservar la selección de fuentes del mapa.

## 0.14.1 — 2026-11-25

- La evaluación entrega un CSV listo para Moodle. La guía muestra cómo identificar al alumnado por correo y asignar la nota y la retroalimentación de cada actividad.

## 0.14.0 — 2026-11-25

- La evaluación revisa descuentos y máximos contra el enunciado definitivo y las evidencias de cada entrega.
- El informe docente documenta cada decisión y el comentario informativo de Moodle explica al estudiante los motivos con ejemplos de su propio trabajo.

## 0.13.0 — 2026-11-24

- Nuevo espacio opcional «Notas del curso» para las ideas y la planificación del profesor. Se puede habilitar al iniciar un curso o después, con una carpeta nueva o existente y el nombre elegido.
- Las notas quedan fuera del catálogo de materiales, del Mapa docente y de las vistas del alumnado. Incorporar una nota como referencia requiere elegir el documento, su destino y su audiencia.
- La inicialización y la ayuda explican dónde guardar los borradores y cómo proponer agrupaciones. Los cursos con tres espacios conservan su configuración.

## 0.12.0 — 2026-11-24

- Espacios asignables para fuentes, producción y entregas. La organización física del docente se conserva por defecto.
- Catálogo versionado, clasificación jerárquica, registro de operaciones y reconciliación incremental por identidad.
- Planes de organización con aprobación completa, parcial o modificada, recuperación de traslados e incorporación explícita de material de IA.
- Seguimiento de las fuentes de la wiki y sus derivados por identidad y versión. Las entregas y la gestión quedan fuera del corpus.

- La guía de primer uso cubre ChatGPT Work, Codex, Claude Cowork y Claude Code.
- Español simplificado bajo petición, como encargo independiente o combinado con otra skill.
- Criterios editoriales flexibles y actualización de las instrucciones generadas del curso y del mapa.

## 0.11.4 — 2026-10-21

- Instrucciones de curso para usar subagentes en subtareas independientes cuando el anfitrión lo permita.
- Revisión e integración centralizadas, con consolidación única de la hoja Moodle.
- Elección explícita del docente antes de usar un modelo más sencillo; autorización reutilizable por lote.
- Conservación de instrucciones previas y ejemplos actualizados.

## 0.11.3 — 2026-10-21

- Presentación para profesorado en `.zenodo.json`, con recorridos, alcance y enlaces.
- Metadatos incluidos en el paquete fuente; DOI y versión gestionados por la integración GitHub–Zenodo.
- Incluye la guía visual de los procesos docentes.

## 0.11.2 — 2026-10-21

- Categorías Moodle por cuestionario y nombre visible Modelo 01, Modelo 02…
- Categoría y nombre registrados en el manifiesto y explicados en el LEEME.
- Pesos, tolerancias e identificadores técnicos conservados.

## 0.11.1 — 2026-10-21

- Al terminar una actividad, ofrecer preparar su carpeta de recepción con el
  mismo identificador, separando trabajos recibidos, hoja Moodle y corrección.
- LEEME reutilizable con enlaces a los criterios, entradas necesarias y petición
  de evaluación; reutilización de lotes existentes sin sobrescrituras.
- Aclarar el uso de CSV frente a Excel y el encargo conjunto de corrección,
  calificaciones y feedback. El profesor no tiene que preparar JSON.
- Ejemplo completo de recepción y revisión de referencias antiguas en las
  instrucciones de actividades y calificaciones.

### Presentación y puntuaciones de cuestionarios

- Cabecera compacta, identificación en dos columnas y opciones con círculos o cuadrados.
- Criterios predeterminados compartidos por bancos y modelos; pesos negativos GIFT conservados.
- Comprobaciones técnicas de Moodle reservadas al docente.

## 0.11.0 — 2026-10-21

- Nuevos cursos `curso-v3`: materiales nuevos en `materiales_generados/` y
  configuración e inventario en `_datos_internos_proyecto/`.
- Cada material usa `_datos_internos/` para sus registros. Los cuestionarios
  reúnen allí selección, manifiesto, cobertura y bancos congelados, con enlaces
  a modelos, solucionarios y GIFT en su `LEEME.md`.
- Catálogos y registros del mapa en carpetas técnicas de su ámbito. El formato
  de proyecto admitido es `curso-v3`; una configuración en otra ubicación o de
  otra versión produce un diagnóstico en lugar de leerse como curso vigente.
- Reorganización guiada y previsualizada de materiales aportados, sin traslados
  automáticos ni regeneración de cuestionarios utilizados. Se conserva la ayuda inline
  preparada en 0.10.1.
- Nombres de archivos y ejemplos del flujo actual normalizados a
  «cuestionario». La CLI usa `build-cuestionarios`. El módulo Python pasa a
  `docencia.cuestionarios`.

## 0.10.1 — preparación local

- Ayuda inline mediante `proyecto-docente-ayuda` ante dudas de uso, archivos, resultados, posibilidades y siguientes pasos, también durante otras skills y al orientar al cierre.
- Recuperar el contexto disponible de la conversación y comprobar el estado pertinente del curso; evitar preguntas repetidas, menús innecesarios y cierres recursivos.
- Preferencia de invocación implícita explícita e instrucciones de curso generadas para estructuras existentes y nuevas, conservando el procedimiento de conflictos.

## 0.10.0 — 2026-10-21

- Entrega de bancos como archivos GIFT y metadatos individuales; ZIP opcional.
  Identificadores nuevos por principal y variante: `01-A`, `01-B`, `02-A`…
  Los IDs y snapshots anteriores se conservan.

- Tres skills agrupadas bajo Cuestionarios y carpetas `cuestionarios/` para cursos nuevos; rutas anteriores y registros `examen` conservados.
- Cuatro modelos por defecto, propuesta razonada de cantidad y duración y bancos con preguntas principales y variantes identificadas.
- Selección sin dos variantes de una misma principal por modelo y preferencia por familias distintas entre modelos.
- Wiki explicativa con conceptos, relaciones, condiciones, ejemplos y límites trazables; índice como navegación, originales para profundizar y verificar.
- Leyenda de destinatarios del grafo y distintivo para materiales pendientes de clasificar.

## 0.9.0 — 2026-10-21

- Doce skills con identificadores y nombres visibles agrupados por categoría,
  descripciones de interfaz y equivalencias documentadas, sin alias duplicados.
- Creación y visualización del mapa unificadas: crear o actualizar, regenerar
  solo vistas, o mostrar las existentes; consulta separada de solo lectura.
- Inicialización y adaptación con inventario previo, clasificación contrastada,
  propuesta concreta de movimientos y aprobación completa o parcial; conservar
  la organización si se rechaza, sin ampliar el corpus automáticamente.

- Nuevos cursos con estructura `curso-v2`: originales en `fuentes/`, trabajos
  nuevos por tipo en `creados/`, mapa independiente y resultados privados con
  archivos recibidos y correcciones separados.
- Estados visibles y registro `material-docente.json`, sin mover materiales al
  revisarlos o reutilizarlos. La wiki exige selección explícita y estado
  revisado o listo para incorporar documentos creados.
- Cierre contextual de las doce skills: inicio → mapa; actividad → corrección;
  banco → modelos impresos → feedback. Comprobar indicios antes de proponer
  repetir resultados y explicar las entradas pendientes, sin ejecutar otro flujo.
- Español claro por defecto y apoyos de apuntes y diapositivas visuales
  individuales, respetando las preferencias del profesor.
- Catálogos con rutas relativas al curso para combinar bancos originales y
  nuevos sin copias; exámenes con separación de alumnado y docente mediante
  `--layout curso-v2`, conservando la salida anterior.
- Compatibilidad con `curso-v1`, propuesta de migración sin movimientos
  automáticos, ejemplos actualizados y paquetes desde una fuente común.

## 0.8.0 — 2026-10-20

- Salida UTF-8 explícita de la CLI y del ejemplo reproducible, también en
  terminales de Windows con codificación heredada; lecturas de pruebas portables.

- Nueva skill `orientar-docente`: trece skills, ayuda contextual y ejemplos de
  peticiones sin ejecutar otros procesos. La inicialización recomienda el mapa
  y ofrece orientación, conservando el encargo explícito para crearlo.
- Carpeta de entregas por actividad y convocatoria, fuera de la wiki;
  actualización aditiva con conservación de instrucciones y consulta de conflictos.
- Diseño dialogado de actividades para cualquier disciplina y alumnado con
  acceso a IA; enunciado, plantillas, rúbrica docente y registro de versión.
- Bancos vinculados a uno o varios materiales, catálogo validado y composición
  reproducible de modelos con cuotas, procedencia y cobertura verificables.
- Exportación de evaluaciones estructuradas a hoja de tarea o libro de
  calificaciones Moodle, con cálculos comprobados, auditoría y bloqueos de ambigüedad.
- Feedback con hasta tres prioridades, umbral y evidencia configurables, y
  cruce opcional con el libro de calificaciones sin modificar sus notas.
- Ejemplos sintéticos, compatibilidad con bancos y manifiestos anteriores y
  paquetes comunes. Las importaciones reales y la publicación son pasos separados.

## 0.7.0 — código en main

- Inicio rápido con incorporación de marketplaces GitHub e instalación posterior;
  guías separadas para profesores, administradores y usuarios avanzados.
  Sin distribución en los directorios públicos de ChatGPT o Claude.
- Puesta en marcha guiada con estructura de curso, configuración de fuentes,
  LEEME e instrucciones locales respetadas; no crea ni propone la wiki.
- Selección explícita de carpetas y exclusiones, diagnóstico de entradas y
  previsualización de la preparación y de las migraciones.
- Corpus separado de resultados, borradores y mapa; revisión de dependencias
  al retirar fuentes y comprobación previa a generar derivados.
- Nombres de las doce skills sin prefijo y tabla de equivalencias para actualizar
  proyectos anteriores sin duplicar skills.
- Materiales en una sola ubicación y guía para profesores en tres pasos;
  documentación de compatibilidad, capacidades y migración.
- Fuente y marketplaces 0.7.0 en la rama `main`. Se conserva la release 0.6.0;
  la actualización del código no crea una nueva release ni acredita instalaciones
  reales en los anfitriones.

## 0.6.0

- Preparación para GitHub bajo MIT, con repositorio y avisos de terceros.
- Catálogos de instalación y adaptadores Claude/Codex generados desde una fuente.
- Instalador Python común a macOS, Linux y Windows, con PDF y desarrollo opcionales.
- Fuente distribuible sin entornos, cachés ni datos operativos; comprobación pública.
- Apuntes en el idioma del encargo, identificadores de evaluación configurables
  y ficha vacía sin disciplina, nivel ni escala heredados.
- Guías públicas de instalación, contribución y publicación y CI multiplataforma.
- Código QR del repositorio en el README y PNG reutilizable en presentaciones.
- Conservación de saltos de línea e integridad de dependencias al clonar en Windows.

## 0.5.2

- La inicialización respeta contenido y organización del AGENTS.md existente,
  modifica solo lo indicado y pregunta ante cualquier conflicto.
- Registra español claro como preferencia del proyecto y aclara ubicación y
  tipos de materiales solo cuando faltan. No inicia la creación del mapa.
- La skill de redacción admite la selección predeterminada explícita del proyecto.

## 0.5.1

- Iniciar el proyecto prepara únicamente sus instrucciones generales; no ofrece
  ni invoca la creación del Mapa docente ni pregunta por sus carpetas.
- Crear o actualizar el mapa integra en el `AGENTS.md` del proyecto la consulta
  del índice como punto de partida, con recorrido de los enlaces pertinentes y
  acceso a los originales cuando haga falta, sin leer todo el corpus.
- La plantilla de consulta pertenece a la skill de crear el mapa. Conserva y
  actualiza el bloque existente, incluido el creado con 0.5.0, sin duplicarlo ni
  reemplazar las reglas del profesor. No exige inicializar antes el proyecto.

## 0.5.0

- Nueva `iniciar-proyecto-docente`, con plantilla para crear o completar
  el `AGENTS.md` del proyecto docente conservando sus instrucciones existentes.
  El plugin reúne doce skills.
- Las tareas docentes parten del índice de la wiki, recorren los enlaces
  pertinentes de forma recursiva y consultan los originales cuando necesitan
  verificar la evidencia. La consulta evita ciclos y respeta vigencia y acceso.
- Tras preparar las instrucciones, se propone crear el mapa y se solicitan las
  carpetas de origen que falten. Se reutilizan decisiones y mapas existentes;
  aplazar la wiki deja un estado pendiente explícito.
- El `AGENTS.md` del plugin recoge la comprobación en navegador del lector y del
  grafo, con revisión de navegación, Reorganizar, filtros y selección.

## 0.4.0

- «Reorganizar» distribuye los nodos y relaciones visibles, conserva filtros y
  selección y tiene en cuenta etiquetas y proporción de la pantalla. «Ajustar»
  conserva las posiciones y solo cambia el encuadre.
- Lector `index.html` autónomo desde el índice y las páginas Markdown registradas,
  con navegación, búsqueda, anclas, historial del navegador y acceso al original.
  El contenido reservado se distingue y el lector completo es de uso docente.
- El panel del grafo ofrece los documentos de la wiki asociados al nodo, tanto
  renderizados como en Markdown. El lector enlaza de vuelta al grafo.
- La creación del mapa genera ambos derivados. Nuevo `build_wiki.py` y opción
  `--wiki-output` de `build_graph.py`; se conserva la generación de grafos aislados.
- La exportación estudiantil sigue sin enlaces a archivos ni lector docente.

## 0.3.0

- Mapa docente como nombre propio: crear, consultar y visualizar; once skills en total.
- Markdown estándar y enlaces relativos, sin frontmatter obligatorio ni dependencia
  de Notion u Obsidian.
- Registro de fuentes versión 2 con varias carpetas elegidas explícitamente,
  `source_roots` y `pages`; originales intactos y tipos separados de accesos.
- Organización de conceptos, presentaciones, apuntes, prácticas y talleres, con
  evaluaciones, soluciones y criterios reservados separados.
- Grafo HTML autónomo con arrastre, zoom, búsqueda, filtros y panel; se actualiza
  al mantener el mapa cuando hay Python y se puede regenerar por separado.
- Vista docente con enlaces a archivos y evaluaciones ocultas inicialmente como
  filtro; vista estudiantil sin datos no autorizados ni dependencias transitivas,
  y sin enlaces salientes a archivos.
- Compatibilidad de validación con registros de versión 1; migración solicitada
  en una copia del mapa, sin modificar los originales.
- Ejemplo de siete fuentes en dos raíces y grafos para ambas audiencias;
  paquetes Agent Plugins y Claude actualizados desde una fuente común.

## 0.2.0

- Dos skills nuevas: organizar y consultar la biblioteca docente; diez en total.
- Índice del material del profesor con fichas de fuentes y mapas temáticos,
  distinguiendo vigencia, acceso y alcance real de lectura.
- Plantillas portables, ejemplo sintético y consulta resuelta con fuentes precisas.
- Validador de inventario, enlaces y huellas; lectura sin cambios en las fuentes.
- Adaptación conceptual de WikiForge, Wiki Query y LLM Wiki con procedencia.
- Los dos paquetes incluyen las nuevas capacidades desde la misma fuente.

## 0.1.0

- Ocho skills genéricas y ficha docente reutilizable.
- Parser GIFT estricto y modelos reproducibles desde una fuente ordenada común.
- PDF/HTML del estudiante y solucionario separados, GIFT ofuscado y snapshot.
- Feedback conceptual configurable, CSV conservador e informe de incidencias.
- MathJax local y comprobación explícita de capacidades PDF.
- Paquetes Agent Plugins y Claude generados desde los mismos contenidos.
- Ejemplos sintéticos de humanidades y ciencias y pruebas de regresión.

Las instalaciones en ChatGPT Work y Claude Cowork y las importaciones en Moodle
se verifican por separado; véase [validación](docs/VALIDACION.md).
