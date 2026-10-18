# Uso de Asistente docente

El plugin reúne doce skills que comparten criterios de claridad y trazabilidad. Se puede pedir directamente el resultado en lenguaje natural. La ficha del curso ayuda cuando hay decisiones docentes relevantes; no es un trámite obligatorio para cada petición.

| Necesidad | Skill |
| --- | --- |
| Preparar las instrucciones generales de un proyecto docente | [Iniciar proyecto docente](../skills/skill-iniciar-proyecto-docente/SKILL.md) |
| Organizar carpetas elegidas y establecer el mapa como entrada del proyecto | [Crear Mapa docente](../skills/skill-crear-mapa-docente/SKILL.md) |
| Localizar evidencia en el mapa sin modificarlo | [Consultar Mapa docente](../skills/skill-consultar-mapa-docente/SKILL.md) |
| Generar o regenerar el lector HTML de la wiki y su grafo | [Visualizar Mapa docente](../skills/skill-visualizar-mapa-docente/SKILL.md) |
| Enunciados, talleres y guía del profesor | [Preparar actividades](../skills/skill-preparar-actividades-docentes/SKILL.md) |
| Teoría y materiales de estudio | [Generar apuntes](../skills/skill-generar-apuntes-estudio/SKILL.md) |
| Trabajos entregados y rúbricas | [Evaluar entregas](../skills/skill-evaluar-entregas/SKILL.md) |
| Preguntas y metadatos conceptuales | [Crear bancos](../skills/skill-crear-bancos-preguntas/SKILL.md) |
| Papel y respuestas ofuscadas en Moodle | [Preparar exámenes](../skills/skill-preparar-examenes-papel-moodle/SKILL.md) |
| Resultados y comentarios de mejora | [Generar feedback](../skills/skill-generar-feedback-evaluaciones/SKILL.md) |
| Claridad, precisión y formato explicativo | [Redactar español claro](../skills/skill-redactar-espanol-claro/SKILL.md) |
| Imágenes con estilo de boceto didáctico | [Crear infografías](../skills/skill-crear-infografias-didacticas/SKILL.md) |

## Iniciar el proyecto docente

Pedir «Prepara este proyecto para trabajar con material docente» activa
`skill-iniciar-proyecto-docente`. La skill actúa en la raíz del proyecto elegido,
no en el `AGENTS.md` global ni en el del plugin. Si ya hay instrucciones, las
lee y conserva; modifica únicamente los puntos indicados, sin reorganizar el
resto. Ante conflictos muestra las reglas incompatibles y pregunta antes de
cambiar esa parte.
Repetir la puesta en marcha no debe duplicar esa sección.

La puesta en marcha prepara instrucciones generales del trabajo docente. No
crea ni invoca el Mapa docente ni pregunta si se quiere crearlo. Sí solicita
la ubicación y el tipo de los contenidos de origen cuando falten: teoría,
prácticas, talleres, exámenes, soluciones u otros. Reutiliza lo ya conocido y
registra ese contexto sin inventariar ni recorrer todos los materiales.
Incorpora en AGENTS.md el uso predeterminado de `skill-redactar-espanol-claro`
para redactar en español, salvo indicación distinta del encargo; si contradice
una regla previa, pregunta antes de cambiarla.
Si ya hay un bloque de consulta de un mapa, lo conserva;
no es un requisito haber creado un mapa para iniciar el proyecto.

El archivo es texto portable; su carga automática depende del anfitrión. Si el
agente no lo lee automáticamente, hay que incorporarlo como instrucciones del
proyecto o pedirle que lo lea al comenzar. La skill no crea un `CLAUDE.md` ni
modifica configuraciones globales como efecto secundario.

## Trabajar con un curso

Usar la [ficha Markdown](../templates/ficha-asignatura.md) o su [ejemplo JSON](../templates/ficha-asignatura.json) como contexto. Registrar objetivos, audiencia, fuentes vigentes, criterios y recursos permitidos. No imponer la estructura de una asignatura anterior ni usar exámenes reservados como fuente de apuntes sin autorización.

Guardar materiales y resultados fuera del paquete instalado. Mantener fuentes y derivados diferenciados: por ejemplo, `materiales`, `bancos`, `examenes` y `resultados` en el espacio del curso. Los nombres son orientativos; no se exige esa estructura.

