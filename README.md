# Asistente docente

Trece skills para organizar fuentes, crear materiales, evaluar y devolver feedback en
cualquier asignatura. La fuente común genera paquetes para **ChatGPT Work** y
**Claude Cowork**. Versión **0.8.0**, bajo [MIT](LICENSE).
[Instalación y primer uso](docs/INSTALACION.md) ·
[Descargar la versión 0.8.0](https://github.com/cjescudero/asistente-docente/releases/tag/v0.8.0) ·
[Repositorio](https://github.com/cjescudero/asistente-docente).

## Inicio rápido

**Asistente docente se distribuye desde GitHub mediante marketplaces
personalizados. No se publicará en los directorios públicos de ChatGPT ni de
Claude.** Un marketplace es un catálogo que incorporas a tu aplicación; después
puedes instalar los plugins que contiene.

### Instalación en ChatGPT

Primero, una persona con **permisos de administración** debe incorporarlo al
espacio de trabajo de ChatGPT:

1. Abrir la [consola de administración de ChatGPT](https://admin.openai.com)
   y elegir el espacio de trabajo.
2. Entrar en **Plugins → Añadir → Importar marketplace**.
3. Introducir `https://github.com/cjescudero/asistente-docente` como origen y
   **dejar vacío el campo Ruta**.
4. Importar el marketplace, autorizar GitHub si se solicita y habilitar
   **Asistente docente** para los profesores.

Después, el profesor puede abrir **Plugins**, elegir la sección de su espacio
de trabajo e instalar **Asistente docente**. Si no tienes permisos de
administración, facilita el enlace del repositorio al responsable de tu
organización para que realice esa configuración inicial.
[Procedimiento oficial de importación](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github).

Si utilizas una cuenta individual sin espacio de trabajo administrado, consulta
la [alternativa avanzada con Codex](docs/INSTALACION.md#codex-cli).

### Instalación en Claude

1. Abre **Personalizar → Plugins**. En Cowork, entra primero en **Cowork**.
2. Elige **Agregar → Agregar mercado → Agregar desde un repositorio**.
3. Introduce `https://github.com/cjescudero/asistente-docente` y añade el marketplace.
4. En **Descubrir**, selecciona **Asistente docente** (puede aparecer como
   `asistente-docente`) del marketplace que acabas de añadir y pulsa **Agregar**
   para instalarlo.

Esos son los nombres de la [ayuda oficial en español de Claude](https://support.claude.com/es/articles/13837440-usar-plugins-en-claude).
En inglés: **Customize → Plugins → Add → Add marketplace → Add from a repository**.
Si tu organización restringe los marketplaces, pide al responsable que autorice
esta fuente.

### Primer uso

Inicia una conversación nueva en ChatGPT Work o Claude Cowork, abre o selecciona
la carpeta del curso y permite al agente trabajar con ella. Escribe:

**«Inicia mi proyecto docente».**

El agente pregunta por el contexto, los materiales y las exclusiones que falten;
prepara las carpetas `alumnado/`, `docente/` y `archivo/`, la configuración y una
guía breve. Conserva tus instrucciones y consulta los conflictos. Comprueba qué
está disponible y qué falta. Al terminar, te orienta y recomienda crear el mapa
docente; lo creará cuando se lo pidas. Si ya hay
materiales, presenta una propuesta antes de reorganizarlos. No necesitas escribir
comandos.

Este recorrido corresponde a la **0.8.0**. Si ya tienes el marketplace,
actualiza su contenido y comprueba la versión instalada. Publicar una versión
en GitHub no actualiza por sí solo una instalación existente. [Guía para el profesor](docs/PROYECTO-DOCENTE.md) ·
[Actualizar a 0.8](docs/MIGRACION-0.8.md).

<a href="https://github.com/cjescudero/asistente-docente">
  <img src="assets/qr-repositorio.png" alt="Código QR del repositorio de Asistente docente en GitHub" width="288" height="288">
</a>

Escanea el QR para abrir el repositorio. [Descargar el QR en PNG](assets/qr-repositorio.png)
para usarlo en presentaciones.

## Qué incluye

Orientación contextual mediante «¿Qué puedo hacer ahora?». Puesta en marcha
con estructura de curso, selección de fuentes, configuración,
`LEEME.md` y `AGENTS.md`; Mapa docente con índice, conceptos,
consultas trazables y grafo HTML, actividades y
enunciados, apuntes, evaluación de entregas con rúbricas, bancos
GIFT asociados a los materiales, modelos equilibrados combinando bancos,
GIFT ofuscado, notas de actividades y feedback priorizado para Moodle, redacción clara e
infografías didácticas. [Guía de uso](docs/USO.md) y
[catálogo de skills](docs/CATALOGO.md).

Las fuentes docentes y los datos del alumnado pertenecen al proyecto del
profesor, no a la instalación del plugin. Las tareas simples pueden partir de
una conversación; la [ficha reutilizable](templates/ficha-asignatura.json) permite
mantener contexto entre encargos. Los materiales escritos usan Markdown y PDF;
el Mapa docente conserva sus páginas navegables en Markdown estándar, un registro
JSON, un lector `index.html` y un grafo HTML autónomo. Consulta la [guía del Mapa docente](docs/MAPA-DOCENTE.md)
y su [índice de ejemplo](examples/mapa-docente/mapa-docente/index.md).

## Puesta en marcha del proyecto docente

`iniciar-proyecto-docente` organiza `alumnado/`, `docente/` y `archivo/`, guarda
la selección explícita en `proyecto-docente.json` y prepara `LEEME.md` y
`AGENTS.md`. Conserva las instrucciones existentes y pregunta ante conflictos.
Establece `redactar-espanol-claro` para escribir en español y aclara dónde están
los contenidos y qué son cuando falte esa información.

Los materiales nuevos se preparan en `docente/borradores/`; las entregas,
calificaciones y feedback se guardan en `docente/resultados/`, fuera de la wiki.
`alumnado/conocimientos/` recoge aclaraciones útiles, sin duplicar el mapa.
Los lotes de entregas se organizan por actividad y convocatoria en
`docente/resultados/entregas/`. La carpeta `docente/mapa-docente/` queda vacía
hasta un encargo de creación. Puedes pedir orientación en cualquier momento.
La selección de fuentes no autoriza su publicación ni acredita que se hayan leído.
Consulta el [árbol completo y el contrato](docs/PROYECTO-DOCENTE.md).
El [curso de ejemplo](examples/proyecto-docente/README.md) permite probar la
iniciación, la selección y las exclusiones con materiales sintéticos.

## Del material a la evaluación

Puedes empezar por **«¿Qué puedo hacer ahora con mi asignatura?»**. La ayuda
consulta los índices disponibles y propone siguientes pasos con sus entradas.

- **Actividades:** diálogo sobre conocimientos, fuentes y condiciones de IA;
  enunciado, plantillas pertinentes y rúbrica completa reservada al docente.
- **Bancos y exámenes:** preguntas vinculadas a materiales o actividades,
  reparto de contenidos y dificultad, modelos PDF y GIFT ofuscado sincronizados.
- **Corrección:** evidencias por criterio y actualización de una copia de la
  hoja de tarea o del libro de calificaciones, con identificadores explícitos.
- **Feedback de examen:** hasta tres dificultades prioritarias y recomendaciones
  desde materiales del estudiante; conserva las notas calculadas por Moodle.

[Actividades](docs/ACTIVIDADES.md) · [Bancos](docs/BANCOS.md) ·
[Calificaciones](docs/CALIFICACIONES.md) · [Recorrido de ejemplo](examples/recorrido-docente/README.md).
Las importaciones en Moodle son manuales. Las ayudas complementarias son
infografías y diapositivas visuales individuales, apuntes y español claro inspirado
en ASD-STE100; no se promete una presentación editable.

## Mapa docente

Tres skills separadas permiten crear o mantener el mapa, consultarlo sin cambios
y visualizarlo. Crear o actualizar el mapa escribe también en el `AGENTS.md` de
la raíz del proyecto docente la ruta a su índice y la regla común de consulta:
índice → enlaces pertinentes → originales cuando sean necesarios. El agente
reúne la evidencia del encargo sin volver a recorrer toda la documentación.
Esta integración conserva las reglas previas y no exige ejecutar antes la skill
de puesta en marcha. Si no se conoce la raíz del proyecto, se solicita.

El profesor elige explícitamente una o varias carpetas de origen y sus
exclusiones. El mapa reutiliza la selección guardada; no descubre fuentes ni
amplía el corpus por seguir enlaces. Resultados, borradores y el propio mapa
quedan excluidos. Las páginas dependientes de fuentes retiradas requieren revisión. Los originales
no se mueven, editan ni copian salvo petición expresa de copia.

En un curso inicializado, el mapa reside en `docente/mapa-docente/`. Un mapa
previo conserva su ubicación hasta una migración acordada. Dentro del mapa, `contenidos/` organiza
conceptos, presentaciones, apuntes, prácticas y talleres; `reservado/` separa
evaluaciones, soluciones y criterios que no deben trasladarse al alumnado.
La organización interna se adapta al contenido. El tipo de material y su acceso son clasificaciones
independientes.

Las páginas usan enlaces Markdown normales, sin dependencia de Notion, Obsidian
o frontmatter obligatorio. `fuentes.json`, versión 2, registra varias raíces
en `source_roots`, las fuentes y las páginas en `pages`. Las rutas son relativas
al mapa y a cada raíz. Si no se puede representar una ubicación con rutas
relativas, como entre unidades distintas en Windows, se comunica la limitación;
no se trasladan ni copian archivos automáticamente.

Crear o actualizar el mapa incluye regenerar el lector `index.html` y el grafo
tras validar las páginas y su correspondencia con el corpus vigente.
El lector abre el índice Markdown renderizado y permite navegar entre páginas,
buscar y consultar por separado los contenidos reservados. Ambos HTML funcionan
sin servidor. El grafo permite arrastrar, ampliar, buscar y filtrar nodos;
«Reorganizar» redistribuye solo los visibles, conservando filtros y selección.
Su panel ofrece documentos de la wiki renderizados, Markdown editables y originales;
los archivos originales deben seguir accesibles para abrirlos. Las evaluaciones aparecen diferenciadas y ocultas al
inicio mediante un filtro que no es un control de seguridad.

La vista opcional de estudiantes excluye de los datos los nodos no autorizados y
los que dependen de ellos, incluso de forma transitiva; no ofrece enlaces salientes
a archivos ni distribuye los documentos. Compartir el HTML docente con filtros
activados no equivale a esa exportación. El mapa no aplica autenticación ni se
publica automáticamente.

## Adaptar a tu materia

Elige disciplina, nivel, idioma, objetivos, fuentes, actividad y criterios de
evaluación para cada proyecto. Se admiten formación escolar, universitaria,
profesional y otros contextos; no se impone una rúbrica, matrícula institucional
ni escala sobre diez. Los ejemplos son sintéticos y no se heredan como reglas.
La interfaz y las instrucciones están en español; los materiales respetan el
idioma del encargo. Para textos en español se aplica la skill de redacción clara.

Puedes comenzar con la [ficha vacía](templates/ficha-asignatura-vacia.md) o con un
encargo en la conversación. Moodle solo es necesario para sus flujos de
intercambio; el mapa, las actividades, los apuntes y las rúbricas pueden usarse
sin él. [Alcance y revisión de generalidad](docs/GENERALIDAD.md).

## Instalación

Sigue la [guía para profesores, administradores y usuarios avanzados](docs/INSTALACION.md).
El repositorio incluye los marketplaces de ambas plataformas. Primero se
incorpora ese origen de GitHub y después se instala el plugin en la cuenta.
No basta con copiar una skill aislada: comparte referencias y utilidades con
el resto del paquete. La instalación depende de las capacidades de la cuenta.

La [release 0.8.0](https://github.com/cjescudero/asistente-docente/releases/tag/v0.8.0) ofrece:

- `asistente-docente-0.8.0-agent-plugins.zip`: Agent Plugins y adaptador Codex.
- `asistente-docente-0.8.0-claude.zip`: plugin para Claude.
- `asistente-docente-0.8.0-source.zip`: fuente con catálogos y automatización GitHub.

## Utilidades para agentes y desarrollo

Se necesita **Python 3.10 o posterior** para las utilidades. No hay claves API ni
servidores que configurar. El agente puede preparar carpetas e instrucciones mediante herramientas de
archivos sin Python. Los comandos siguientes documentan las utilidades; no son
un requisito para pedir la puesta en marcha en lenguaje natural.

macOS/Linux, desde la carpeta del plugin:

```sh
python3 scripts/setup_environment.py
```

Windows PowerShell:

```powershell
py -3 scripts/setup_environment.py
```

La preparación normal usa la caché del usuario, fuera del plugin y del curso;
el instalador muestra la ruta del intérprete y cómo ejecutar el diagnóstico.
`--dev` conserva `.venv` para desarrollo. `doctor --project RUTA_CURSO` añade la
comprobación del proyecto; `doctor` sin esa opción mantiene el diagnóstico de
capacidades. Distingue `basic_ready` y `pdf_ready`; usa `doctor --pdf` para exigir
las capacidades PDF. Un PDF concreto requiere comprobar su generación.

La instalación básica prepara Markdown y el lector de la wiki. Añade `--pdf`
para instalar Playwright y Chromium; `--dev` prepara validaciones y pruebas.
`--venv` permite preparar un entorno fuera del curso y de una instalación
de solo lectura; reutilizar el entorno del anfitrión cuando ya sea suficiente.
`--dry-run` muestra las operaciones. `sh install.sh` conserva el acceso rápido
en macOS/Linux y acepta las mismas opciones.

Si el anfitrión ya tiene Python y las dependencias, puede usarlos directamente.
Los bancos GIFT, el feedback, la validación del mapa y el grafo usan Python
estándar. Para PDF se puede indicar un navegador ya disponible mediante
`ASISTENTE_DOCENTE_CHROMIUM`; si no funciona, se conserva el HTML y se declara
el PDF pendiente. La generación de imágenes requiere esa capacidad del anfitrión.

## Ejemplo completo sin datos reales

Los comandos siguientes son ejemplos para agentes y desarrollo. Usan `.venv`
preparado con `--dev`; con la instalación normal, sustituir el intérprete por la
ruta indicada por el instalador. Guarda resultados **fuera del plugin**, por
ejemplo en una carpeta hermana llamada `demo-docente`:

```sh
.venv/bin/python scripts/docencia.py validate-bank examples/humanidades/banco.gift
.venv/bin/python scripts/docencia.py build-exams examples/humanidades/banco.gift --metadata examples/humanidades/metadatos.json --output ../demo-docente/examen --title "Fuentes e interpretación histórica" --models 2 --questions 4 --seed 42
.venv/bin/python scripts/docencia.py build-feedback ../demo-docente/examen/manifest.json --input examples/resultados-sinteticos.csv --config examples/feedback-config.json --output ../demo-docente/feedback
.venv/bin/python scripts/docencia.py render-markdown examples/apuntes.md --output ../demo-docente/apuntes
.venv/bin/python scripts/validate_library.py examples/mapa-docente/mapa-docente
```

El [ejemplo de Mapa docente](examples/mapa-docente/README.md) contiene siete
fuentes sintéticas en dos carpetas: cinco revisadas completas, una parcial y una
pendiente. Su [índice](examples/mapa-docente/mapa-docente/index.md) enlaza las
páginas, el [lector HTML](examples/mapa-docente/mapa-docente/index.html) y los grafos
`grafo-docente.html` y `grafo-estudiante.html`. Para mantener
un mapa propio, trabajar en la carpeta del curso y generar allí el HTML con
`scripts/build_graph.py`; véase [uso](docs/USO.md).

También hay un [banco de ciencias](examples/ciencias/banco.gift) con
[metadatos](examples/ciencias/metadatos.json). Todos los ejemplos son sintéticos.
La carpeta [demostración](examples/demostracion) incluye los nueve PDF revisados,
HTML, GIFT, manifiestos, snapshots y comentarios producidos en la validación.
Es material de referencia; genera los resultados de cada curso fuera del plugin.
El emparejamiento de humanidades queda expresamente excluido de los modelos;
la CLI comunica los identificadores excluidos.

`--html-only` permite generar y comprobar el modelo sin navegador. Si se pide
PDF y falla, los HTML y el manifiesto se conservan y la CLI devuelve código 2;
no declara éxito de PDF. Código 1 significa entrada o procesamiento inválidos.
No se sobrescriben resultados de exámenes ni comentarios existentes.

## Formatos y límites

- GIFT: opción única, múltiple, verdadero/falso, numérica y emparejamiento.
  Examen impreso: los primeros cuatro tipos. Se exige título/ID único.
- Se rechazan respuesta corta, ensayo, Cloze, preguntas sin ID, texto después
  del bloque de respuestas, formatos por opción y sintaxis ambigua. No es un
  importador universal de todas las variantes Moodle.
- HTML: texto, listas, tablas y formato básico; `rowspan`/`colspan` conservados.
  El formato GIFT `moodle` conserva HTML básico y saltos de línea; no reproduce
  todos los filtros, autoenlaces y extensiones de un curso Moodle.
  HTML activo, SVG, MathML e imágenes incrustadas en enunciados requieren una
  adaptación explícita y se rechazan, sin perder contenido silenciosamente.
- Matemáticas: `\(...\)` y `\[...\]`, con MathJax 3.2.2 local (base, ams y
  newcommand). Sin carga remota de extensiones. Escapar símbolos GIFT en el banco.
- Feedback: exportaciones UTF-8/UTF-8 BOM y separador coma, punto y coma o tabulador.
  Las columnas y los máximos son explícitos; no se presume escala sobre diez.
- Notebooks y Word se preparan con capacidades disponibles del anfitrión; no
  hay un corrector universal de código ni conversión a Word en esta CLI.
- Mapa docente: el agente lee y sintetiza fuentes con las capacidades disponibles.
  El validador comprueba inventario, rutas, enlaces y huellas; no ingiere PDF,
  ejecuta notebooks ni certifica la corrección semántica de una síntesis.
  El grafo deriva relaciones de enlaces Markdown reales, no de proximidad visual.
  Se pueden validar registros anteriores de versión 1; su actualización se hace
  en una copia del mapa y el grafo requiere versión 2.

[Contratos técnicos](docs/CONTRATOS.md) · [Guía Moodle](docs/MOODLE.md)

## Desarrollo y distribución

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/sync_manifests.py --check
.venv/bin/python scripts/validate_plugin.py --public
.venv/bin/python scripts/build_release.py --source
```

Las pruebas PDF son optativas en la suite: establecer `RUN_PDF_TESTS=1` cuando
Chromium esté disponible. El pipeline incluido para GitHub comprueba el código
y construye paquetes como artefactos; no publica releases ni notas de alumnos.
Los ZIP excluyen entornos, cachés y datos operativos. `SHA256SUMS` permite
comprobar su integridad; `contents.json` registra el contenido común.

La versión 0.8.0 se distribuye desde GitHub con su fuente y paquetes. Las
versiones anteriores se conservan. La subida del código
no demuestra una instalación real en cada anfitrión.
La distribución se mantiene en los marketplaces de GitHub; no se solicita
publicación en los directorios públicos de OpenAI ni de Anthropic.
El contenido propio está bajo MIT por decisión del propietario. MathJax y el
esquema Agent Plugins conservan sus avisos Apache-2.0. Consulta cómo
[contribuir](CONTRIBUTING.md) y [preparar la publicación en GitHub](docs/PUBLICACION-GITHUB.md).
Los paquetes se distribuyen en las [versiones publicadas](https://github.com/cjescudero/asistente-docente/releases).

[Procedencia](docs/PROCEDENCIA.md) · [Avisos](NOTICE.md) ·
[Validación realizada](docs/VALIDACION.md)
