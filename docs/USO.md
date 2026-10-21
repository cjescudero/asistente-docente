# Uso de Asistente docente

El plugin reúne doce skills que comparten criterios de claridad y trazabilidad.
Se puede pedir directamente el resultado en lenguaje natural, sin conocer sus
nombres. Para descubrir el siguiente paso, pregunta **«¿Qué puedo hacer ahora
con mi asignatura?»**. La ficha del curso ayuda cuando hay decisiones docentes
relevantes; no es un trámite obligatorio para cada petición.

| Necesidad | Skill |
| --- | --- |
| Preparar el curso, elegir fuentes y conciliar sus instrucciones | [Proyecto docente: inicialización y adaptación](../skills/proyecto-docente-inicializacion-adaptacion/SKILL.md) |
| Conocer opciones y entradas necesarias según el estado del curso | [Proyecto docente: ayuda](../skills/proyecto-docente-ayuda/SKILL.md) |
| Organizar carpetas elegidas y establecer el mapa como entrada del proyecto | [Mapa docente: creación y visualización](../skills/mapa-docente-creacion-visualizacion/SKILL.md) |
| Localizar evidencia en el mapa sin modificarlo | [Mapa docente: consulta](../skills/mapa-docente-consulta/SKILL.md) |
| Generar o regenerar el lector HTML de la wiki y su grafo | [Mapa docente: creación y visualización](../skills/mapa-docente-creacion-visualizacion/SKILL.md) |
| Diseñar por diálogo enunciados, plantillas y rúbrica docente | [Actividades: preparación](../skills/actividades-preparacion/SKILL.md) |
| Teoría y materiales de estudio | [Apuntes estudio: creación](../skills/apuntes-estudio-creacion/SKILL.md) |
| Corregir trabajos y preparar notas y feedback para Moodle | [Actividades: evaluación](../skills/actividades-evaluacion/SKILL.md) |
| Bancos asociados a materiales y actividades | [Bancos de preguntas: creación](../skills/bancos-preguntas-creacion/SKILL.md) |
| Combinar bancos en modelos impresos y respuestas ofuscadas | [Evaluaciones: preparación modelos a partir de bancos de preguntas](../skills/evaluaciones-preparacion-modelos/SKILL.md) |
| Resultados y comentarios de mejora | [Evaluaciones: observaciones para el alumnado](../skills/evaluaciones-observaciones-alumnado/SKILL.md) |
| Claridad, precisión y formato explicativo | [Español conciso: redacción](../skills/espanol-conciso-redaccion/SKILL.md) |
| Imágenes con estilo de boceto didáctico | [Infografías didácticas: creación](../skills/infografias-didacticas-creacion/SKILL.md) |

## Iniciar el proyecto docente

Instala el plugin, abre la carpeta del curso y pide **«Inicia mi proyecto docente»**.
El agente aclara solo los datos que faltan, prepara el árbol uniforme y guarda
`proyecto-docente.json`, `LEEME.md` y `AGENTS.md`. El contrato de estructura,
selección y herramientas está en [Proyecto docente](PROYECTO-DOCENTE.md).

Si ya existen materiales, el agente presenta movimientos y enlaces afectados
antes de reorganizarlos. No sobrescribe archivos ni instrucciones. Modifica
solo lo autorizado en `AGENTS.md` y pregunta ante conflictos. Repetir la puesta
en marcha no duplica reglas ni borra un mapa o una selección previos.

El profesor elige las carpetas y exclusiones del corpus, o aplaza esa selección.
La inicialización deja la carpeta del mapa vacía cuando no existe, recomienda
crearlo y ofrece orientación para continuar. Su creación requiere un encargo del
profesor. Establece `espanol-conciso-redaccion` para escribir en español y conserva
un bloque de consulta de mapa existente.

Comprobar que el anfitrión incorpora `AGENTS.md`. Si no, pedir su lectura
explícita o utilizar las instrucciones de carpeta disponibles. No se crea
`CLAUDE.md` ni se cambian configuraciones globales por sistema.

