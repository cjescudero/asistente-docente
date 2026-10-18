# Historial

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

- Nueva `skill-iniciar-proyecto-docente`, con plantilla para crear o completar
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
