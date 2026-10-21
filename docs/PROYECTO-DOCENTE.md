# Proyecto docente: puesta en marcha y contrato común

Instala el plugin, abre la carpeta del curso y pide **«Inicia mi proyecto docente»**.
También puedes pedir **«Adapta la organización de mi curso»**. El agente revisa
lo que ya hay, propone los cambios y explica lo que falta. El profesor no necesita
escribir comandos ni completar una ficha pedagógica para una petición sencilla.

## Estructura del curso

Los proyectos utilizan `curso-v3`. Separa la procedencia de los materiales,
su tipo y el destinatario; un borrador conserva su ubicación al revisarse.

```text
curso/
├── AGENTS.md
├── _datos_internos_proyecto/
│   ├── proyecto-docente.json
│   └── inventario-inicial.json   (solo cuando se prepare)
├── LEEME.md
├── fuentes/
│   ├── teoria/
│   ├── actividades/
│   └── evaluaciones/
│       ├── cuestionarios/
│       └── bancos/
├── materiales_generados/
│   ├── materiales/
│   ├── actividades/
│   ├── bancos/
│   └── cuestionarios/
├── mapa-docente/
├── resultados/
└── archivo/
```

`fuentes/` conserva materiales aportados, vigentes o históricos. Por ejemplo,
un cuestionario anterior puede estar en `fuentes/evaluaciones/cuestionarios/2025-2026/`.
`materiales_generados/` contiene lo elaborado en este proyecto, también cuando se convierte
en entrada de otra tarea: no copiar una actividad nueva a `fuentes/` para crear
un banco a partir de ella. Los originales enlazados mantienen una única ubicación.
Un Markdown y su PDF son formatos del mismo material.

Cada actividad se guarda en `materiales_generados/actividades/<id>/`, con `alumnado/` para
enunciado y plantillas, `docente/` para rúbrica completa y guía, y `_datos_internos/actividad.json` para su registro.
Cada evaluación se guarda en `materiales_generados/cuestionarios/<id>/`, con modelos imprimibles
estudiantiles y documentos docentes separados. Los bancos están en
`materiales_generados/bancos/<id>/`; los apuntes, imágenes y otras ayudas, en
`materiales_generados/materiales/<id>/`. Separar también allí notas reservadas cuando existan.
El catálogo se guarda en `materiales_generados/bancos/_datos_internos/catalogo.json`.
Los datos técnicos de cada banco y actividad se guardan en su `_datos_internos/`.
Los nombres de carpetas organizan contenidos; no conceden ni restringen acceso.

Cada cuestionario nuevo es un conjunto autocontenido:

```text
materiales_generados/cuestionarios/<id>/
├── LEEME.md
├── alumnado/                 modelos imprimibles
├── docente/                  solucionarios y GIFT de Moodle
└── _datos_internos/
    ├── seleccion.json        selección previa, única y congelada
    ├── material-docente.json
    ├── manifest.json
    ├── coverage.json
    └── source/               bancos y metadatos congelados
```

La selección puede prepararse antes de generar; el destino no puede contener
otros resultados. La generación no sobrescribe modelos existentes. `LEEME.md`
enlaza los archivos de interés del profesor. Una pregunta del banco y su modelo
se identifican mediante el manifiesto, no por parecido de texto.