## Descubrir qué hacer a continuación

La orientación consulta las instrucciones, la configuración y los índices
disponibles. Presenta opciones adecuadas al estado del curso con ejemplos y
archivos necesarios:

| Situación | Ejemplo de petición |
| --- | --- |
| Materiales elegidos, sin mapa | «Crea el mapa docente de las fuentes seleccionadas». |
| Mapa disponible | «Localiza los materiales sobre este tema» o «Muéstrame el mapa». |
| Materiales para diseñar una actividad | «Ayúdame a preparar un taller sobre estas fuentes y su rúbrica». |
| Materiales o actividad ya definidos | «Crea un banco de preguntas asociado a estos apuntes y a esta actividad». |
| Bancos disponibles | «Prepara tres modelos de evaluación de estos temas y prácticas». |
| Entregas descargadas de Moodle | «Corrige este lote con su enunciado y rúbrica y prepara las calificaciones». |
| Examen ya puntuado | «Añade recomendaciones de mejora a partir del detalle de respuestas y las notas». |

Preguntar qué se puede hacer no inicia esos procesos ni lee todo el corpus.
Si falta una entrada, el agente la identifica. Se puede realizar una tarea con
adjuntos suficientes aunque el curso todavía no tenga mapa.

Como apoyo se ofrecen apuntes para estudiantes, español claro inspirado en
ASD-STE100 e infografías o diapositivas visuales individuales. La skill de
infografías conserva ese alcance; no promete presentaciones editables.

## Trabajar con un curso

Usar la [ficha Markdown](../templates/ficha-asignatura.md) o su [ejemplo JSON](../templates/ficha-asignatura.json) como contexto. Registrar objetivos, audiencia, fuentes vigentes, criterios y recursos permitidos. No imponer la estructura de una asignatura anterior ni usar exámenes reservados como fuente de apuntes sin autorización.

Guardar materiales y resultados fuera del paquete instalado. Los cursos nuevos
usan `curso-v2`: originales en `fuentes/`, trabajos nuevos por tipo en `creados/`,
wiki en `mapa-docente/` y lotes en `resultados/<actividad>/<convocatoria>/`, con
`recibidos/` y `correccion/` separados. Las actividades y exámenes reúnen sus
documentos de alumnado y docente en subcarpetas. Los estados se registran sin
mover ni duplicar los archivos. Los cursos `curso-v1` conservan sus rutas hasta
una [migración acordada](MIGRACION-0.9.md).

Al terminar una skill, ofrecer próximos pasos según los resultados existentes,
sin ejecutar otras tareas ni asumir que una carpeta acredita su finalización.
Seguir los [flujos docentes](FLUJOS-DOCENTES.md) y usar español claro por defecto,
salvo indicación distinta. Una tarea con adjuntos suficientes no exige preparar
todo el curso ni crear un mapa.

Para materiales escritos, entregar Markdown y PDF por defecto. El Mapa docente usa Markdown navegable, registro JSON, lector `index.html` y grafo HTML; el PDF solo se añade si se pide una copia estática. Un notebook es opcional. Una petición de imagen o vídeo conserva su formato: ni un prompt ni un guion cuentan como archivo final generado. Las infografías requieren una capacidad de imágenes disponible; si falta, esa skill entrega brief y prompt, sin cambiar por defecto a SVG. El grafo del mapa se construye a partir de datos y enlaces, sin generación de imágenes.

## Actividades, bancos y evaluación

Para diseñar una actividad, el agente aclara objetivos, materiales, ejemplos
anteriores, condiciones y entregables por etapas. Propone evidencias de
aprendizaje considerando el acceso del alumnado a modelos de IA y pregunta las
condiciones de uso que falten. Produce enunciado, plantillas adecuadas y rúbrica
docente, con una guía de corrección cuando corresponda. El enunciado comunica
criterios generales; la rúbrica completa permanece reservada. El registro
`actividad.json` relaciona las fuentes y archivos de esa versión. Véase
[Actividades](ACTIVIDADES.md).