Para materiales escritos, entregar Markdown y PDF por defecto. El Mapa docente usa Markdown navegable, registro JSON, lector `index.html` y grafo HTML; el PDF solo se añade si se pide una copia estática. Un notebook es opcional. Una petición de imagen o vídeo conserva su formato: ni un prompt ni un guion cuentan como archivo final generado. Las infografías requieren una capacidad de imágenes disponible; si falta, esa skill entrega brief y prompt, sin cambiar por defecto a SVG. El grafo del mapa se construye a partir de datos y enlaces, sin generación de imágenes.

## Crear y consultar el Mapa docente

Pedir «Crea un Mapa docente con estas dos carpetas, separando el curso actual de
los exámenes anteriores» activa la creación. El profesor debe elegir las carpetas:
puede haber una o varias, pero ninguna se presupone o descubre automáticamente.
La selección ya indicada se reutiliza; no hay que confirmarla en cada consulta.
No hace falta ejecutar previamente la skill de puesta en marcha.

Al crear o actualizar el mapa, la propia skill integra en el `AGENTS.md` de la
raíz del proyecto docente el bloque de consulta, siguiendo su
[plantilla](../skills/skill-crear-mapa-docente/assets/agents-mapa.md). Si esa raíz
no está identificada, la solicita; no la deduce buscando carpetas ascendentes.
Conserva las instrucciones previas y actualiza el bloque del mapa una sola vez,
incluido el que pudiera existir desde la versión 0.5.0. Las rutas al índice y a
los orígenes se resuelven desde el `AGENTS.md`, no desde la instalación del plugin.

El bloque establece la ruta común para los encargos docentes y skills: índice
de la wiki → páginas relevantes → enlaces pertinentes → originales cuando sean
necesarios. El agente sigue solo las ramas que aportan evidencia, resuelve cada
enlace desde su página y evita ciclos. Se detiene cuando tiene evidencia
suficiente o identifica una laguna; no vuelve a leer todo el corpus. Respeta
curso, vigencia, lectura y acceso, y verifica originales para citas,
calificaciones, preguntas evaluables o dudas. Puede reutilizar el conocimiento
ya revisado y vigente durante la misma tarea.

Una consulta o generación de material no modifica por sí sola la wiki. La
incorporación de nuevas fuentes, decisiones o resultados corresponde a un
encargo de mantenimiento. El bloque tampoco convierte la wiki en autoridad
superior a las fuentes ni a las instrucciones del profesor.

El resultado incluye índice, fichas, conceptos, referencias precisas, estados de
lectura y lagunas explícitas. Las páginas son Markdown estándar con enlaces
normales; no requieren Notion, Obsidian ni frontmatter. Crear o mantener el mapa
incluye generar su lector `index.html` y su grafo mediante la skill de visualización
cuando están las capacidades necesarias. También puede pedirse regenerar solo uno.

Una estructura posible es `materiales-docentes/`, `archivo-evaluaciones/` y
`mapa-docente/`, con `index.md`, `LEEME.md`, `fuentes.json`, `incidencias.md` y
`log.md`. Bajo `contenidos/` se pueden separar conceptos, presentaciones, apuntes,
prácticas y talleres; bajo `reservado/`, evaluaciones, soluciones y criterios
reservados. Estas rutas son ejemplos, nunca carpetas fijas. El acceso de una
página y su tipo se registran por separado.

Los originales se conservan en sus carpetas. No se mueven ni copian para crear
el mapa; una copia requiere que se haya pedido. `fuentes.json` usa
`schema_version: 2`: `source_roots` recoge las raíces con rutas relativas al mapa,
cada fuente indica la raíz a la que pertenece y `pages` registra las páginas y
sus fuentes. Si las ubicaciones no permiten rutas relativas —por ejemplo,
unidades distintas de Windows—, comunicar la limitación y acordar un destino
compatible; no copiar archivos como solución automática.

