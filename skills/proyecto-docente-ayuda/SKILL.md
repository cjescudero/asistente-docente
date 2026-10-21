---
name: proyecto-docente-ayuda
description: Resolver dudas sobre Asistente docente y el proyecto como ayuda inline. Invocar siempre ante preguntas sobre qué puede hacer el plugin, cómo continuar, siguientes pasos, flujos, archivos, resultados o entradas necesarias, también durante otra skill y al orientar tras una tarea. Revisar primero el contexto disponible de la conversación y el estado pertinente del curso. Responder a la duda o proponer opciones sin iniciar otros procesos. Las preguntas disciplinares sobre contenidos corresponden a mapa-docente-consulta.
---

# Proyecto docente: ayuda

Dar una ayuda breve y adaptada al curso. El profesor no necesita conocer nombres
de skills ni leer manuales. Consultar el [catálogo](../../docs/CATALOGO.md) para
enrutar un encargo, y el [contrato del curso](../../docs/PROYECTO-DOCENTE.md) para
interpretar sus carpetas.

Usar por defecto [español conciso](../espanol-conciso-redaccion/SKILL.md) en la
conversación y los documentos, salvo que el profesor indique otro idioma o estilo.
Respetar citas, identificadores y términos que deban conservarse literalmente.

## Activación como ayuda inline

Invocar esta skill antes de responder dudas sobre el uso del plugin o el
proyecto, preguntas de siguientes pasos o qué se puede hacer, y explicaciones
sobre sus flujos, archivos y resultados. Se aplica también a preguntas breves
como «¿y ahora?», «¿para qué sirve este archivo?» o «¿qué falta?», y a dudas que
aparezcan durante otra skill. El profesor no tiene que mencionar su nombre.
Usarla también para preparar la orientación al terminar una tarea.

La ayuda forma parte de la respuesta en la conversación, no abre otro proyecto
ni exige pasar a un modo separado. Cargar y aplicar la skill mediante el mecanismo
disponible en el anfitrión; no limitarse a sugerir al profesor que la invoque.
Una aplicación por respuesta basta para reunir todas sus dudas y sugerencias;
esta skill no se invoca a sí misma ni vuelve a iniciar el cierre de otra.
Si el anfitrión no dispone de la skill, explicar la limitación y orientar con el
contexto verificable, sin afirmar una invocación que no se ha realizado.

Las preguntas sobre el contenido de una asignatura corresponden a la consulta
del mapa o a la skill que elabore ese contenido. Cuando el mensaje mezcle una
duda de uso y un encargo concreto, resolver la orientación con esta ayuda y
continuar el encargo ya autorizado con su skill, sin pedir repetirlo.

## Recuperar el contexto disponible

Antes de orientar, revisar el historial disponible de esta conversación y sus
resúmenes: objetivo actual, decisiones y restricciones, materiales identificados,
resultados y rutas ya comunicados, incidencias pendientes y último encargo.
Respetar correcciones y preferencias posteriores. No repetir preguntas cuyas
respuestas consten ni recomendar empezar fases ya completadas. No inventar
historial ausente ni buscar otras conversaciones por sistema.

Comprobar el estado actual del proyecto en lo pertinente a la duda. Reutilizar
registros ya revisados en esta tarea si siguen vigentes y contrastar cambios
conocidos desde esa revisión. Si conversación y archivos discrepan, explicar
qué se ha comprobado y qué queda pendiente; no concluir por un nombre o fecha.
El contexto orienta la comprobación, no acredita por sí solo que un PDF existe,
un banco está validado o unas notas se han importado en Moodle.

## Reconocer el estado sin leerlo todo

1. Identificar la raíz y leer las instrucciones aplicables. Consultar
   la configuración en `_datos_internos_proyecto/proyecto-docente.json`. Si no se conoce la raíz, preguntar por ella
   solo si hace falta para resolver esa duda. Ofrecer lo que pueda contestarse
   con la conversación y documentación disponible; no bloquear una explicación
   de formatos por desconocer la carpeta. No confundir la instalación del plugin
   o su repositorio de desarrollo con la raíz de un curso.
2. Revisar solo los índices y registros necesarios: índice del mapa registrado,
   catálogo en `materiales_generados/bancos/_datos_internos/`, registros `_datos_internos/material-docente.json` y actividades,
   manifiestos de cuestionarios y nombres de lotes en `resultados/`. Leer cabeceras o informes de ejecución solo
   cuando hagan falta para verificar un indicio. No leer entregas ni calificaciones
   para dar una orientación inicial. La mera presencia de archivos no demuestra
   que estén revisados, actualizados, accesibles o completos.
