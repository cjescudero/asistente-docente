---
name: iniciar-proyecto-docente
description: Preparar o ajustar un proyecto docente con estructura de curso, selección explícita de fuentes, configuración, LEEME y AGENTS.md respetado. Usar al iniciar el proyecto o actualizar su organización; preguntar por datos que falten y conflictos. Recomienda el mapa y ofrece orientación sin crearlo automáticamente.
---

# Iniciar un proyecto docente

Guiar al profesor desde «Inicia mi proyecto docente» hasta un curso preparado
para trabajar. No exigir comandos ni una ficha completa. Esta skill prepara la
estructura y las instrucciones; no inicia otro flujo docente.

## Identificar contexto y fuentes

Leer el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md). Identificar
la raíz elegida por el profesor, sin confundirla con el plugin, su directorio
personal o un workspace con varios cursos. Si no está clara, pedirla antes de
escribir. Leer las instrucciones aplicables, `AGENTS.md` y la configuración que
ya exista.

Preguntar solo por lo que falte: contexto del curso, ubicación de materiales,
tipos de contenido y selección para la futura wiki. Admitir teoría, prácticas,
talleres, exámenes, soluciones y otros tipos, incluso mezclados en una carpeta.
Reutilizar decisiones explícitas; no recorrer toda la documentación para deducir
el temario. Identificar carpetas no equivale a haber leído sus documentos.

Solicitar las carpetas concretas que podrán alimentar el mapa y las exclusiones
de archivos o subcarpetas. No elegir toda la raíz ni `docente/` completo. Excluir
siempre resultados, borradores y el propio mapa; incluir `archivo/` solo cuando
se indique expresamente. La selección no autoriza publicación ni lectura de
fuentes excluidas a través de enlaces. Si se aplaza, registrar el estado pendiente
sin inventar un corpus y completar las partes independientes. Distinguirlo de
la decisión expresa de trabajar sin fuentes, que guarda selección vacía. Usar
rutas dentro del curso; si los materiales están fuera, proponer otra raíz que
los contenga o una integración acordada, sin mover originales por defecto.

## Preparar la estructura

Crear el árbol `curso-v1` definido en el contrato: `alumnado/` para materiales,
actividades y conocimientos; `docente/` para fuentes, evaluaciones, soluciones,
rúbricas, borradores, mapa y resultados; y `archivo/`. Guardar `proyecto-docente.json`
y un `LEEME.md` breve con la función de las carpetas y ejemplos de peticiones.
Dejar `docente/mapa-docente/` vacía y `map: null` cuando aún no exista mapa.
Incluir `docente/resultados/entregas/`. Cada lote de entregas tendrá una carpeta
por actividad y convocatoria, con `originales/`, `identificacion/` y `correccion/`
cuando se reciba. Conservar las descargas de Moodle y sus identificadores; no
inventar correspondencias por nombres. Todo `docente/resultados/` queda fuera
del corpus. Añadir carpetas vacías en cursos existentes es una actualización
aditiva; no reorganizar entregas previas sin una propuesta aprobada.

En un proyecto existente, distinguir añadir carpetas vacías de reorganizar
archivos. Antes de mover originales, presentar correspondencias, destinos,
colisiones y enlaces afectados conforme a [la guía de migración](../../docs/MIGRACION-0.7.md).
Aplicar solo la propuesta concreta aprobada, sin sobrescribir ni duplicar
materiales. Conservar mapas y selecciones existentes salvo actualización
solicitada. Los materiales nuevos se preparan en `docente/borradores/`; su paso
a `alumnado/` requiere un encargo de entrega. No generar copias de exportación
por sistema.

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
> `redactar-espanol-claro`, salvo indicación expresa distinta en el encargo.
> Conservar rigor, condiciones, cifras, terminología y citas; simplificar la
> expresión no autoriza a omitir información.

Es una preferencia local. No incrustar rutas personales ni cambiar la activación
global de [la skill de redacción](../redactar-espanol-claro/SKILL.md). Si no está
disponible, explicar la limitación y aplicar claridad y precisión sin afirmar
que se ha ejecutado.

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
falta. Ofrecer [orientación docente](../orientar-docente/SKILL.md) con ejemplos de
peticiones y recomendar crear el mapa con las fuentes elegidas como siguiente
paso; si ya existe, recomendar consultarlo. Si falta la selección, orientar
primero a elegir fuentes. Si el profesor decidió trabajar sin ellas, ofrecer
tareas con sus adjuntos sin insistir en crear el mapa. La recomendación no es un encargo:
no invocar su creación hasta que el profesor la pida. Si ya la ha solicitado,
tratarla como encargo separado de
[crear el Mapa docente](../crear-mapa-docente/SKILL.md), conservando la selección.
