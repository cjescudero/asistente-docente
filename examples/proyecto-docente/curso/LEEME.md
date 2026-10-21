# Mi proyecto docente

Trabaja con el agente en esta carpeta. Las instrucciones están en `AGENTS.md` y
la selección de fuentes se guarda en `_datos_internos_proyecto/proyecto-docente.json`.

| Carpeta | Uso |
| --- | --- |
| `_datos_internos_proyecto/` | Configuración e inventario técnico del curso. |
| `fuentes/teoria/` | Apuntes, diapositivas y referencias aportados. |
| `fuentes/actividades/` | Actividades aportadas, actuales o de otros cursos. |
| `fuentes/evaluaciones/cuestionarios/` | Cuestionarios aportados, identificando curso y vigencia. |
| `fuentes/evaluaciones/bancos/` | Bancos aportados; se enlazan sin copiarlos. |
| `materiales_generados/materiales/` | Apuntes, infografías y diapositivas visuales creados. |
| `materiales_generados/actividades/` | Una carpeta por actividad con documentos del alumnado y del docente separados. |
| `materiales_generados/bancos/` | Nuevos bancos y el catálogo que enlaza los bancos utilizables. |
| `materiales_generados/cuestionarios/` | Una carpeta por cuestionario, con modelos y archivos docentes separados. |
| `mapa-docente/` | Wiki, lector y grafo cuando se creen. |
| `resultados/` | Un lote por actividad y convocatoria: recibidos originales y corrección; siempre fuera de la wiki. |
| `archivo/` | Material apartado; solo se usa si se selecciona expresamente. |

Los materiales aportados permanecen en `fuentes/`. Cada producción nueva tiene
una carpeta estable en `materiales_generados/`, un registro `_datos_internos/material-docente.json` y un
`LEEME.md` que muestra su estado: **borrador**, **revisado** o
**listo para entregar**. Cambiar de estado no mueve los documentos.
Un documento creado puede alimentar otra tarea sin copiarlo a `fuentes/`.
Las rúbricas completas y soluciones quedan separadas de los documentos estudiantiles.
Seleccionar un material para la wiki no autoriza su entrega al alumnado.

## Qué hacer ahora

Puedes preguntar en cualquier momento «¿Qué puedo hacer?», «¿Y ahora?» o
«¿Para qué sirve este archivo?». El agente utilizará la ayuda contextual del
plugin, revisando la conversación y el estado pertinente del curso; no necesitas
conocer nombres de skills ni volver a explicar decisiones ya disponibles.

Pide **«¿Qué puedo hacer ahora con mi asignatura?»**. El agente consultará la
configuración, los índices y los resultados pertinentes para sugerir el siguiente
paso pendiente. No iniciará tareas por su cuenta ni leerá todo el curso.

El recorrido recomendado es **iniciar el proyecto → crear el mapa docente →
elegir un flujo de trabajo**. Pide «Crea el mapa con las fuentes que he elegido».
Si ya existe, puedes consultarlo, visualizarlo o pedir que se actualice.
Si aún no has elegido fuentes, el agente te ayudará a concretarlas. Si has
preferido trabajar sin fuentes, puedes usar adjuntos sin necesidad de crear el mapa.

| Flujo o petición | Entradas para avanzar |
| --- | --- |
| «Diseñemos una actividad» → «Evalúa las entregas» | Materiales, conocimientos y condiciones para diseñar; enunciado, criterios, entregas identificadas y hoja Moodle para corregir. |
| «Crea un banco» → «Prepara modelos impresos» | Materiales y objetivos para el banco; bancos válidos, cobertura, cantidad de preguntas, modelos y dificultad para el cuestionario. |
| «Prepara modelos» → «Genera observaciones sobre las calificaciones» | Resultados detallados por pregunta, manifiesto de los modelos y hoja Moodle; una nota global no permite inferir dificultades conceptuales. |
| «Prepara apuntes», «Crea diapositivas visuales» o «Haz una infografía» | Fuentes, propósito y destinatarios; las diapositivas son visuales individuales, no presentaciones editables. |

Para los cuestionarios, el punto de partida son cuatro modelos. El agente
propondrá cantidad de preguntas y tiempo aproximado según los conceptos y tipos
de respuesta; puedes ajustar ambas cosas. Las variantes no son conceptos nuevos.

Al finalizar cada tarea, el agente propondrá pasos adecuados a los resultados
comprobados. Si solo encuentra indicios, los señalará y verificará lo necesario;
una carpeta vacía no demuestra que una fase esté hecha. Si faltan entregas o
respuestas, explicará qué debes aportar antes de corregir o generar feedback.
Por defecto redactará en español claro, inspirado en ASD-STE100, salvo que indiques otra preferencia.

Las entregas y exportaciones originales de Moodle se guardan en
`resultados/<actividad>/<convocatoria>/recibidos/`; los informes, las copias de
calificaciones y el feedback se guardan en `correccion/` del mismo lote.
No se alteran las descargas originales ni se importan resultados automáticamente.
La rúbrica local no configura la calificación avanzada de Moodle.

La puesta en marcha deja la carpeta del mapa vacía. La wiki solo incorpora
materiales seleccionados; las producciones requieren un registro válido y estado
revisado o listo para entregar. Borradores, resultados y el propio mapa quedan fuera.

El catálogo de bancos se guarda en `materiales_generados/bancos/_datos_internos/`.
Cada cuestionario conserva selección, manifiesto y bancos congelados en su propia
carpeta `_datos_internos/`; consulta `LEEME.md` para abrir sus modelos.

Los nombres de las carpetas organizan los contenidos: no configuran permisos.
Una carpeta sincronizada con OneDrive o SharePoint sigue usando sus permisos y
su sincronización existentes. Comprueba que el agente haya leído `AGENTS.md`;
si su aplicación no lo carga, pídele expresamente que lo lea.