Los bancos se vinculan a diapositivas, apuntes, ejercicios o actividades concretos.
Sus metadatos permiten combinar preguntas según contenido y dificultad. Los
exámenes antiguos pueden servir para calibrar estilo y nivel sin convertirlos
en temario vigente. La composición de modelos presenta antes un reparto y
declara insuficiencias; no inventa preguntas para rellenarlas. Véase
[Bancos y composición de modelos](BANCOS.md).

La corrección de entregas aplica enunciado, rúbrica y resolución disponibles.
Si faltan criterios suficientes, propone acordarlos antes de asignar notas
definitivas. Los trabajos y archivos Moodle se identifican por claves explícitas.
La utilidad prepara una copia de la hoja de tarea o del libro de calificaciones
con notas justificadas y feedback; conserva los casos pendientes y la trazabilidad
de cambios. Véase [Calificaciones de actividades](CALIFICACIONES.md).

El feedback de exámenes parte de puntuaciones por pregunta y del manifiesto.
Prioriza hasta tres dificultades y recomendaciones de mejora, conservando las
notas de Moodle. La nota global por sí sola no permite saber qué conceptos
fallaron. Ambos recorridos terminan en archivos revisables para importación manual.

## Crear y consultar el Mapa docente

Pedir «Crea un Mapa docente con estas dos carpetas, separando el curso actual de
los exámenes anteriores» activa la creación. El profesor debe elegir las carpetas:
puede haber una o varias, pero ninguna se presupone o descubre automáticamente.
La selección guardada y sus exclusiones se reutilizan; no hay que confirmarlas
en cada consulta. Una fuente retirada o excluida no puede reintroducirse por un
enlace ni por un registro antiguo. Sus páginas dependientes requieren revisión.
No hace falta ejecutar previamente la skill de puesta en marcha.

Al crear o actualizar el mapa, la propia skill integra en el `AGENTS.md` de la
raíz del proyecto docente el bloque de consulta, siguiendo su
[plantilla](../skills/mapa-docente-creacion-visualizacion/assets/agents-mapa.md). Si esa raíz
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
cuando están las capacidades necesarias y la validación del corpus y sus
dependencias pasa. También puede pedirse regenerar solo uno.

El mapa de un curso nuevo está en `mapa-docente/`, con `index.md`,
`LEEME.md`, `fuentes.json`, `incidencias.md` y `log.md`. Un mapa previo conserva
su ruta hasta una migración autorizada. Bajo `contenidos/` se separan conceptos,
presentaciones, apuntes, prácticas y talleres; bajo `reservado/`, evaluaciones,
soluciones y criterios reservados. El acceso y el tipo se registran por separado.

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

Este apartado es para agentes y mantenimiento. El profesor puede solicitar los
resultados en lenguaje natural. La preparación del curso y el diagnóstico con
`doctor --project` se describen en [Proyecto docente](PROYECTO-DOCENTE.md).

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

Para bancos asociados a varios materiales, validar el catálogo y componer con un
reparto acordado. El formato del catálogo y de la selección se detalla en
[Bancos](BANCOS.md):

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" validate-catalog \
  creados/bancos/catalogo.json --project .
python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-exams \
  --catalog creados/bancos/catalogo.json --selection reparto.json \
  --project . --output creados/examenes/parcial-01 --layout curso-v2 --title "Evaluación de fuentes" \
  --models 2 --questions 5 --seed 42
```

También se mantiene la entrada de un único banco:

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" validate-bank banco.gift
python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-exams banco.gift \
  --metadata metadatos.json --output creados/examenes/parcial-01 --layout curso-v2 \
  --title "Evaluación de fuentes" --models 2 --questions 5 --seed 42
```

`--metadata` es opcional para la entrada de un GIFT anterior. Los nuevos bancos
del catálogo requieren procedencia, objetivos, conceptos, dificultad y
orientaciones de repaso. Completar los datos que falten antes de prometer
equilibrio basado en ellos. No usar la ficha de asignatura como metadatos.

