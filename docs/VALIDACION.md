# Validación local

## Preparación de 0.10.0 — 21 de octubre de 2026

**381 pruebas automatizadas superadas**, con las dos pruebas PDF activadas,
en macOS con Python 3.12 y Chromium. La primera ejecución aislada no pudo iniciar
Chromium; se repitió con acceso al navegador local y la suite completa pasó.
Esta preparación no constituye una publicación ni una instalación comprobada
en ChatGPT Work, Claude Cowork o Moodle.

- Entrega de bancos: ejemplo con ocho IDs `01-A` a `02-D`, metadatos
  concordantes y cuatro modelos compuestos sin archivos ZIP. El compresor del
  repositorio corresponde a releases del plugin; la entrega individual del banco
  se indica expresamente en la skill.
- Variantes: campos en pareja, identidades únicas, conceptos/objetivo/dificultad,
  namespaces por banco, compatibilidad sin familias y familias frente a IDs
  independientes coincidentes. Manifest y snapshots conservan procedencia.
- Selección: cuatro modelos por defecto, una variante por principal dentro de
  cada modelo, principales distintas cuando existen suficientes, versiones
  distintas al reutilizar familias, semilla reproducible y cuotas solapadas.
  Fondo insuficiente falla antes de escribir; no se inventan preguntas.
- Proyecto: cursos nuevos usan `cuestionarios/`; curso-v2 anterior conserva las
  rutas previas sin ramas paralelas, registros usados intactos y rutas configuradas
  validadas frente a escapes y colisiones con otros tipos. Curso-v1 compatible.
- Ejemplo ejecutado: dos principales, cuatro variantes por principal y cuatro
  modelos de dos preguntas; ninguna versión compartida entre modelos, dos
  principales comunes correctamente indicadas. HTML de estudiante, solucionario,
  GIFT y manifiesto generados; PDF comprobado en la suite separada.
- Grafo: filtros, búsqueda, teclado, enlaces, arrastre, zoom, vista estudiantil,
  leyenda de destinatarios y símbolo pendiente comprobados en Chromium; también
  reorganización de nodos visibles, móvil y prueba con 600 nodos.
- Lector HTML: navegación, anclas, historial, enlaces profundos, búsqueda, filtros,
  vista móvil y ausencia de cargas de red verificados en Chromium.
- Wiki: explicaciones revisadas con fuentes sintéticas, acceso y lectura parcial
  respetados; registro y HTML actualizados. Revisión cualitativa de cantidad,
  duración y diálogo documentada en el catálogo; no equivale a un diálogo real
  probado en cada anfitrión.

