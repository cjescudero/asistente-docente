---
name: proyecto-docente-inicializacion-adaptacion
description: Inicializar o adaptar un proyecto docente, revisando primero sus contenidos y proponiendo su organización. Usar al iniciar un curso, reorganizar materiales o ajustar configuración e instrucciones existentes; preguntar por datos, destinos ambiguos y conflictos. Mover solo según una propuesta concreta aprobada. Recomendar el mapa sin crearlo automáticamente.
---

# Proyecto docente: inicialización y adaptación

Guiar al profesor ante «Inicia mi proyecto docente» o «Adapta mi curso existente»
hasta un proyecto preparado para trabajar. No exigir comandos ni una ficha completa. Esta skill prepara la
estructura y las instrucciones; no inicia otro flujo docente.

Usar por defecto [español conciso](../espanol-conciso-redaccion/SKILL.md) en la
conversación y los documentos, salvo que el profesor indique otro idioma o estilo.
Respetar citas, identificadores y términos que deban conservarse literalmente.

Ante dudas sobre el uso, flujo, archivos o resultados del plugin, o preguntas
sobre siguientes pasos y posibilidades, invocar
[Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) antes de responder.
Transferirle el objetivo, las decisiones conocidas y los resultados de esta tarea;
tras resolver la duda, retomar el encargo ya autorizado.

## Identificar contexto y fuentes

Leer el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md). Identificar
la raíz elegida por el profesor, sin confundirla con el plugin, su directorio
personal o un workspace con varios cursos. Si no está clara, pedirla antes de
escribir. Leer las instrucciones aplicables, `AGENTS.md` y la configuración que
ya exista.

Preguntar solo por lo que falte: contexto del curso, ubicación de materiales,
tipos de contenido y selección para la futura wiki. Admitir teoría, prácticas,
talleres, cuestionarios, soluciones y otros tipos, incluso mezclados en una carpeta.
Reutilizar decisiones explícitas; no recorrer toda la documentación para deducir
el temario. Identificar carpetas no equivale a haber leído sus documentos.

Solicitar las carpetas concretas que podrán alimentar el mapa y las exclusiones
de archivos o subcarpetas. No elegir toda la raíz ni una carpeta que mezcle datos personales y materiales. Excluir
siempre resultados, materiales en estado `borrador` y el propio mapa; incluir `archivo/` solo cuando
se indique expresamente. La selección no autoriza publicación ni lectura de
fuentes excluidas a través de enlaces. Si se aplaza, registrar el estado pendiente
sin inventar un corpus y completar las partes independientes. Distinguirlo de
la decisión expresa de trabajar sin fuentes, que guarda selección vacía. Usar
rutas dentro del curso; si los materiales están fuera, proponer otra raíz que
los contenga o una integración acordada, sin mover originales por defecto.

## Revisar antes de crear o adaptar

Antes de crear carpetas o ejecutar `init-project`, comprobar si la raíz está
vacía, contiene materiales mezclados o ya tiene instrucciones, configuración o
un mapa. Un error de acceso no significa que esté vacía. Inventariar solo los
archivos y carpetas pertinentes; omitir entornos, cachés, control de versiones
y componentes ajenos a los materiales docentes. No recorrer carpetas vecinas.

Usar nombres, rutas, extensiones y fechas como pistas, contrastándolos con el
contenido necesario para distinguir teoría, actividades, bancos, cuestionarios,
soluciones, rúbricas y resultados. No inferir destinatario, vigencia, procedencia
ni estado de palabras como «cuestionario», «final» o «2025». Indicar para cada conjunto
si la clasificación está **comprobada**, es **provisional** o queda **pendiente**,
y qué fragmentos se inspeccionaron. No declarar lectura completa por una muestra.
Un documento ilegible queda pendiente; no inventar su contenido o destino.

