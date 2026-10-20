# Mi proyecto docente

Trabaja con el agente en esta carpeta. Las instrucciones están en `AGENTS.md` y
la selección de fuentes se guarda en `proyecto-docente.json`.

| Carpeta | Uso |
| --- | --- |
| `alumnado/materiales/` | Materiales preparados para estudiantes. |
| `alumnado/actividades/` | Enunciados y actividades para estudiantes. |
| `alumnado/conocimientos/` | Dudas frecuentes y aclaraciones útiles. |
| `docente/fuentes/` | Fuentes de referencia elegidas por el profesor. |
| `docente/evaluaciones/` | Bancos, exámenes y criterios reservados. |
| `docente/soluciones/` | Soluciones y orientaciones del docente. |
| `docente/rubricas/` | Rúbricas de evaluación. |
| `docente/borradores/` | Nuevos materiales todavía en preparación. |
| `docente/mapa-docente/` | Wiki, lector y grafo cuando se creen. |
| `docente/resultados/` | Entregas, calificaciones y feedback; fuera de la wiki. |
| `docente/resultados/entregas/` | Un lote por actividad y convocatoria, con originales, identificación y corrección separados. |
| `archivo/` | Material apartado; solo se usa si se selecciona expresamente. |

## Qué hacer ahora

Pide **«¿Qué puedo hacer ahora con mi asignatura?»**. El agente consultará la
configuración y los índices disponibles para orientarte sin leer todo el curso
ni iniciar tareas por su cuenta.

El primer paso recomendado es **«Crea el mapa docente con las fuentes que he
elegido»**. Después puedes pedir «Consulta el mapa para localizar materiales de
este tema», «Muéstrame su grafo» o «Actualiza el mapa con los cambios autorizados».
Si aún no has elegido fuentes, el agente te ayudará a concretarlas.
Si has decidido trabajar sin fuentes, puedes usar adjuntos para cada encargo
sin necesidad de crear el mapa.

| Petición de ejemplo | Qué necesita el agente |
| --- | --- |
| «Diseñemos una actividad sobre estos conocimientos» | Materiales, nivel, objetivos y condiciones. El diálogo termina con enunciado, plantillas y rúbrica docente reservada. |
| «Crea un banco para estos apuntes y esta actividad» | Fuentes actuales; ejemplos anteriores opcionales para calibrar dificultad. |
| «Prepara dos modelos de examen sobre estos temas» | Bancos, cobertura, título, cantidad de preguntas y dificultad; PDF y GIFT ofuscado para importar manualmente en Moodle. |
| «Evalúa estas entregas con los criterios de la actividad» | Enunciado, rúbrica o criterios, entregas e identificación explícita, y hoja Moodle para devolver nota y feedback. |
| «Añade recomendaciones a estas calificaciones» | Detalle por pregunta, manifiesto del examen y hoja Moodle; se conservan las notas y se priorizan hasta tres dificultades. |
| «Prepara apuntes», «Haz una infografía» o «Aclara este texto» | Fuentes y destinatarios. Infografías o diapositivas visuales individuales, apuntes y español claro inspirado en ASD-STE100. |

Indica las fuentes y el destino cuando el encargo no los deje claros. El agente
preguntará únicamente por la información que falte. Los bancos se registran en
`docente/evaluaciones/bancos/` cuando se incorporen al catálogo. Las rúbricas
completas y soluciones permanecen en `docente/`; el enunciado comunica criterios
generales. La rúbrica local no configura la calificación avanzada de Moodle.

La puesta en marcha deja la carpeta del mapa vacía. Crear el Mapa docente es un
encargo posterior y explícito; las fuentes seleccionadas pueden revisarse antes.
No es necesario duplicar la wiki en las carpetas del alumnado.

Los nombres de las carpetas organizan los contenidos: no configuran permisos.
Una carpeta sincronizada con OneDrive o SharePoint sigue usando sus permisos y
su sincronización existentes. Comprueba que el agente haya leído `AGENTS.md`;
si su aplicación no lo carga, pídele expresamente que lo lea.
