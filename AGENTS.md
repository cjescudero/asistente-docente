# Asistente docente

## Alcance

Este proyecto contiene doce skills docentes y utilidades portables para ChatGPT
Work y Claude Cowork. Por decisión explícita del usuario, carpeta, identificador
y paquetes se llaman `asistente-docente`, sin prefijo `plugin-`. Las doce skills
usan nombres sin prefijo `skill-` desde 0.7.0 por decisión del propietario;
las equivalencias anteriores se documentan en `docs/MIGRACION-0.7.md`.

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

- Generar papel, GIFT ofuscado y manifiesto desde el mismo modelo ordenado.
- Conservar pesos y tolerancias; nunca mover la respuesta correcta al principio.
- Separar soluciones docentes y documentos del estudiante. No trasladar
  enunciados, explicaciones o soluciones al contenido visible del GIFT ofuscado.
- Conservar el banco y su huella. El feedback usa el manifiesto y su snapshot,
  no un banco modificado después de generar el examen.
- No convertir datos ausentes en errores del estudiante ni resolver duplicados
  silenciosamente. Conservar notas, identificadores y columnas ajenas al feedback.
- Una salida HTML o un prompt no equivalen a un PDF o una imagen generados.
- El Mapa docente usa raíces elegidas por el usuario y enlaces Markdown relativos.
  El grafo es un derivado: la vista estudiantil excluye los datos reservados,
  incluidas sus dependencias, antes de serializar; un filtro visual no basta.

## Proyectos docentes

- El contrato compartido es `docs/PROYECTO-DOCENTE.md`: estructura `curso-v1`,
  configuración UTF-8 con rutas relativas y selección explícita del corpus.
- La iniciación prepara carpetas, configuración, LEEME e instrucciones. No crea
  ni propone la wiki. La creación del mapa registra un índice real e integra
  su consulta en el AGENTS.md del curso, preservando las reglas previas.
- Ante conflictos en instrucciones existentes, preguntar antes de cambiarlas.
  No imponer bloques generados ni modificar instrucciones globales.
- Respetar exclusiones incluso mediante enlaces. Resultados, borradores y el
  propio mapa quedan fuera del corpus; el archivo requiere selección explícita.
  Detectar páginas dependientes de fuentes retiradas antes de reutilizarlas.
- No sobrescribir ni mover originales sin una propuesta concreta aprobada.
  Mantener una ubicación para cada material; separar soluciones y estudiantes.
- Comprobar solo las entradas necesarias para el encargo. Adjuntos suficientes
  permiten tareas sencillas aunque el curso o el mapa aún no estén preparados.
- Los entornos operativos quedan fuera de los datos del curso y de instalaciones
  de solo lectura. Los nombres de carpetas no gestionan permisos ni sincronización.

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