Cuando haya materiales, seguir la [organización guiada](../../docs/PROYECTO-DOCENTE.md#organizar-materiales-existentes):
mostrar una tabla con **origen, destino, contenido identificado, motivo y dudas
pendientes**, seguida del árbol resultante. Mantener juntos enunciado, plantillas,
rúbrica y solución, o modelos, manifiesto y bancos congelados; separar dentro del
conjunto lo estudiantil de lo reservado. No asignar todo lo existente a `fuentes/`,
lo reciente a `materiales_generados/` ni lo dudoso a `archivo/`. Preguntar por las ambigüedades
que afecten al destino antes de incluirlas entre los movimientos ejecutables.

Preguntar si el profesor quiere que el agente realice **los movimientos concretos
mostrados**. Ofrecer aceptar todos, seleccionar algunos, corregir destinos o
conservar la organización actual. Una petición general de iniciar o adaptar no
aprueba movimientos aún no presentados. Si se rechazan, conservar los materiales
y continuar con los ajustes compatibles solicitados; no crear una organización
paralela para forzar la propuesta. Organizar no selecciona el corpus de la wiki.

Antes de aplicar, comprobar colisiones, dependencias y enlaces; no sobrescribir
ni resolver nombres repetidos silenciosamente. Conservar un inventario de rutas
y huellas de los originales y conjuntos congelados para verificar integridad.
Aplicar solo lo aprobado y actualizar las rutas afectadas en configuración,
registros y enlaces. Preservar versiones, pesos, orden, identificadores,
correspondencias y bancos congelados de cuestionarios usados; revisar manualmente los
registros que la utilidad señale, sin reemplazos globales de texto. Si un cambio
necesario excede la propuesta aprobada, presentarlo antes de continuar esa parte.

Cuando se inventaríe un curso, guardar el inventario en
`_datos_internos_proyecto/inventario-inicial.json`, con rutas relativas,
clasificación y su grado de certeza; no convertir su ausencia en una prueba de
que el curso esté vacío. Una carpeta con material previo se organiza mediante
una propuesta concreta; no se presume que proceda de otra versión del plugin.

Tras los movimientos, comparar huellas de archivos trasladados sin edición,
revisar por separado las modificaciones de rutas acordadas y comprobar enlaces
y registros. Informar de movimientos realizados, elementos conservados y asuntos
pendientes. Repetir el inicio no vuelve a mover conjuntos ya organizados.

## Rutas de cuestionarios

Los cursos guardan cuestionarios aportados en
`fuentes/evaluaciones/cuestionarios/` y nuevos en `materiales_generados/cuestionarios/`.
Registrar ambas rutas en `questionnaire_paths` conforme al contrato. No crear
ramas paralelas al repetir el inicio.

## Preparar la estructura

Tras esa revisión y los acuerdos necesarios, crear el árbol `curso-v3` del contrato: `fuentes/` para
materiales aportados; `materiales_generados/` para materiales, actividades, bancos y cuestionarios
producidos; `mapa-docente/`, `resultados/` y `archivo/`. Guardar
`_datos_internos_proyecto/proyecto-docente.json` y un `LEEME.md` con la función de las carpetas y peticiones
de ejemplo. Dejar `mapa-docente/` vacía y `map: null` hasta que exista un índice.
Cada lote de resultados tendrá `resultados/<actividad>/<convocatoria>/recibidos/`
para descargas e identificación y `correccion/` para evaluación, notas y feedback.
Todo el lote queda fuera del corpus; crear esas subcarpetas cuando haya un lote.

Los materiales nuevos conservan su ubicación por tipo y un registro
`_datos_internos/material-docente.json` con `schema_version: 1`, `id`, `type` y `status`, además
del estado visible en `LEEME.md`. El estado cambia, la carpeta no. Mantener
`alumnado/` y `docente/` dentro de actividades y cuestionarios para separar destinatarios.
Un material creado que se use en otra tarea permanece donde está.

Si se pide reorganizar una carpeta con materiales, presentar una propuesta por
archivo, colisiones, dependencias y enlaces. Distinguir procedencia de los
archivos de su antigüedad; no clasificar automáticamente carpetas mezcladas.
Aplicar solo la propuesta aprobada, preservar instrucciones y no sobrescribir
ni duplicar materiales. Seleccionar contenidos creados para el mapa requiere
una decisión explícita y un registro válido en
estado `revisado` o `listo-para-entregar`; no marcar revisado para forzar su entrada.

Con Python disponible, usar el ayudante `scripts/docencia.py init-project` y su
modo `--dry-run` para revisar los cambios; `plan-migration` solo informa.
Resolver instalación y curso reales, sin escribir resultados en el plugin.
También se puede preparar el proyecto mediante las herramientas de archivos del
agente, manteniendo el mismo contrato. La ausencia de Python no bloquea la
creación de carpetas, instrucciones y configuración.

## Conciliar AGENTS.md

Crear `AGENTS.md` si falta. Si existe, respetar contenido y organización y cambiar
solo los puntos autorizados. El texto propuesto por un ayudante no sustituye el
archivo ni autoriza a reescribirlo. No normalizar ni reordenar reglas ajenas.

Ante cualquier conflicto, mostrar las reglas incompatibles y preguntar cuál debe
mantenerse o cómo conciliarlas. Conservar la parte en conflicto hasta recibir
respuesta; completar únicamente cambios independientes ya autorizados. Una
repetición de la puesta en marcha no duplica secciones ni borra decisiones.

Registrar contexto conocido, organización del curso y referencia a la
configuración, sin inventar asignatura, nivel, criterios o políticas. Mantener
los detalles pedagógicos extensos en la ficha opcional u otros documentos del
curso. Separar materiales estudiantiles y soluciones; evaluar con la rúbrica
vigente y evidencias, sin penalizar un supuesto uso de IA.

Incorporar una sola vez, respetando el procedimiento de conflictos:

> Para redactar o revisar textos del proyecto en español, usar por defecto
> `espanol-conciso-redaccion`, salvo indicación expresa distinta en el encargo.
> Conservar rigor, condiciones, cifras, terminología y citas; simplificar la
> expresión no autoriza a omitir información.

Es una preferencia local. No incrustar rutas personales ni cambiar la activación
global de [la skill de redacción](../espanol-conciso-redaccion/SKILL.md). Si no está
disponible, explicar la limitación y aplicar claridad y precisión sin afirmar
que se ha ejecutado.

Incorporar también la [política de trabajo paralelo y elección de modelos](../../docs/PROYECTO-DOCENTE.md#trabajo-paralelo-y-elección-de-modelos)
al `AGENTS.md`, tanto al usar la utilidad como al prepararlo con herramientas de
archivos. Usar subagentes para trabajo independiente cuando sea posible y útil;
el agente principal conserva criterios comunes, revisión e integración. Antes de
usar un modelo más sencillo, ofrecer una opción disponible y pedir elección
explícita para el lote o alcance, sin prometer ahorros no comprobados. Respetar
la elección vigente, la disponibilidad del anfitrión y los conflictos con reglas
previas. La inicialización escribe la política; no lanza tareas de evaluación.

Conservar el bloque de consulta de un mapa existente y sus enlaces. No añadir
una política de consulta a un índice inexistente. La carpeta prevista en la
estructura no acredita que el mapa esté creado; solo su creación o actualización
integra el índice real como punto de partida.

## Comprobar y cerrar

Usar `check-project` y `doctor --project` cuando haya Python, o realizar las
comprobaciones equivalentes con herramientas de archivos. Distinguir ubicaciones
inexistentes, vacías, sin archivos seleccionados y no accesibles. Explicar las
entradas pendientes sin ampliar fuentes ni bloquear tareas independientes.

Reutilizar el entorno disponible. Preparar dependencias solo cuando se necesiten,
fuera de los materiales del curso y de una instalación de solo lectura. PDF es
opcional; una falta de capacidad no equivale a un error en el curso.

Verificar raíz, estructura, configuración, preservación de instrucciones,
preferencia de redacción y fuentes conocidas o pendientes. Comprobar que el
anfitrión incorpora `AGENTS.md`; si no, pedir su lectura explícita o usar sus
instrucciones de carpeta. No crear `CLAUDE.md` por sistema ni modificar reglas
globales.

Entregar las rutas del proyecto y una explicación breve de qué está listo y qué
falta. Invocar la [ayuda contextual](../proyecto-docente-ayuda/SKILL.md) con ejemplos de
peticiones y recomendar crear el mapa con las fuentes elegidas como siguiente
paso; si ya existe, recomendar consultarlo. Si falta la selección, orientar
primero a elegir fuentes. Si el profesor decidió trabajar sin ellas, ofrecer
tareas con sus adjuntos sin insistir en crear el mapa. La recomendación no es un encargo:
no invocar su creación hasta que el profesor la pida. Si ya la ha solicitado,
tratarla como encargo separado de
[crear el Mapa docente](../mapa-docente-creacion-visualizacion/SKILL.md), conservando la selección.

## Sugerir el siguiente paso

Invocar [Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) para preparar
el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md), una sola vez
por respuesta y reutilizando el contexto y las comprobaciones disponibles:
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Priorizar la selección de fuentes pendiente o la creación del mapa; si ya hay un mapa válido, ofrecer consultarlo o visualizarlo y escoger el flujo siguiente.