Después se puede pedir «¿Qué fuentes sustentan una nueva práctica sobre este
tema?» o «Localiza los criterios vigentes para evaluar este trabajo». La consulta
prepara evidencia para la skill de actividades, bancos o evaluación. No toma los
pesos de un examen antiguo como rúbrica actual ni sustituye las fuentes por el
resumen. Consultar no cambia páginas ni regenera el grafo. Véanse el [flujo y contrato](MAPA-DOCENTE.md), las
[plantillas](../templates/mapa-docente) y el
[índice del ejemplo](../examples/mapa-docente/mapa-docente/index.md). El ejemplo
tiene dos raíces y siete fuentes sintéticas: cinco completas, una parcial y una
pendiente. No genera apuntes del estudiante automáticamente.

Los registros anteriores de versión 1 siguen siendo validables. Si se pide
actualizarlos, la migración a versión 2 se prepara en una copia del mapa,
conservando la versión anterior y los originales; la consulta no migra nada.

## Ejecutar las utilidades

La CLI funciona mediante la ruta del script y no requiere instalar el módulo `docencia` como paquete. Requiere Python 3.10 o posterior. El PDF utiliza las dependencias declaradas en el plugin y Chromium de Playwright; su disponibilidad debe comprobarse en el entorno real.

Los ejemplos siguientes se ejecutan desde la carpeta del curso. `ASISTENTE_DOCENTE` debe contener la ruta absoluta de la raíz instalada del plugin, localizada por el anfitrión. No es una ruta personal fija ni una variable que deba añadirse a la configuración global. Para guardarla desde una terminal situada en esa raíz:

```sh
export ASISTENTE_DOCENTE="$PWD"
```

Después, trabajar en la carpeta del curso. Usar el intérprete Python del entorno que tenga las dependencias y pasar el script por su ruta absoluta:

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" doctor
python "$ASISTENTE_DOCENTE/scripts/docencia.py" --help
```

`doctor` comprueba las capacidades básicas; `doctor --pdf` exige además las de PDF. El diagnóstico no instala dependencias ni demuestra que un PDF concreto haya renderizado correctamente. Consultar la ayuda de cada comando para sus argumentos.

### Wiki navegable y grafo HTML

Desde la carpeta del curso, con un mapa ya preparado:

```sh
python "$ASISTENTE_DOCENTE/scripts/validate_library.py" mapa-docente
python "$ASISTENTE_DOCENTE/scripts/build_graph.py" mapa-docente \
  --output mapa-docente/grafo-docente.html --wiki-output mapa-docente/index.html --audience docente
```

El grafo usa enlaces Markdown existentes; no inventa relaciones a partir de
proximidad o de títulos parecidos. `source_ids` registra procedencia y permite
comprobar dependencias de acceso. El HTML incorpora la visualización y sus datos,
sin llamadas de red: ofrece arrastre, zoom, búsqueda, filtros y panel. En modo
docente conserva enlaces relativos a páginas y originales, que solo se abrirán
si esos archivos siguen disponibles. Las evaluaciones están diferenciadas y
ocultas inicialmente mediante un filtro; sus datos siguen presentes en esa copia.

Abrir `index.html` para leer la wiki desde su índice, seguir enlaces entre páginas,
buscar documentos y volver con el navegador. El panel del grafo enlaza los
documentos relacionados, tanto renderizados como en Markdown. El lector mantiene
los materiales reservados en una sección diferenciada y es de uso docente.
«Reorganizar» redistribuye solo los nodos visibles sin perder filtros ni selección;
«Ajustar» encuadra las posiciones actuales. Para regenerar solo el lector:

```sh
python "$ASISTENTE_DOCENTE/scripts/build_wiki.py" mapa-docente --graph mapa-docente/grafo-docente.html
```

Para una exportación expresamente destinada a estudiantes:

```sh
python "$ASISTENTE_DOCENTE/scripts/build_graph.py" mapa-docente \
  --output mapa-docente/grafo-estudiante.html --audience estudiante
