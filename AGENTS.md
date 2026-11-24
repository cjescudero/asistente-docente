# Asistente docente

## Alcance

Este proyecto contiene doce skills docentes y utilidades portables para ChatGPT
Work, Codex, Claude Cowork y Claude Code. Por decisión explícita del usuario, carpeta, identificador
y paquetes se llaman `asistente-docente`, sin prefijo `plugin-`. Las skills
usan nombres sin prefijo `skill-` y se agrupan por categoría. La organización
vigente se documenta en `docs/PROYECTO-DOCENTE.md`.

## Fuentes y portabilidad

- Mantener una única fuente en `skills/`, `scripts/` y `docencia/`; generar los
  paquetes Agent Plugins y Claude con `scripts/build_release.py`.
- No modificar las skills de origen ni depender de rutas personales, del
  directorio de ejecución, de TI o de herramientas exclusivas de un anfitrión.
- Los datos y resultados docentes viven fuera del paquete instalado. Usar datos
  sintéticos en ejemplos y pruebas; no incorporar entregas ni notas reales.
- No incluir entornos virtuales, cachés, credenciales ni binarios del navegador.
- Contenido propio bajo MIT, por decisión del propietario. Conservar LICENSE y
  los avisos de terceros; el repositorio es cjescudero/asistente-docente.
- Generar adaptadores y catálogos con scripts/sync_manifests.py; no mantener
  versiones o metadatos divergentes respecto a plugin.json.
- Distribuir mediante marketplaces de GitHub; no presuponer disponibilidad en
  los directorios públicos de ChatGPT o Claude. Documentar la incorporación del
  marketplace y la instalación posterior del plugin según `docs/INSTALACION.md`.

## Invariantes

- Los cuestionarios parten de cuatro modelos salvo indicación distinta. Proponer
  cantidad de preguntas principales por cobertura conceptual y explicar el motivo;
  las variantes no incrementan esa cobertura. Acordar cantidad y estimación de
  duración ajustable antes de componer modelos. No incluir dos variantes de una
  misma familia en un modelo; priorizar familias distintas y luego variantes
  distintas entre modelos, conservando cuotas y trazabilidad.
- Entregar bancos como GIFT y metadatos individuales, sin ZIP por defecto.
  En bancos nuevos usar número de principal y letra de variante (`01-A`, `01-B`),
  con correspondencia en `family_id` y `variant_id`. Mantener IDs de bancos
  anteriores y snapshots utilizados; la numeración impresa es independiente.
- El mapa debe explicar el contenido y sus relaciones, condiciones, ejemplos y
  límites sustentados por lo revisado. El índice facilita navegar; las páginas
  permiten comprender sin abrir originales salvo para ampliar o verificar.

- Generar papel, GIFT ofuscado y manifiesto desde el mismo modelo ordenado.
- Conservar pesos y tolerancias; nunca mover la respuesta correcta al principio.
- Separar soluciones docentes y documentos del estudiante. No trasladar
  enunciados, explicaciones o soluciones al contenido visible del GIFT ofuscado.
- Conservar el banco y su huella. El feedback usa el manifiesto y su snapshot,
  no un banco modificado después de generar el cuestionario.
- En cuestionarios combinados, conservar banco y pregunta originales, cuotas de
  cobertura y dificultad, reutilización y snapshots. No inventar preguntas para
  suplir un reparto inviable ni prometer un óptimo matemático.
- No convertir datos ausentes en errores del estudiante ni resolver duplicados
  silenciosamente. Conservar notas, identificadores y columnas ajenas al feedback.
- La exportación de actividades actualiza solo nota y comentario autorizados,
  con identificación explícita, comprobación de cálculo y auditoría. El feedback
  de cuestionarios conserva la nota de Moodle y prioriza hasta tres dificultades.
- Diseñar actividades mediante diálogo para cualquier disciplina, considerando
  acceso a IA. Vincular enunciado, plantillas, rúbrica y versión; reservar la
  rúbrica completa y soluciones al docente, comunicando criterios generales.
- Una salida HTML o un prompt no equivalen a un PDF o una imagen generados.
- El Mapa docente usa raíces elegidas por el usuario y enlaces Markdown relativos.
  El grafo es un derivado: la vista estudiantil excluye los datos reservados,
  incluidas sus dependencias, antes de serializar; un filtro visual no basta.

## Proyectos docentes

- Aplicar el contrato de espacios asignables de `docs/PROYECTO-DOCENTE.md`. Respetar el árbol del profesor y crear gestión cuando haya datos que persistir. Separar identidad, ubicación, versión, origen, clasificación y consolidación. Clasificar por agrupaciones lógicas con prioridad a confirmaciones.
- Serializar los cambios en el catálogo y conservar el historial y la recuperación de operaciones. Los traslados y consolidaciones requieren operaciones concretas aceptadas. Preservar originales, unidades docentes y snapshots. Reconciliar sin releer contenido inalterado y actualizar únicamente dependencias afectadas.
- La skill del mapa distingue crear/actualizar, regenerar vistas y mostrar vistas
  existentes. Regenerar vistas conserva páginas y metadatos; mostrar no regenera.
  Mantener la consulta separada y de solo lectura.