La validación pública, las doce skills y sus interfaces, el registro del mapa y
la equivalencia de paquetes se comprueban desde la fuente común. Las pruebas de
paquetes cubren extracción, instalación de solo lectura y reproducción de ZIP.
Las comprobaciones remotas y la publicación son posteriores a esta preparación;
su resultado se registra en las [notas de la release 0.10.0](https://github.com/cjescudero/asistente-docente/releases/tag/v0.10.0).


## Nombres y organización guiada — 21 de octubre de 2026

Suite local: **368 casos, 366 superados y 2 pruebas PDF omitidas** por ser
opcionales en esta ejecución. Las pruebas PDF de la preparación anterior se
conservan como evidencia separada; no se han vuelto a ejecutar para este cambio
de nombres, instrucciones e interfaz. No se han cambiado los renderizadores.

- Doce skills y doce interfaces `agents/openai.yaml`; comprobación de nombres,
  frontmatter, descripciones cortas, enlaces locales y adaptadores.
- Pruebas de paquetes extraídos: recursos funcionales equivalentes, archivos de
  interfaz presentes, referencia de visualización incluida y antigua skill ausente;
  reproducción del ZIP y uso desde otra carpeta e instalación de solo lectura.
- Regresión de inicio vacío, repetición, instrucciones previas, curso-v1,
  exclusiones, colisiones, enlaces y revisión de registros de migración.
- Revisión de instrucciones con los casos del catálogo: nombres engañosos,
  archivos ilegibles, materiales mezclados, aprobación total/parcial/rechazo y
  conjuntos de examen congelados. Se verificó que cada caso tiene una salida
  explícita sin movimientos automáticos; no es una ejecución real del diálogo.
- Revisión de los tres recorridos del mapa: crear actualiza contenidos y vistas;
  regenerar conserva Markdown/metadatos; mostrar abre sin escribir. Consulta
  independiente. Las pruebas existentes de los generadores siguen pasando.

Validación pública y registro del mapa de ejemplo correctos. El validador de
biblioteca no comprueba anclas; los enlaces de las referencias nuevas se revisaron
por separado. Paquetes locales preparados; publicación, instalación real y orden
visible en ChatGPT/Claude pendientes. Sin modificaciones a cursos reales, copias
instaladas o instrucciones generales del workspace.

## Preparación inicial de 0.9.0 — 20 de octubre de 2026

**367 pruebas automatizadas superadas**, incluidas las dos pruebas PDF activadas
con `RUN_PDF_TESTS=1`. Ejecución local en macOS con Python 3.12.9 y Chromium.
Este resultado corresponde a la versión local; no acredita una ejecución de
0.9 en Windows/Linux, una instalación real en anfitriones ni una publicación.

| Comprobación | Resultado |
| --- | --- |
| Inicio y compatibilidad | Nuevos cursos `curso-v2`; repetición sin duplicados; `curso-v1` conserva estructura e instrucciones; previsualización y conflictos respetados. |
| Corpus | Selección explícita y estados por producción; borradores, registros ausentes/inválidos y resultados excluidos; un registro de categoría no acredita todos sus hijos. |
| Mapa existente | Retirar el estado revisado bloquea el acceso a esa fuente y marca sus dependencias transitivas pendientes antes de reutilizarlas. |
| Migración | Propuesta sin mover archivos, colisiones y enlaces; inventario `metadata_reviews` de registros que requieren revisión semántica, sin sustituir rutas dentro de snapshots. |
| Bancos | Catálogos anteriores conservados y `path_base: project` para bancos originales y nuevos sin duplicarlos; rutas fuera de la raíz rechazadas. |
| Exámenes | `--layout curso-v2` separa alumnado/docente; rutas del manifiesto y snapshots coherentes; salida plana anterior conservada. |
| Recorrido completo | Tres bancos, tres modelos, dos vías de calificación y feedback; originales intactos y datos estudiantiles fuera del corpus. |
| Distribución | Pruebas de ambos paquetes extraídos y de solo lectura, reconstrucción reproducible, equivalencia funcional y trece skills válidas. |

El ejemplo completo se ejecutó con PDF real fuera del plugin: seis PDF de
modelos/solucionarios y uno de actividad. Se comprobó la numeración de preguntas
en los tres modelos y la separación de archivos. La revisión visual cubrió las
dos páginas del modelo A estudiantil, la primera del solucionario B y el
enunciado de la actividad, sin texto cortado ni soluciones en la copia estudiantil.

La revisión independiente de instrucciones examinó una actividad sin entregas,
un examen con nota global sin detalle y una petición de apuntes en gallego.
Las sugerencias distinguen indicios de resultados comprobados, señalan entradas
pendientes, respetan el idioma pedido y no ejecutan pasos adicionales por su
cuenta. Se corrigieron dos ejemplos de feedback que conservaban la ruta plana
anterior del manifiesto. Esta revisión es cualitativa; no equivale a conversaciones
reales verificadas en ChatGPT Work o Claude Cowork.

Validación pública de manifiestos y enlaces, sincronización de adaptadores,
frontmatter de las trece skills y registro del mapa de ejemplo correctos. No se
modificaron skills instaladas, cursos reales ni instrucciones generales del
workspace. La publicación en GitHub y las importaciones Moodle quedan fuera de
esta entrega local. La release 0.8.0 permanece disponible.

## Historial: validación de 0.8.0

Fecha: 20 de octubre de 2026. Validación local previa a la publicación de **0.8.0**.

## Resultado de 0.8.0

**347 pruebas automatizadas aprobadas**, incluidas las dos pruebas PDF
opcionales activadas con `RUN_PDF_TESTS=1`. Ejecución local en macOS con Python
3.12.9 y Chromium disponible indicado mediante `ASISTENTE_DOCENTE_CHROMIUM`.
Durante la preparación de la release, GitHub detectó una diferencia de codificación
en Windows. Se fijó UTF-8 para stdout/stderr de la CLI y del ejemplo, se hicieron
explícitas las lecturas de archivos en las pruebas y se añadió una regresión con
consola cp1252, acentos y caracteres fuera de esa codificación. La suite local
completa volvió a pasar con PDF tras la corrección.

Este apartado documenta la ejecución local. Los resultados remotos para Windows,
Linux y macOS se registran por separado en [GitHub Actions](https://github.com/cjescudero/asistente-docente/actions/workflows/ci.yml);
no se deducen de estas pruebas locales.

| Comprobación | Resultado local |
| --- | --- |
| Inicialización nueva y repetida | Estructura aditiva, entregas excluidas, instrucciones conservadas y propuestas ante conflictos; mapa vacío. |
| Orientación | Revisión de instrucciones y casos: fuentes pendientes, decisión de no usar fuentes, mapa existente, adjuntos suficientes y nota global sin detalle. No equivale a una prueba en los anfitriones. |
| Actividades | Ejemplo experimental con enunciado, plantilla, rúbrica reservada, guía y registro; revisión de un caso de humanidades sin imponer programación. |
| Bancos y modelos | Tres bancos sintéticos con fuentes múltiples e IDs coincidentes; cuotas, semilla, insuficiencia, solapamiento, huellas, exclusiones, escapes y snapshots. |
| Corrección | Hoja de tarea y libro, grupo con miembros explícitos, duplicados, ausencias y documentos ilegibles/pendientes, versiones, cálculo y auditoría; límites de redondeo y CSV sin cambios ajenos. |
| Feedback | Máximo configurable, umbral y evidencia mínima, dificultad acusada frente a fallo aislado, referencias reservadas rechazadas y notas originales conservadas. |
| Compatibilidad | Bancos únicos y manifiestos anteriores; catálogo y campos de procedencia aditivos; funciones actuales de mapas y selección pasan sus regresiones. |
| Portabilidad | Recorrido completo por CLI desde otra carpeta y desde ambos paquetes extraídos con instalación de solo lectura; inicialización sin dependencias de terceros. |
| Distribución | Trece skills; validación pública de manifiestos, enlaces y recursos; equivalencia funcional y construcción reproducible de ambos paquetes y del archivo fuente. |

La [demostración reproducible](../examples/recorrido-docente/README.md) se ejecutó
además con PDF real: tres modelos, seis preguntas por modelo, seis PDF de
estudiante/docente, GIFT ofuscados, manifiesto y bancos congelados, más el PDF del enunciado de
la actividad asociado a su registro. La revisión visual cubrió ese enunciado, las dos páginas del modelo A estudiantil y la primera página del
solucionario B. Se comprobó la numeración de los tres PDF estudiantiles contra
el GIFT y el manifiesto, verdadero/falso con B correcta y tolerancias numéricas.
No hay créditos ni soluciones en los PDF estudiantiles ni enunciados originales
en los cuestionarios ofuscados.

El catálogo reutiliza las doce preguntas para dieciocho posiciones: el informe
muestra las coincidencias entre modelos, sin afirmar un óptimo global. Las dos
vías de actividad producen 8,75/10 para el grupo evaluado y conservan el caso sin
entrega. El feedback mantiene literalmente las notas del libro y vacía el
comentario del caso no presentado.

La revisión independiente detectó y corrigió dos casos límite, con regresiones:
referencias por pregunta que reclasificaban una fuente docente como estudiantil,
y redondeo capaz de superar una escala cuyo máximo no admite los decimales
configurados. La prueba de instalación de solo lectura detectó y corrigió que
la copia del ejemplo heredaba permisos no editables. Tras completar el PDF del
enunciado, se repitieron las 14 comprobaciones de integración y empaquetado,
todas aprobadas, y el recorrido completo con PDF.

También se comprobaron el frontmatter de la nueva skill con el validador de
Agent Skills, el catálogo y el manifiesto con Claude Code, la sincronización de adaptadores,
el mapa anterior y 219 enlaces locales y anclas de la documentación revisada. La revisión de comportamiento fue por lectura
de instrucciones y casos, no una evaluación en conversaciones reales de ChatGPT
Work o Claude Cowork.

**Pendiente fuera de esta entrega:** instalación real de 0.8.0 en ChatGPT Work y
Claude Cowork e importación en un servidor Moodle. La distribución del código y
los paquetes se recoge en la [release 0.8.0](https://github.com/cjescudero/asistente-docente/releases/tag/v0.8.0). Las limitaciones de Moodle se contrastaron con documentación
oficial enlazada, sin subir datos ni cambiar calificaciones. La release 0.6.0 y
los paquetes anteriores se conservan. No se modificaron las copias instaladas
de las skills ni las instrucciones generales del workspace.

## Historial de comprobaciones anteriores

Los apartados siguientes registran validaciones de 0.7 y versiones previas;
sus recuentos y fechas no describen la nueva ejecución de 0.8.

Fecha: 20 de octubre de 2026. Versión preparada localmente: **0.7.0**.

## Revisión de la instalación desde GitHub

La revisión documental del 20 de octubre de 2026 contrasta la importación del
marketplace en ChatGPT, los menús de Claude en español y las alternativas de
Codex CLI y Claude Code con las fuentes oficiales enlazadas en
[Instalación](INSTALACION.md). Distingue la incorporación del catálogo, la
instalación del plugin y las políticas de la organización. No se prevé publicar
el plugin en los directorios públicos de las plataformas.

Pasan la sincronización de manifiestos, la validación del plugin para
distribución pública en GitHub y la validación del catálogo mediante Claude
Code. Se repiten y superan las **10 pruebas de empaquetado**, incluidos recursos
comunes, construcción reproducible y uso desde otra carpeta. La revisión de
enlaces locales y anclas se realiza sobre la documentación modificada.

Las huellas de 45 archivos confirman que esta revisión conserva las skills,
scripts, biblioteca Python, recursos visuales y `AGENTS.md` existentes. No se
repiten pruebas funcionales de evaluación ni de PDF, porque no cambia su código.
Estas comprobaciones no acreditan una importación o instalación real desde las
interfaces de ChatGPT o Claude, ni una publicación de los cambios en GitHub.

## Puesta en marcha y organización del curso (0.7.0)

**260 pruebas superadas en macOS, Python 3.12.9.** La ejecución general pasó
258 y dejó las dos PDF opcionales omitidas; ambas se ejecutaron después con
Chrome local y también pasaron. Se conservan las pruebas de bancos, exámenes,
feedback, integridad y paquetes, y se añaden 54 para esta versión.

Comprobaciones nuevas:

- Curso nuevo, previsualización sin cambios, repetición sin alteración de bytes
  ni fechas, instrucciones anteriores conservadas y propuestas ante conflictos.
- Selección pendiente frente a selección vacía, rutas portables, carpetas
  inexistentes/vacías/sin archivos seleccionados y acceso denegado simulado.
- Exclusiones por archivo y subárbol, resultados y borradores fuera del corpus,
  enlaces simbólicos sin capacidad de eludir la selección y fuentes no leídas
  durante el diagnóstico.
- Examen reservado seleccionado y ausencia de su contenido en la vista
  estudiantil; retirada de una fuente y detección de dependencias transitivas.
  La validación se detiene antes de abrir los originales excluidos y bloquea la
  regeneración sin sobrescribir los HTML anteriores.
- Registro de un mapa real sin cambiar instrucciones ni selección; compatibilidad
  de mapas antiguos sin configuración de curso y del formato `fuentes.json`.
- Migraciones sin cambios, huellas de contenidos, destinos repetidos/existentes,
  solapamientos entre movimientos y enlaces Markdown que necesitan actualización.
- Utilidades ejecutadas desde otra carpeta sin `site-packages`, diagnóstico PDF
  separado y creación del curso desde ambos ZIP con el plugin de solo lectura.
  Preparación del entorno en caché externa con manifiesto OpenAI o Claude.
- Curso de ejemplo copiado fuera del plugin: selección exacta de tres fuentes,
  exclusión del examen retirado y carpeta del mapa vacía.

También se reprodujo la preparación de carpetas, instrucciones y configuración
mediante herramientas de archivos, sin ejecutar Python en esa preparación.
La comprobación posterior confirmó la estructura completa, fuentes pendientes,
mapa vacío y ausencia de `CLAUDE.md`. Esto acredita la alternativa de archivos
en este entorno; no demuestra que otros anfitriones seleccionen automáticamente
la skill o dispongan de esas herramientas.

Se comprobaron el lector y el grafo con Chrome temporal, sin la sesión del
usuario y con solicitudes remotas bloqueadas. Pasaron los tres programas de
comprobación: navegación, anclas, enlaces, filtros, búsqueda, selección,
Reorganizar, Ajustar, arrastre, escritorio, móvil y mapas de hasta 600 nodos.
Revisadas las capturas del ejemplo en escritorio y móvil. Los renderizadores
visuales no cambian; se verifica que la nueva validación conserva su recorrido.

Los nombres de las doce skills, enlaces, licencia, recursos y manifiestos pasan
la validación pública. El catálogo Claude pasa además `claude plugin validate`.
Ambos paquetes mantienen contenidos funcionales idénticos y construcción
reproducible; la fuente extraída reconstruye los ZIP desde otra carpeta.

**Pendiente fuera de la validación local:** ejecutar esta versión en Windows y
Linux, donde está preparada la matriz de GitHub Actions; instalarla y probar
el inicio real en ChatGPT Work y Claude Cowork; verificar la carga de instrucciones
en cada anfitrión. Las rutas de caché de los tres sistemas se comprueban en pruebas
locales, lo que no sustituye ejecutarlas en esos sistemas. Tampoco se han hecho
nuevas importaciones en Moodle.

La release pública 0.6.0 se conserva. La fuente 0.7.0 se distribuye desde `main`;
su subida no crea una nueva release ni instala el plugin automáticamente.
La revisión de instrucciones es local; no garantiza las decisiones pedagógicas
ni la activación de skills en otros modelos.

## Preparación pública y generalidad (0.6.0)

**205 pruebas aprobadas, incluidas las dos PDF, sin omisiones** en macOS,
Python 3.12.9 y Chrome local mediante un perfil temporal. No se ha cambiado el
renderizador; se comprueban además las nuevas funciones de distribución e
instalación. El código común de ambos paquetes es idéntico, las construcciones
son reproducibles y la fuente extraída reconstruye los mismos ZIP desde otra
carpeta. Los paquetes extraídos funcionan con la instalación de solo lectura.

Se verifican exclusión de archivos de entorno y cachés, licencia y avisos,
catálogos y adaptadores sincronizados, recursos compartidos y enlaces locales.
Se detectan un adaptador desactualizado y la ausencia de licencia. La suite
comprueba los comandos de instalación por plataforma, el rechazo de un destino
que no sea un entorno, el modo sin cambios y la parada ante fallos de instalación.

Instalación básica real en un entorno virtual temporal nuevo: descarga de
markdown-it-py y mdurl, diagnóstico `basic_ready: true`, `pdf_ready: false`, y
lector de trece documentos generado desde otra carpeta, sin Playwright ni
navegador en ese entorno. Esta prueba no sustituye una instalación de las skills
en un anfitrión. No se han modificado configuraciones globales.

Claude Code 2.1.50 valida sin errores ni avisos el manifiesto y el catálogo de
Claude. No se ha instalado el plugin en Claude Cowork ni ChatGPT Work. El
comando Codex disponible en esta máquina no permite comprobar la instalación
porque su ejecutable interno no está disponible; los archivos se validan con
las reglas locales y las referencias oficiales. Esta validación local no incluye
GitHub Actions ni importaciones nuevas en Moodle. Las ejecuciones remotas se
consultan por separado en [GitHub Actions](https://github.com/cjescudero/asistente-docente/actions).

Las doce skills y sus plantillas se revisaron para separar ejemplos de reglas
obligatorias; véase [generalidad](GENERALIDAD.md). Las pruebas no acreditan un
resultado pedagógico en toda disciplina. No se repitió la revisión visual de
la wiki o el grafo, cuyos generadores y presentación no cambian en esta versión.

## Respeto de instrucciones, redacción y orígenes (0.5.2)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF opcionales omitidas.** Sin
errores en el validador del plugin ni en los validadores de las skills de inicio
y redacción. La suite incluye extracción, equivalencia y portabilidad de ambos
paquetes. Se revisaron las instrucciones y los casos del catálogo para conservar
AGENTS.md, preguntar ante conflictos, registrar español claro por defecto y
solicitar solo ubicación o tipos de contenidos desconocidos, sin iniciar el mapa.

No se realizó una nueva simulación de conversación para esos casos ni pruebas
en cuentas externas. Las pruebas Python no verifican por sí solas que un agente
respete el procedimiento de preguntas. No se repiten PDF ni revisión visual,
porque esta versión modifica instrucciones y documentación, no renderizadores.

## Responsabilidades de inicio y creación del mapa (0.5.1)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF opcionales omitidas.** El
validador del plugin y los validadores de las dos skills modificadas no presentan
errores. La prueba de empaquetado comprueba la plantilla en la skill de creación
del mapa y su ausencia en la de inicio, además de equivalencia funcional y
ejecución de ambos paquetes extraídos fuera de la carpeta fuente.

Evaluación manual por un agente en dos proyectos temporales: la inicialización
de Historia creó solo instrucciones generales, sin preguntar por fuentes ni
continuar con el mapa. En una copia del mapa de ejemplo, el cierre de creación
integró el bloque en el `AGENTS.md` del proyecto y conservó una regla previa
del profesor. Comprobadas la entrada real y ambas raíces desde ese archivo.
La segunda aplicación mantuvo el resultado idéntico, sin duplicados; los otros
26 archivos de la copia conservaron sus huellas. El mapa de siete fuentes pasó
su validador. Esta evaluación se limita al reparto de instrucciones y al cierre
del flujo: no incluye una nueva síntesis del corpus ni renderizado.

No se repiten PDF ni revisión visual: no cambia el renderizado. Tampoco se ha
instalado esta versión en ChatGPT Work o Claude Cowork. La evaluación de 0.5.0
descrita debajo se conserva como historial y no representa el reparto actual
de responsabilidades.

## Puesta en marcha y consulta recursiva (0.5.0)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF opcionales omitidas.** El
validador del plugin y los validadores de las skills de puesta en marcha y
consulta no presentan errores. Las pruebas de empaquetado comprueban doce skills,
la nueva plantilla de `AGENTS.md`, contenido común idéntico, construcción
reproducible y ejecución desde los dos paquetes extraídos en otra carpeta, con
la instalación marcada de solo lectura.

Una evaluación manual por un agente, en un proyecto temporal con instrucciones
previas, aplicó la skill dos veces: conservó esas reglas, produjo una sola
sección sin campos pendientes y dejó el segundo resultado idéntico al primero.
Sin carpetas elegidas, no creó una wiki ni otras configuraciones; preparó la
pregunta de creación y selección de orígenes.

En un corpus sintético se siguió índice → concepto → ficha → original. El
original indicaba 40 ms y la síntesis 50 ms: la respuesta usó el original y
señaló la discrepancia. Se evitó un enlace cíclico al índice y no se aplicó como
vigente una rúbrica de 2023. La consulta conservó archivos, huellas SHA-256 y
fechas de modificación. Esta evaluación de instrucciones declarativas no es
una prueba de selección automática de la skill ni garantiza el comportamiento
de otros modelos o anfitriones.

No se han repetido la revisión visual de navegador ni las pruebas PDF: esta
versión cambia instrucciones, documentación y catálogo, sin modificar los
renderizadores. Las instalaciones reales en ChatGPT Work y Claude Cowork siguen
pendientes; la presencia de `AGENTS.md` no demuestra que un anfitrión lo cargue.

## Wiki navegable y reorganización (0.4.0)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF omitidas.** Incluyen generación
conjunta del lector y el grafo, documentos asociados sin inventar aristas,
rutas relativas desde otras carpetas, originales protegidos, reproducibilidad,
HTML incrustado inerte, enlaces y anclas Unicode, autorreferencias y bloqueo del
lector docente en una exportación estudiantil. Ambos paquetes se extraen y
generan HTML desde otra carpeta con la instalación marcada de solo lectura.

El ejemplo conserva 16 nodos y 29 relaciones docentes, y 12 nodos y 21 relaciones
estudiantiles. El lector incluye 13 documentos (nueve páginas y cuatro de guía y
registro). No cambia fuentes, estados de lectura ni relaciones académicas.

Comprobación en Chrome local con perfil temporal, Playwright y solicitudes
HTTP/HTTPS bloqueadas: escritorio 1440 × 960 y móvil 390 × 844. Verificados
Reorganizar sobre el conjunto visible, conservación de búsqueda/filtros/selección,
Ajustar sin mover nodos, arrastre, teclado, zoom y navegación de documentos
HTML/Markdown. Casos sintéticos de 48 nodos sin solapamientos de cajas, 320
conectados y 600 nodos con encuadre completo. Los mapas grandes requieren zoom
o filtrado para leer todas las etiquetas; encuadrarlos no hace legible todo a la vez.

En el lector se han probado índice → página → otra página, anclas, volver/avanzar,
recarga de enlaces profundos, búsqueda, tipos, área reservada, salto accesible y
menú móvil. También el recorrido real del ejemplo grafo → documento → índice →
concepto → volver → grafo. Sin errores JavaScript, ejecución de contenido hostil
ni solicitudes remotas en estos casos. Revisadas capturas de ambas vistas.

Comprobaciones opcionales de navegador (requieren navegador local):

```sh
python tests/check_graph_browser.py --html examples/mapa-docente/mapa-docente/grafo-docente.html
python tests/check_graph_layout.py
python tests/check_wiki_browser.py --html examples/mapa-docente/mapa-docente/index.html
```

Las capturas se guardan fuera del paquete. No se han repetido los PDF ni las
instalaciones/importaciones reales en ChatGPT Work, Claude Cowork o Moodle.


## Mapa docente y grafo (0.3.0)

**176 pruebas ejecutadas: 174 aprobadas y dos pruebas PDF omitidas**. Se mantienen
los casos anteriores y se incorporan pruebas de varias raíces seleccionadas,
páginas clasificadas y grafo derivado. Se comprueban compatibilidad del registro
anterior, raíces inválidas, conservación de originales, enlaces relativos desde
otra carpeta, generación reproducible y sobrescritura limitada al derivado propio.

El HTML estudiantil se valida por contenido: excluye fuentes y páginas privadas,
referencias sin clasificar y dependencias transitivas, incluidos ciclos y fuentes
con rutas alias. Los títulos se serializan como datos; una cadena con cierre de
script no se ejecuta. Se comprueba que no contiene enlaces salientes a archivos.

El ejemplo actualizado usa dos carpetas de materiales elegidas para la
demostración, siete fuentes y nueve páginas. Produce 16 nodos y 29 enlaces para
docencia; 12 nodos y 21 enlaces para estudiantes. Los originales son documentos
Markdown sintéticos. El contenido reservado no aparece en los datos del HTML
estudiantil; en el docente, ocultar evaluaciones es solo un filtro visual.

Comprobación real con Playwright 1.60 y Chrome local, usando perfil temporal:
búsqueda con y sin tildes, filtros por tipo y acceso, selección por teclado,
panel de relaciones, arrastre, desplazamiento, rueda, botones de zoom y
restablecimiento, vista móvil y modo estudiante. Sin solicitudes HTTP/HTTPS,
errores JavaScript ni ejecución de títulos hostiles en los casos comprobados.
Se ha revisado visualmente el ejemplo en escritorio y móvil. El navegador
necesitó ejecutarse fuera del sandbox que impedía su arranque; no utilizó la
sesión de navegación del usuario.

La comprobación de navegador es optativa y se ejecuta aparte:

```sh
python tests/check_graph_browser.py --html examples/mapa-docente/mapa-docente/grafo-docente.html
```

`ASISTENTE_DOCENTE_CHROMIUM` permite indicar el ejecutable existente;
`--screenshots` acepta una carpeta externa al paquete. El grafo no necesita
Playwright para generarse o consultarse: se usa únicamente en esta prueba.

Los paquetes incluyen once skills. La suite extrae ambos ZIP y ejecuta
validación y generación desde otra carpeta; compara el contenido funcional
común y la construcción reproducible. Los dos PDF no se regeneran en esta
ampliación: su renderer y sus flujos no cambian. Las pruebas en las cuentas de
ChatGPT Work, Claude Cowork y una instancia Moodle siguen pendientes.

## Validación previa de biblioteca docente (0.2.0)

Suite local: **140 pruebas ejecutadas, 138 aprobadas y dos pruebas PDF omitidas**.
Se incorporan 32 pruebas de inventario, lectura parcial, rutas, enlaces, huellas,
datos malformados y funcionamiento de solo lectura. Se comprueba detección de
fuentes cambiadas, ausentes, duplicados de ID y rutas que salen del corpus.

El ejemplo sintético contiene seis fuentes: cuatro lecturas completas, una
parcial y una pendiente, con dos mapas temáticos. Su validación de estructura y
huellas no presenta errores. También se comprueba desde ambos paquetes
extraídos en otra carpeta. Los paquetes contienen diez skills y recursos
funcionales idénticos; la construcción es reproducible. Los ZIP finales se
extraen y el validador de biblioteca funciona desde otra carpeta con la
instalación marcada de solo lectura. Se comprueban sus SHA-256.

La comprobación semántica del ejemplo contrasta síntesis, localizadores y
restricciones con sus originales Markdown. No acredita lectura de archivos
PDF/PowerPoint reales ni lectura de un corpus del profesor. El validador no
comprueba anclas, precisión pedagógica ni cobertura declarada por el agente.

Una consulta representativa local, siguiendo la nueva skill, identificó la
ausencia de rúbrica vigente, conservó el 8/2 como criterio histórico, delimitó
el contenido de las diapositivas y consultó el apéndice en el original antes
de responder sobre él. La consulta no modificó fichas ni estados. Es una prueba
de seguimiento de instrucciones en este entorno, no de selección automática
o instalación de la skill en ChatGPT Work o Claude Cowork.

Las dos pruebas PDF no se repiten en esta ampliación: el renderer, las fórmulas,
los exámenes y el feedback no cambian. Se conserva abajo la evidencia de 0.1.0;
no se presenta como una nueva ejecución de PDF en 0.2.0.

## Validación previa (0.1.0)

**108 pruebas aprobadas**, incluidas las dos pruebas PDF, sin pruebas omitidas
en aquella ejecución completa. Ambos paquetes de esa versión superaron la
validación.

## Evidencias

- Parser GIFT: pruebas con los cinco tipos de banco, escapes, feedback, pesos,
  tolerancias, Unicode y entradas rechazadas explícitamente.
- Exámenes: pruebas de semilla, cuotas, reutilización de preguntas, snapshot,
  orden de opciones, verdadero/falso con B correcta y precisión numérica.
- Feedback: pruebas de notas y dialectos preservados, blancos explícitos,
  duplicados, datos ausentes, correspondencias, detalle opcional y consolidado.
- Renderizado: generación real de PDF con fórmulas, detección de macros no
  soportadas y conservación del HTML cuando no se completa un PDF.
- Nueve PDF de demostración generados: cuatro de humanidades, cuatro de ciencias
  y unos apuntes. Las nueve páginas se renderizaron y revisaron visualmente:
  sin texto cortado, soluciones en hojas del estudiante ni fórmulas pendientes.
- Circuito de feedback con tres identidades sintéticas: dos comentarios
  individuales y un no presentado sin comentario, conservando las notas.
- Empaquetado: estructura validada, contenido común idéntico, hashes, construcción
  reproducible y ejecución desde ambos ZIP extraídos en otra carpeta.

## Entorno y repetición

Python 3.12, Playwright 1.60.0 y Chrome local en macOS. El navegador se ejecutó
fuera del sandbox del agente, que impedía su arranque. Se usó un perfil temporal
de Playwright, sin la sesión de navegación del usuario. Las solicitudes de red
del documento se bloquearon; MathJax se cargó desde el recurso incluido.

```sh
python -m unittest discover -s tests -v
python scripts/validate_plugin.py
python scripts/validate_library.py examples/mapa-docente/mapa-docente
python scripts/build_release.py
```

Para incluir las dos pruebas PDF, establecer `RUN_PDF_TESTS=1` con Chromium
disponible. `ASISTENTE_DOCENTE_CHROMIUM` permite seleccionar un ejecutable local.
Sin esa variable se utiliza el Chromium instalado por Playwright. El resto de
las pruebas no necesita navegador ni conexión a Moodle.

## Límites de lo comprobado

No se han instalado los ZIP en cuentas de ChatGPT Work o Claude Cowork ni se han
importado preguntas o comentarios en una instancia real de Moodle. La
compatibilidad de empaquetado no sustituye esas pruebas. Están descritas en
[compatibilidad](COMPATIBILIDAD.md) y [Moodle](MOODLE.md).

El pipeline está preparado para Linux, macOS y Windows. Sus resultados para
cada revisión se consultan en [GitHub Actions](https://github.com/cjescudero/asistente-docente/actions);
no se deducen de las comprobaciones locales descritas aquí.
El proyecto tiene licencia MIT y una release 0.6.0 publicada. Los casos del [catálogo](CATALOGO.md) permiten
evaluar cada skill en los anfitriones; la suite Python comprueba las utilidades,
no todas las decisiones pedagógicas del agente.