```

Esta salida elimina de los datos los nodos no autorizados y los que dependen de
ellos, también a través de otras páginas. No contiene enlaces salientes a archivos
ni distribuye los documentos. Un filtro del HTML docente no produce el mismo
resultado. Revisar interfaz y datos incrustados antes de entregar cualquier copia.

Los Markdown y HTML no aplican autenticación ni permisos. No se publica nada al
generarlos. Sin Python, conservar el mapa Markdown y declarar la generación del
lector y grafo pendiente. El lector requiere `markdown-it-py`; si falta, comunicarlo
y conservar las fuentes. La validación de rutas, enlaces y huellas no certifica que se haya
leído o comprendido todo el material.

### Banco y modelos

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" validate-bank banco.gift
python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-exams banco.gift \
  --metadata metadatos.json --output examen \
  --title "Evaluación de fuentes" --models 2 --questions 5 --seed 42
```

`--metadata` es opcional. Los metadatos vinculan los identificadores de preguntas con conceptos y orientaciones para el feedback; siguen el [contrato](CONTRATOS.md). No usar la ficha de asignatura como metadatos.

Para cuotas por categoría, añadir `--per-category cuotas.json`, cuyo contenido es un objeto de nombre exacto de categoría a cantidad. Su suma debe coincidir con `--questions`. Por ejemplo, `{"Fuentes": 3, "Argumentación": 2}` solo sirve para un banco con esas categorías exactas.

La salida debe ser una carpeta nueva o vacía. Incluye `manifest.json`, el snapshot del banco y archivos separados por modelo: HTML/PDF de estudiante, HTML/PDF docente y GIFT ofuscado. Los identificadores y rutas concretas están en el manifiesto. Guardar todo el conjunto; no conservar únicamente los PDF.

El banco puede contener emparejamiento, pero este tipo queda fuera del flujo ofuscado de v1. Revisar la lista de identificadores excluidos y confirmar que la selección sigue cumpliendo el objetivo. No interpretar una exclusión como pregunta aplicada.

`--html-only` conserva una salida HTML sin intentar PDF. Si se intentó PDF y falta una capacidad o falla una fórmula, revisar `pdf_status`: el HTML conservado no sustituye el PDF pendiente. El estado de error debe resolverse antes de imprimir un examen.

### Material escrito y fórmulas

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" render-markdown apuntes.md \
  --output apuntes-renderizados --title "Métodos de investigación"
```

En Markdown, usar su sintaxis de formato y delimitadores matemáticos; las etiquetas HTML se muestran como texto literal. En bancos GIFT `[html]`, usar HTML simple para formato habitual y subíndices/superíndices cuando basten. Para matemáticas, se admiten `\(...\)` en línea y `\[...\]` en bloque; no se usan delimitadores `$`, que pueden representar moneda. El renderizado usa MathJax local, sin descargar recursos remotos, con los paquetes `base`, `ams` y `newcommand`. No admite carga dinámica de extensiones.

En GIFT, escapar además los caracteres especiales del formato antes de guardar la fórmula; el parser los decodifica antes del renderizado. Una fórmula no soportada que genere error bloquea el PDF y conserva el HTML para diagnóstico. La compatibilidad matemática de Moodle depende de los filtros del curso y debe probarse allí por separado.

### Feedback de resultados

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-feedback examen/manifest.json \
  --input resultados.csv --config feedback.json --output comentarios
```

Repetir `--input` para varios CSV. La configuración debe mapear columnas reales, identificadores, modelo, estado, máximos y valores declarados de ausencia o blanco; véase [Moodle](MOODLE.md). Los mapas pueden variar por modelo. No suponer que todos los CSV usan el mismo separador o escala.

Se generan CSV por modelo cuando no hay incidencias bloqueantes. `--consolidated` añade consolidado si se solicita. `--detailed` pide feedback más detallado y requiere datos suficientes; el modo normal es conceptual. Las notas originales y las columnas ajenas al comentario se conservan. La herramienta no corrige trabajos abiertos ni reevalúa notas de Moodle.

## Verificar y entregar

Comprobar el estado devuelto y el informe de incidencias, abrir los archivos finales y contrastar una muestra con las fuentes. Para exámenes, revisar todos los modelos y la correspondencia de numeración y opciones con el manifiesto. Para feedback, revisar casos de acierto, fallo, crédito parcial, blanco y ausencia.

Las comprobaciones locales de formato y PDF no acreditan instalación real en ChatGPT Work o Claude Cowork, ni importación real en Moodle. Registrar esas pruebas por separado y no anunciar una operación externa que no se haya realizado. La instalación del plugin no publica materiales ni importa calificaciones.