Cada lote puede prepararse al terminar la actividad, si el profesor acepta la
oferta, o al recibir las entregas dentro de un encargo de evaluación. Se organiza en
`resultados/<actividad-o-evaluacion>/<convocatoria>/`, con `recibidos/` para
originales descargados de Moodle y correspondencias de identificación y
`correccion/` para evaluaciones, CSV modificados, feedback e incidencias.
Para actividades, reutilizar su identificador y nombre de carpeta; los trabajos
van en `recibidos/entregas/` y la hoja Moodle original en `recibidos/`. Un LEEME
del lote explica entradas, enlaces a criterios y pasos de evaluación, según
[Recepción y corrección](ACTIVIDADES.md#recepción-y-corrección). No crear CSV ficticios
ni confundir carpetas preparadas con entregas recibidas.
Todo `resultados/` queda fuera del corpus de la wiki. Conservar los originales;
una actualización del CSV es una copia de trabajo necesaria, no una sustitución
de la exportación recibida.

`archivo/` guarda materiales apartados y solo alimenta el mapa si el profesor lo
selecciona expresamente. La inicialización deja `mapa-docente/` vacía; recomienda
crearlo sin invocar esa creación. Solo un mapa real integra su índice en
`AGENTS.md`. Repetir la inicialización conserva la selección y no reorganiza
archivos por sí solo.

## Estado de los materiales creados

Cada conjunto nuevo mantiene `_datos_internos/material-docente.json` y un
`LEEME.md` con el estado visible. La [plantilla del registro](../templates/material-docente.json)
es un ejemplo que se adapta al resultado real. Ejemplo:

```json
{
  "schema_version": 1,
  "id": "analisis-de-fuentes",
  "type": "actividad",
  "status": "borrador"
}
```

Los tipos admitidos son `material`, `actividad`, `banco`, `cuestionario`, `apuntes`,
`diapositivas` e `infografia`. `material` permite registrar las ayudas sin una
clasificación más específica. Los estados son
`borrador`, `revisado` y `listo-para-entregar`. El registro común identifica tipo
y estado; `_datos_internos/actividad.json`, los metadatos del banco y el manifiesto del cuestionario
conservan sus contratos específicos de procedencia, versión y evaluación.

- `borrador`: contenido en preparación o con comprobaciones pendientes.
- `revisado`: se completaron las revisiones pertinentes; anotar su alcance y las
  capacidades pendientes. No equivale a aprobación del profesor ni a publicación.
- `listo-para-entregar`: los archivos previstos están preparados para su destino
  y se ha comprobado la separación del material reservado. No significa que se
  hayan entregado ni importado en Moodle.

Cambiar el estado de acuerdo con revisiones reales y mantener coherencia con el
`LEEME.md`. No mover carpetas al aprobar ni marcar como revisado para eludir una
exclusión. Un cambio sustantivo que invalide la revisión devuelve el material a
`borrador` y obliga a revisar sus dependencias. Conservar versiones ya utilizadas
en una evaluación; una versión nueva no modifica los snapshots de un cuestionario.
No exigir este registro a una respuesta breve de conversación ni a originales.

## Configuración operativa

`_datos_internos_proyecto/proyecto-docente.json` utiliza UTF-8 y rutas relativas dentro de la raíz del
curso, sin segmentos `..`. Las fuentes externas requieren elegir una raíz de
curso que las contenga o acordar su integración mediante una propuesta de
movimientos; no se trasladan originales automáticamente.
La única configuración operativa admitida está en
`_datos_internos_proyecto/proyecto-docente.json`. Un archivo con ese nombre en
la raíz requiere aclarar su función antes de iniciar; no se interpreta como
configuración del curso. Un JSON aportado como material no se mueve por su
extensión.
Si se inventaría un curso con materiales previos, `inventario-inicial.json`
registra rutas relativas, clasificación y dudas en `_datos_internos_proyecto/`;
no declara leídos documentos que solo se hayan inspeccionado parcialmente.

La versión del formato es independiente de la versión del plugin. Ejemplo:

```json
{
  "schema_version": 1,
  "structure": "curso-v3",
  "questionnaire_paths": {
    "sources": "fuentes/evaluaciones/cuestionarios",
    "created": "materiales_generados/cuestionarios"
  },
  "sources": {
    "selected": true,
    "include": ["fuentes/teoria", "fuentes/actividades"],
    "exclude": ["fuentes/actividades/actividad-pendiente.pdf"]
  },
  "map": null
}
```

- `sources.include` contiene carpetas elegidas expresamente. Se incluyen sus
  archivos descendientes, salvo las exclusiones. No seleccionar toda la raíz del
  curso ni una carpeta general que mezcle fuentes y datos personales: elegir
  las carpetas concretas.
- `sources.exclude` contiene rutas exactas de archivos o carpetas; no admite
  patrones glob. Excluir una carpeta excluye sus descendientes. Resolver también
  enlaces y rutas secundarias contra estas restricciones antes de abrir fuentes.
- En `curso-v3`, `resultados/`, `mapa-docente/`, `_datos_internos_proyecto/`
  y todas las carpetas `_datos_internos/` quedan siempre fuera del corpus.
  Los documentos de `materiales_generados/` requieren selección explícita y un registro común
  válido en estado `revisado` o `listo-para-entregar`. Los borradores y el registro
  común `_datos_internos/material-docente.json` no son fuentes. La selección no cambia el acceso docente
  o estudiantil de cada documento; los bancos y solucionarios siguen reservados.
- Respetar las exclusiones sin reintroducir documentos mediante otra raíz o un
  enlace. Una evaluación puede leer entradas aportadas expresamente para su
  encargo sin convertirlas en fuentes de la wiki.
- `sources.selected: false`, con `include` y `exclude` vacíos, indica selección
  aplazada. `selected: true` con listas vacías registra la decisión explícita de
  trabajar sin fuentes por ahora. Ninguno de esos estados selecciona todas las
  carpetas. Completar las partes independientes y preguntar por las fuentes
  cuando sean necesarias.
- `map` es `null` hasta que exista un mapa con `index.md` real. Después contiene
  la ruta relativa de su carpeta. La mera existencia de la carpeta vacía no
  permite registrarla como mapa creado.

La selección autoriza a usar un corpus en encargos que lo necesiten; no declara
sus documentos leídos ni autoriza su publicación. `_datos_internos/fuentes.json` conserva su
formato: registra lo inventariado, los estados de lectura y las páginas del
mapa. No sustituye la selección operativa ni convierte fuentes antiguas en
fuentes todavía admitidas. La ficha de asignatura es opcional y contiene nivel,
objetivos, idioma y criterios pedagógicos, sin duplicar esta configuración.

Si una ruta no puede representarse de forma relativa, como entre unidades de
Windows, explicar la limitación y acordar una ubicación accesible. No mover ni
copiar originales para resolverla por iniciativa propia.

## Organizar materiales existentes

La revisión precede a la creación de la estructura. El agente distingue una
carpeta vacía de una carpeta con materiales mezclados o de un curso configurado.
Lee las instrucciones y configuración existentes e inventaría los archivos
pertinentes, excluyendo entornos, cachés y componentes ajenos a la docencia.
La imposibilidad de acceder a un archivo no prueba que no haya contenido.

Nombres, rutas, extensiones y fechas orientan la inspección; no sustituyen la
lectura necesaria para clasificar. «Examen», «final» o «2025» no prueban acceso,
vigencia ni procedencia. La propuesta distingue clasificación comprobada,
provisional y pendiente de aclaración, y limita sus afirmaciones a los fragmentos
realmente revisados. Un archivo ilegible conserva su incertidumbre.

Antes de mover, el agente muestra una tabla con **origen, destino, contenido
identificado, motivo y dudas pendientes**, además del árbol resultante. Los
destinos de referencia para `curso-v3` son:

| Contenido identificado | Destino propuesto |
| --- | --- |
| Teoría aportada | `fuentes/teoria/` |
| Actividades aportadas | `fuentes/actividades/` |
| Cuestionarios aportados o de referencia | `fuentes/evaluaciones/cuestionarios/` |
| Bancos aportados | `fuentes/evaluaciones/bancos/` |
| Material elaborado en el proyecto, con procedencia confirmada | `materiales_generados/`, según su tipo |
| Entregas y exportaciones originales de Moodle | `resultados/<actividad>/<convocatoria>/recibidos/` |
| Correcciones y feedback producidos | `resultados/<actividad>/<convocatoria>/correccion/` |
| Mapa existente | Conservar su ubicación o proponer traslado con revisión de enlaces |

Son destinos propuestos según evidencia, no reglas automáticas por nombre.
Mantener juntos enunciado, plantillas, rúbrica y solución, o modelos, manifiesto
y bancos congelados. Separar dentro de cada conjunto lo destinado al alumnado
y lo reservado. No convertir todo lo antiguo en fuente ni todo lo reciente en
material creado; no usar `archivo/` para ocultar dudas de clasificación.

El profesor puede aceptar todos los movimientos mostrados, aprobar una parte,
corregir destinos o conservar la organización actual. Resolver primero las dudas
que afecten a los destinos. Si rechaza movimientos, continuar únicamente los
ajustes compatibles solicitados. No crear un segundo árbol para imponer la
organización rechazada. La organización y la selección del corpus son decisiones
separadas: mover un archivo no lo incorpora automáticamente a la wiki.

Antes de aplicar la parte aprobada, comprobar colisiones, dependencias y enlaces;
no sobrescribir archivos ni decidir nombres alternativos silenciosamente.
Registrar rutas y huellas para contrastar integridad. Actualizar los enlaces,
configuración y registros afectados de forma selectiva, revisando sus contratos.
Los manifiestos y snapshots de exámenes utilizados conservan versiones,
identificadores, orden, pesos y correspondencias; no regenerarlos con bancos
actuales. Comprobar huellas de archivos trasladados sin edición y revisar por
separado los cambios de rutas autorizados. Al terminar, informar de lo movido,
lo conservado y lo pendiente. `plan-migration` prepara comprobaciones y propuestas;
no clasifica por nombres ni ejecuta movimientos.

En cursos configurados, conservar las reglas del profesor y la estructura
`curso-v3`. No adaptar instrucciones en conflicto sin consultarlo. Una
repetición no vuelve a mover archivos ni duplica reglas.

## Recorrido del agente

1. Identificar la raíz y leer instrucciones y configuración. **Antes de crear la
   estructura**, revisar si contiene materiales o un mapa e inventariar lo pertinente.
2. Preguntar solo por contexto, ubicaciones, tipos, selección y ambigüedades que
   falten. Si hay materiales, mostrar la propuesta de organización, tabla y árbol;
   aplicar únicamente los movimientos aprobados tras comprobar sus dependencias.
3. Preparar la estructura acordada, guardar la selección o su estado pendiente,
   completar `LEEME.md` y conciliar `AGENTS.md` dentro del alcance autorizado.
   Conservar texto ajeno; consultar conflictos. Repetir sin duplicar ni sobrescribir.
4. Usar **Español conciso** por defecto mediante `espanol-conciso-redaccion`, salvo
   idioma o estilo indicado por el profesor. Conservar rigor, matices, condiciones
   y atribuciones. Mantener el bloque del mapa y sus rutas, sin entradas ficticias.
5. Comprobar integridad, rutas y capacidades; comunicar lo realizado y lo pendiente.
   No lanzar otro flujo al cerrar. Ofrecer entre uno y tres pasos según
   [los flujos docentes](FLUJOS-DOCENTES.md), recomendar el mapa si falta y
   comprobar resultados existentes antes de proponer crearlos de nuevo.

Los ayudantes de archivos proponen texto cuando `AGENTS.md` ya existe; el agente
integra solo lo autorizado. No aceptar un bloque generado como sustitución de las
instrucciones del profesor. Verificar la carga de `AGENTS.md` en el anfitrión; si
no se incorpora automáticamente, pedir su lectura explícita o utilizar las
instrucciones de carpeta disponibles. No crear `CLAUDE.md` por sistema ni cambiar
la configuración global del anfitrión.

## Comprobaciones antes de cada encargo

Todas las skills aplican este contrato en la medida necesaria para la tarea.
No exigir un proyecto inicializado, una wiki o carpetas llenas para corregir un
texto o producir una actividad con adjuntos suficientes. Comprobar solo las
entradas necesarias y detener únicamente el trabajo que dependa de las ausentes.

Distinguir carpeta inexistente, carpeta vacía, carpeta con archivos pero ninguno
seleccionado y archivos no accesibles. Un problema de acceso o de lectura no
prueba ausencia de contenido y nunca es un fallo del estudiante. No buscar en
carpetas vecinas para completar entradas ni inventar el contenido que falta.

Cuando exista un mapa, empezar por su índice y seguir recursivamente solo los
enlaces pertinentes. Detenerse al reunir evidencia suficiente; evitar ciclos y
relecturas. Verificar originales para citas, calificaciones, preguntas evaluables,
contradicciones o elementos visuales relevantes. Los adjuntos aportados para un
encargo pueden usarse con sus límites, sin incorporarlos automáticamente al mapa.

Antes de crear, actualizar, consultar o visualizar el mapa, contrastar su registro
con la selección vigente. No seguir un enlace a una fuente excluida. Si una
fuente retirada ya sustentaba páginas, identificar sus dependencias directas e
indirectas y señalarlas como pendientes de revisión. Durante una consulta, emitir
la incidencia sin editar archivos; durante el mantenimiento autorizado, revisarlas
antes de volver a utilizarlas. No generar un lector o grafo actualizado si la
validación detecta dependencias fuera del corpus. No presentar HTML antiguos como
si reflejaran la selección nueva.

## Utilidades y capacidades

Los comandos siguientes son para el agente o para mantenimiento. Resolver la
instalación del plugin y las rutas del curso; el profesor puede pedir todas estas
operaciones en lenguaje natural:

```sh
python scripts/docencia.py init-project RUTA_CURSO --include fuentes/teoria --exclude fuentes/teoria/borrador.pdf --dry-run
python scripts/docencia.py init-project RUTA_CURSO --include fuentes/teoria
python scripts/docencia.py init-project RUTA_CURSO
python scripts/docencia.py init-project RUTA_CURSO --no-sources
python scripts/docencia.py check-project RUTA_CURSO
python scripts/docencia.py doctor --project RUTA_CURSO
python scripts/docencia.py plan-migration RUTA_CURSO --moves movimientos.json
python scripts/docencia.py register-map RUTA_CURSO RUTA_MAPA --dry-run
```

`--include` y `--exclude` se pueden repetir. Sin opciones de selección, un
proyecto nuevo queda pendiente y uno existente conserva su selección.
`--no-sources` registra explícitamente una selección vacía (`selected: true`);
usarlo solo cuando esa sea la decisión del profesor. La previsualización no
modifica archivos. `plan-migration` produce un informe, no aplica movimientos.
`register-map` registra únicamente un índice ya creado; no genera la wiki ni
reescribe las instrucciones del profesor. Consultar la ayuda de cada comando
para los argumentos admitidos.

Los informes distinguen lo realizado de lo pendiente. `init-project` puede
crear carpetas y configuración y devolver `pending_approval` (código 2) porque
conserva un `AGENTS.md` o `LEEME.md` existente y propone su actualización.
Revisar `created`, `updated` y `proposals`; no repetir cambios por interpretar
ese estado como un fallo total. `check-project` devuelve código 2 para un
proyecto incompleto, incluidas fuentes pendientes, vacías o no seleccionadas;
código 1 indica configuración inválida y código 0 indica comprobación correcta.
`doctor` conserva además su diagnóstico de capacidades. Las tareas con entradas
suficientes pueden continuar aunque otra capacidad o carpeta esté pendiente.

La preparación de carpetas, configuración e instrucciones puede hacerse con las
herramientas de archivos del agente, sin Python. Mantener el mismo contrato y
comprobar manualmente los resultados. Python 3.10 o posterior es necesario para
las utilidades; el lector requiere las dependencias básicas. PDF sigue siendo
opcional. Reutilizar el entorno del anfitrión cuando sirva; si hay que preparar
otro, usar la caché de usuario fuera del curso y del plugin. El modo `--dev`
conserva un entorno `.venv` local para desarrollar el plugin; no es la preparación
normal de un curso.
Conservar Markdown y HTML cuando falte una capacidad; declarar PDF, grafo o
revisión pendientes según corresponda, sin afirmar que existen.

El proyecto puede estar en una carpeta local sincronizada con OneDrive o
SharePoint si los archivos están disponibles localmente. El plugin no configura
sincronización, conectores ni permisos remotos. Copilot Studio queda fuera de
esta versión.

## Rutas de cuestionarios

La configuración declara `questionnaire_paths.sources` como
`fuentes/evaluaciones/cuestionarios` y `questionnaire_paths.created` como
`materiales_generados/cuestionarios`. Los originales aportados y las nuevas
producciones conservan así una ubicación estable. Una ubicación no determina
por sí sola la vigencia ni el destinatario del contenido.

## Ayuda contextual durante el trabajo

Ante dudas sobre el uso del plugin, los flujos, archivos o resultados, preguntas
sobre posibilidades o siguientes pasos, el agente invoca `proyecto-docente-ayuda`
como ayuda inline. No hace falta conocer su nombre ni esperar a terminar una
actividad: puedes preguntar «¿Y ahora?», «¿Qué puedo hacer con lo que tengo?» o
«¿Para qué sirve este archivo?» dentro de la misma conversación.

La ayuda revisa el contexto disponible de la conversación (objetivos, decisiones,
preferencias, resultados e incidencias) y comprueba el estado pertinente del curso
en instrucciones, configuración, índices y registros. Reutiliza comprobaciones
vigentes y no vuelve a preguntar datos ya conocidos. Si falta acceso o contexto,
lo indica y pide únicamente lo necesario; no recorre todo el curso para orientar.

Resuelve primero la duda y ofrece opciones cuando correspondan. No ejecuta una
tarea por sugerirla ni modifica archivos o calificaciones. Si hay un encargo en
curso, la ayuda no lo cancela: se retoma después. Se aplica una vez por respuesta,
sin invocarse recursivamente. Las preguntas sobre la materia se atienden con los
flujos de contenido, conservando la ayuda para dudas sobre su uso o continuidad.

Las plantillas de `AGENTS.md` incorporan esta regla en cursos nuevos y propuestas
para cursos existentes. Actualizarlos mantiene el procedimiento de conservación
y consulta de conflictos; instalar el plugin no modifica instrucciones previas.
La regla solo puede aplicarse cuando el anfitrión carga las instrucciones y la
skill; las verificaciones locales no certifican una activación real en cada producto.
