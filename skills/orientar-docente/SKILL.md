---
name: orientar-docente
description: Orientar al profesor sobre qué puede hacer con su curso y qué necesita para cada tarea. Usar ante «¿Qué puedo hacer ahora?», «Ayúdame con mi asignatura», dudas sobre el plugin o al ofrecer ayuda tras la inicialización. Consultar configuración e índices y proponer próximos pasos, sin iniciar automáticamente otros procesos.
---

# Orientar al docente

Dar una ayuda breve y adaptada al curso. El profesor no necesita conocer nombres
de skills ni leer manuales. Consultar el [catálogo](../../docs/CATALOGO.md) para
enrutar un encargo, y el [contrato del curso](../../docs/PROYECTO-DOCENTE.md) para
interpretar sus carpetas.

## Reconocer el estado sin leerlo todo

1. Identificar la raíz y leer las instrucciones aplicables. Consultar
   `proyecto-docente.json` si existe. Si no se conoce la raíz, preguntar por ella
   y ofrecer una orientación general con la información de la conversación.
2. Revisar solo los índices y registros necesarios: índice del mapa registrado,
   catálogo en `docente/evaluaciones/bancos/`, registros de actividades y nombres
   de lotes en `docente/resultados/entregas/`. No leer entregas ni calificaciones
   para dar una orientación inicial. La mera presencia de archivos no demuestra
   que estén revisados, actualizados, accesibles o completos.
3. Distinguir lo comprobado, lo pendiente y lo desconocido. Respetar la selección
   y las exclusiones, también mediante enlaces. No ampliar el corpus ni escanear
   todo el curso para suplir información ausente.

## Proponer un siguiente paso

Elegir hasta tres opciones relevantes; explicar en cada una qué obtendrá el
profesor, qué entradas faltan y una petición que pueda usar.

| Estado observado | Orientación y ejemplo |
| --- | --- |
| Curso sin preparar | «Inicia mi proyecto docente». Se elegirán raíz, fuentes y exclusiones, respetando archivos e instrucciones. |
| Sin mapa | Recomendar «Crea el mapa docente con estas fuentes». Si la selección está pendiente, pedir las carpetas antes de proponer un corpus concreto. No crear el mapa al orientar. |
| Con mapa | «Consulta el mapa para localizar materiales de este tema», «Muéstrame el mapa» o «Actualízalo con estas fuentes autorizadas». Un índice existente no acredita que sus fuentes estén al día. |
| Con materiales | «Diseñemos una actividad para evaluar estos conocimientos» o «Crea bancos vinculados a estos materiales». Preguntar solo por objetivos, contexto o antecedentes que falten. |
| Con bancos | «Prepara dos modelos de examen sobre estos temas». Se necesitan título, cobertura, cantidades, tipos y dificultad; revisar la procedencia antes de prometer equilibrio. |
| Con entregas | «Evalúa este lote con los criterios de la actividad». Requiere enunciado y entregables, rúbrica o criterios suficientes, entregas e identificación explícita. Para devolver notas, también una hoja Moodle y sus columnas. |
| Con resultados de examen | «Añade feedback a estas calificaciones». Requiere detalle por pregunta, manifiesto y hoja Moodle. Una nota global no permite deducir dificultades conceptuales. |

Las tareas con adjuntos suficientes pueden comenzar aunque el curso no tenga
mapa; recomendarlo no lo convierte en requisito universal. Si el profesor ha
elegido expresamente trabajar sin fuentes, respetarlo y ofrecer tareas con
adjuntos, sin insistir en la creación del mapa.

Presentar también, cuando sean pertinentes, las tres ayudas complementarias:
**infografías y diapositivas visuales individuales**, **apuntes de estudio** y
**español claro inspirado en ASD-STE100**. No prometer presentaciones editables,
certificación del estándar ni imágenes o PDF cuando falten esas capacidades.

## Límites y continuidad

La orientación no cambia archivos, notas, selección de fuentes ni permisos y no
crea mapas, bancos o actividades. Esperar a que el profesor elija o formule un
encargo. Si ya lo ha hecho, pasar a la skill correspondiente sin pedir una
confirmación redundante. Reutilizar sus respuestas en el diálogo posterior.

Explicar solo los límites que afecten a la opción elegida: rúbrica completa y
soluciones reservadas al docente; evaluación basada en evidencias; importación
manual de archivos en Moodle; notas del examen conservadas al añadir feedback.
Los nombres `docente/` y `alumnado/` organizan contenidos, no controlan accesos.
