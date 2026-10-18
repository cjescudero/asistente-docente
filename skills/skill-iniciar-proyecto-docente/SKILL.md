---
name: skill-iniciar-proyecto-docente
description: Preparar o ajustar el AGENTS.md de un proyecto docente, respetando lo existente y preguntando ante conflictos. Aclarar ubicación y tipo de materiales si faltan y establecer español claro por defecto. Usar al iniciar el proyecto o ajustar sus instrucciones; no crea ni propone crear el Mapa docente.
---

# Iniciar un proyecto docente

Preparar el contexto operativo del proyecto y sus instrucciones locales a partir
del encargo conocido. Esta skill termina con el `AGENTS.md` general del proyecto;
no inicia otro flujo docente.

## Delimitar el proyecto

Identificar la raíz del proyecto docente indicada por el usuario o inequívoca en
el contexto. Si falta, pedirla antes de escribir. No confundirla con la instalación
del plugin, el directorio personal o un workspace que agrupe varios proyectos.
Leer las instrucciones aplicables y el `AGENTS.md` existente.

Si no está claro dónde están los contenidos de origen o en qué consisten,
preguntar solo por lo que falte. Por ejemplo: «¿En qué carpeta o carpetas están
los materiales y qué contiene cada una: teoría, prácticas, talleres, exámenes,
soluciones u otros contenidos?». Reutilizar la información del encargo, del
`AGENTS.md` o del mapa ya identificado, sin repetir preguntas resueltas ni
recorrer toda la documentación para averiguarlo. Admitir varios tipos por carpeta.

Registrar las ubicaciones y su descripción breve cuando el usuario las indique,
preferentemente con rutas relativas al proyecto. Esta identificación aporta
contexto: no autoriza a inventariar, leer íntegramente, mover los materiales ni
crear el mapa. Si el usuario aplaza la respuesta, dejar ese dato pendiente sin
inventarlo y completar las partes independientes de la inicialización.

## Crear o completar las instrucciones

Crear el archivo si falta. Si ya existe, respetar su contenido y organización:
modificar únicamente los puntos indicados en el encargo, sin reescribir,
reordenar ni normalizar el resto. Una petición de inicialización no autoriza a
sustituir el archivo ni a imponer de nuevo todas las reglas generales.

Ante cualquier conflicto entre lo solicitado y las instrucciones existentes,
mostrar las reglas incompatibles y preguntar al usuario cuál debe mantenerse o
cómo conciliarlas. Esperar su respuesta antes de modificar la parte en conflicto;
conservarla mientras tanto. No resolver el conflicto silenciosamente. Completar
solo los cambios independientes que estén autorizados.

Registrar solo el contexto y las decisiones conocidos: asignatura y
audiencia cuando consten, objetivos, idioma, organización de entregables y
criterios de trabajo. No inventar datos ni exigir una ficha completa para empezar.
Mantener en el archivo instrucciones operativas; remitir a documentos del proyecto
para los detalles docentes extensos, si ya están identificados.

Separar material para estudiantes de soluciones y criterios docentes. Fundamentar
la evaluación en la rúbrica vigente del encargo y sus evidencias. Preservar las
fuentes y guardar los resultados fuera de la instalación del plugin. Adaptar estas
reglas al crear un archivo nuevo o cuando el encargo pida incorporarlas; no
añadirlas por sistema a un archivo existente ni reemplazar decisiones del profesor.

## Redacción predeterminada

Incorporar, como parte de esta puesta en marcha, la siguiente regla en el
`AGENTS.md`, integrándola una sola vez y aplicando el procedimiento de conflictos:

> Para redactar o revisar textos del proyecto en español, usar por defecto
> `skill-redactar-espanol-claro`, salvo indicación expresa distinta en el encargo.
> Conservar el rigor, las condiciones, las cifras, la terminología y las citas;
> simplificar la expresión no autoriza a omitir información.

La referencia corresponde a
[Redactar español claro](../skill-redactar-espanol-claro/SKILL.md).
Es una preferencia de este proyecto, no un cambio de activación global. No
incrustar rutas personales de instalación en el archivo generado. Si la skill
no está disponible en el anfitrión, comunicarlo y aplicar los criterios escritos
de claridad y precisión sin afirmar que se ha ejecutado la skill.

Repetir la puesta en marcha debe conservar el contenido sin duplicar secciones.
Si existe un bloque de consulta del Mapa docente, conservarlo junto a sus enlaces;
no trasladarlo, borrarlo ni sustituirlo por un estado pendiente. No añadir una
política de wiki futura ni rutas previstas para un mapa que no existe.

## Alcance y cierre

No preguntar por la creación de la wiki ni invocar la skill de creación del
mapa. Si el usuario ha pedido además un mapa,
ese es un encargo separado que corresponde a
[crear el Mapa docente](../skill-crear-mapa-docente/SKILL.md): esa skill identifica
las fuentes y añade a `AGENTS.md` la consulta del índice como punto de partida.
La inicialización no es un requisito previo para crear un mapa.

Comprobar que el archivo está en el proyecto correcto, que conserva las reglas
previas, que incluye la preferencia de redacción acordada y que las ubicaciones
y tipos de materiales son conocidos o están expresamente pendientes. No dejar
datos inventados ni rutas de instalación. Informar del cambio realizado sin
encadenar la creación del mapa. No crear `CLAUDE.md` ni
modificar instrucciones globales. Si el anfitrión no carga `AGENTS.md`, indicar
que debe adjuntarse o leerse explícitamente.