3. Distinguir lo comprobado, lo pendiente y lo desconocido. Respetar la selección
   y las exclusiones, también mediante enlaces. No ampliar el corpus ni escanear
   todo el curso para suplir información ausente.

## Responder y proponer un siguiente paso

Contestar primero la duda concreta: qué significa el resultado, qué se puede
hacer o qué falta, según el contexto y las comprobaciones realizadas. No sustituir
la explicación pedida por un menú ni repetir la descripción general del plugin.
Indicar de forma breve qué estado se ha podido comprobar cuando afecte a la
respuesta y formular solo las preguntas que falten para avanzar.

Si se preguntan posibilidades o siguientes pasos, aplicar [los flujos y criterios de continuidad](../../docs/FLUJOS-DOCENTES.md).
Elegir entre una y tres opciones relevantes cuando proceda; explicar en cada una qué obtendrá el
profesor, qué entradas faltan y una petición que pueda usar.

| Estado observado | Orientación y ejemplo |
| --- | --- |
| Curso sin preparar | «Inicia mi proyecto docente». Se elegirán raíz, fuentes y exclusiones, respetando archivos e instrucciones. |
| Sin mapa comprobado | Recomendar «Crea el mapa docente con estas fuentes». Si la selección está pendiente, pedir las carpetas antes de proponer un corpus concreto. No crear el mapa al orientar. |
| Con mapa | «Consulta el mapa para localizar materiales de este tema», «Muéstrame el mapa» o «Actualízalo con estas fuentes autorizadas». Un índice existente no acredita que sus fuentes estén al día. |
| Con materiales | «Diseñemos una actividad para evaluar estos conocimientos» o «Crea bancos vinculados a estos materiales». Preguntar solo por objetivos, contexto o antecedentes que falten. |
| Con bancos validados | «Prepara modelos de cuestionario sobre estos temas». Por defecto serán cuatro, salvo una cantidad ya indicada. Se necesitan título, cobertura, cantidades, tipos y dificultad; revisar la procedencia antes de prometer equilibrio. |
| Con lote identificado | «Evalúa este lote con los criterios de la actividad». Requiere enunciado y entregables, rúbrica o criterios suficientes, entregas e identificación explícita. Para devolver notas, también una hoja Moodle y sus columnas. |
| Con detalle de resultados comprobado | «Añade feedback a estas calificaciones». Requiere detalle por pregunta, manifiesto y hoja Moodle. Una nota global no permite deducir dificultades conceptuales. |

Si ya hay una salida válida para el mismo objetivo y versión, ofrecer usarla,
revisarla o actualizarla. Ante un indicio incompleto, verificar el registro o
índice mínimo antes de afirmar que el proceso se ha realizado; un directorio o
nombre «final» no lo demuestra. No pedir de nuevo datos o decisiones conocidos.

Las tareas con adjuntos suficientes pueden comenzar aunque el curso no tenga
mapa; recomendarlo no lo convierte en requisito universal. Si el profesor ha
elegido expresamente trabajar sin fuentes, respetarlo y ofrecer tareas con
adjuntos, sin insistir en la creación del mapa.

Presentar también, cuando sean pertinentes, las tres ayudas complementarias:
**infografías y diapositivas visuales individuales**, **apuntes de estudio** y
**español claro inspirado en ASD-STE100**. No prometer presentaciones editables,
certificación del estándar ni imágenes o PDF cuando falten esas capacidades.

## Límites y continuidad

Esta orientación es de solo lectura y no requiere otra autorización para
consultarse ante una duda. Resolverla y retomar el flujo en curso si lo había;
una interrupción para pedir ayuda no cancela el encargo ni autoriza ampliarlo.

La orientación no cambia archivos, notas, selección de fuentes ni permisos y no
crea mapas, bancos o actividades. Esperar a que el profesor elija o formule un
encargo. Si ya lo ha hecho, pasar a la skill correspondiente sin pedir una
confirmación redundante. Reutilizar sus respuestas en el diálogo posterior.

Explicar solo los límites que afecten a la opción elegida: rúbrica completa y
soluciones reservadas al docente; evaluación basada en evidencias; importación
manual de archivos en Moodle; notas del cuestionario conservadas al añadir feedback.
Los nombres `docente/` y `alumnado/` organizan contenidos, no controlan accesos.

## Sugerir el siguiente paso

Cuando la respuesta requiera continuidad, aplicar el
[cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md) directamente,
sin volver a invocar esta skill. Terminar con la respuesta a la duda y, cuando
procedan, de una a tres opciones sustentadas y sus entradas pendientes. No
repetir un menú completo ni convertir una sugerencia en ejecución.