- La iniciación asigna espacios, conserva instrucciones y prepara la configuración cuando se necesita. Ofrece
  orientación y recomienda el mapa, sin crearlo ni invocarlo sin encargo.
  `proyecto-docente-ayuda` se invoca siempre como ayuda inline ante dudas de uso,
  flujos, archivos, resultados, posibilidades o siguientes pasos, también durante
  otra skill y al orientar al cierre. Revisa la conversación disponible y el estado
  pertinente del curso, sin repetir datos conocidos ni leer todo el corpus.
  No invocarse recursivamente ni ejecutar nuevos procesos por orientar. La creación del mapa registra un índice real e integra
  su consulta en el AGENTS.md del curso, preservando las reglas previas.
- Ante conflictos en instrucciones existentes, preguntar antes de cambiarlas.
  No imponer bloques generados ni modificar instrucciones globales.
- Consultar únicamente las fuentes seleccionadas. Mantener entregas y gestión fuera del corpus, incluso a través de enlaces. Los materiales generados entran al conocimiento tras una consolidación expresa y dentro de las raíces seleccionadas.
- Organizar los lotes en la raíz de entregas acordada, por actividad y convocatoria, con originales en `recibidos/` y hojas derivadas en `correccion/`. Ofrecer preparar la recepción al terminar una actividad. La utilidad Moodle usa CSV.
- No sobrescribir ni mover originales sin una propuesta concreta aprobada.
  Mantener una ubicación para cada material; separar soluciones y estudiantes.
- Comprobar solo las entradas necesarias para el encargo. Adjuntos suficientes
  permiten tareas sencillas aunque el curso o el mapa aún no estén preparados.
- Los entornos operativos quedan fuera de los datos del curso y de instalaciones
  de solo lectura. Los nombres de carpetas no gestionan permisos ni sincronización.
- Al terminar una skill, aplicar `docs/FLUJOS-DOCENTES.md`: sugerir los siguientes
  pasos según registros y archivos pertinentes, sin ejecutar tareas ni dar por
  completados resultados por la mera existencia de una carpeta. Respetar los
  flujos inicio → mapa, actividad → corrección y banco → cuestionario → feedback.
  Ofrecer apuntes y diapositivas visuales individuales como apoyos. Aplicar la skill de español
  simplificado solo cuando el docente solicite la skill o ese estilo.

## Comprobaciones

Desde esta carpeta, con el intérprete del entorno preparado (en macOS/Linux,
`.venv/bin/python`; en Windows, `.venv\Scripts\python.exe`):

```sh
python -m unittest discover -s tests -v
python scripts/sync_manifests.py --check
python scripts/validate_plugin.py --public
python scripts/validate_library.py examples/mapa-docente/mapa-docente
python scripts/build_release.py --source
```

Las pruebas PDF necesitan las dependencias de `requirements-pdf.txt` y Chromium de
Playwright. Comprobar visualmente los PDF representativos. Registrar por separado
la validación local y las pruebas reales en ChatGPT Work, Claude Cowork y Moodle.
Para cambios del grafo o del lector de la wiki, comprobar en un navegador los
enlaces entre documentos y los accesos HTML/Markdown. Verificar que Reorganizar
redistribuye solo los nodos visibles y conserva filtros y selección; Ajustar
solo cambia el encuadre. Ejecutar las comprobaciones que correspondan:

```sh
python tests/check_graph_browser.py
python tests/check_graph_layout.py
python tests/check_wiki_browser.py
```

Para cambios de inicialización y selección, comprobar proyecto nuevo, repetición,
AGENTS.md previo, conflictos, selección aplazada, exclusiones, retirada de fuentes
y migraciones con colisiones y enlaces. Verificar el modo de previsualización
sin cambios y el uso desde otra carpeta y con instalación de solo lectura.

Revisar escritorio y móvil y guardar las capturas fuera del paquete. Si no hay
navegador disponible, declarar esa revisión pendiente; las pruebas unitarias no
la sustituyen.

## Mantenimiento

Consultar las referencias concretas de cada skill. Mantener instrucciones y
contratos coherentes con las CLI. Conservar cambios ajenos y limitar las modificaciones al encargo autorizado.
Proponer por separado el mantenimiento adicional de skills o instrucciones
antes de aplicarlo. No ampliar el alcance a otros proyectos ni publicar o
importar calificaciones automáticamente.