Para cuotas por categoría, añadir `--per-category cuotas.json`, cuyo contenido es un objeto de nombre exacto de categoría a cantidad. Su suma debe coincidir con `--questions`. Por ejemplo, `{"Fuentes": 3, "Argumentación": 2}` solo sirve para un banco con esas categorías exactas.

La salida debe ser una carpeta nueva o vacía. Incluye `manifest.json`, bancos
congelados y archivos separados por modelo: HTML/PDF de estudiante, HTML/PDF
docente y GIFT ofuscado. La composición por catálogo conserva la identidad de
banco y pregunta, y ofrece cobertura, dificultad y reutilización. Los
identificadores y rutas están en el manifiesto. Guardar el conjunto completo.

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
python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-feedback creados/examenes/parcial-01/docente/manifest.json \
  --input resultados/parcial-01/ordinaria/recibidos/resultados.csv \
  --config feedback.json --output resultados/parcial-01/ordinaria/correccion/feedback
```

Para exámenes anteriores con salida plana, usar su `manifest.json` en la raíz
del examen, sin moverlo ni regenerar sus snapshots. Repetir `--input` para varios CSV. La configuración debe mapear columnas reales, identificadores, modelo, estado, máximos y valores declarados de ausencia o blanco; véase [Moodle](MOODLE.md). Los mapas pueden variar por modelo. No suponer que todos los CSV usan el mismo separador o escala.

Para añadir comentarios a una copia del libro de calificaciones, aportar esa
exportación vigente mediante `--gradebook calificaciones.csv` y declarar las
columnas y correspondencias necesarias en el perfil. El detalle por pregunta
sigue siendo obligatorio; el libro no lo sustituye. Se preservan sus notas,
filas y columnas ajenas al feedback.

El objeto opcional `feedback_priority` configura `max_concepts` (3),
`marked_threshold` (0.5) y `min_evidence` (2). Con los valores predeterminados,
un concepto con menos del 50 % y al menos dos preguntas puede describirse como
dificultad acusada; un fallo aislado se presenta como aspecto a revisar.

Se generan CSV por modelo cuando no hay incidencias bloqueantes. `--consolidated` añade consolidado si se solicita. `--detailed` pide feedback más detallado y requiere datos suficientes; el modo normal es conceptual. Las notas originales y las columnas ajenas al comentario se conservan. La herramienta no corrige trabajos abiertos ni reevalúa notas de Moodle.

### Calificaciones de actividades

Una vez revisadas las entregas y preparada la evaluación estructurada, generar
la copia importable desde el archivo Moodle elegido:

```sh
python "$ASISTENTE_DOCENTE/scripts/docencia.py" export-grades evaluacion.json \
  --input calificaciones.csv --config perfil-moodle.json --output correccion
```

El [contrato de calificaciones](CALIFICACIONES.md) describe la evaluación, el
perfil de columnas y las correspondencias individuales o grupales. La utilidad
comprueba cálculos y exporta notas y comentarios; la valoración académica
corresponde al agente y al profesor. Revisar incidencias y cambios antes de
importar. Una hoja de tarea y un libro de calificaciones son vías diferentes:
comprobar el método configurado en Moodle conforme a [la guía](MOODLE.md).

## Verificar y entregar

Comprobar el estado devuelto y el informe de incidencias, abrir los archivos finales y contrastar una muestra con las fuentes. Para exámenes, revisar todos los modelos y la correspondencia de numeración y opciones con el manifiesto. Para feedback, revisar casos de acierto, fallo, crédito parcial, blanco y ausencia.

Las comprobaciones locales de formato y PDF no acreditan instalación real en ChatGPT Work o Claude Cowork, ni importación real en Moodle. Registrar esas pruebas por separado y no anunciar una operación externa que no se haya realizado. La instalación del plugin no publica materiales ni importa calificaciones.
