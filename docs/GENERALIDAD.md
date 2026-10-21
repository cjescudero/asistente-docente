# Alcance para distintas materias

Revisión ampliada el 20 de octubre de 2026 para las doce skills de 0.9.0.

## Organización y continuidad (0.9.0)

Los originales se separan de los materiales creados, sin imponer contenidos de
una disciplina. Cada actividad reúne sus plantillas y documentos por audiencia;
los estados permiten distinguir trabajo en preparación y revisado sin cambiar
de ubicación. Un material creado puede alimentar otro encargo sin duplicarse.

Las skills proponen siguientes pasos según evidencias de resultados y necesidades
pendientes. Los flujos de actividades y de exámenes son independientes, con
apuntes y diapositivas visuales individuales como apoyos. El mapa es recomendable
pero no obligatorio para trabajar con adjuntos suficientes. Español claro es
el idioma y estilo predeterminado; una preferencia explícita del profesor prevalece.

## Orientación y evaluación conectadas (0.8.0)

Las actividades se diseñan por diálogo y pueden ser análisis de fuentes,
problemas, trabajos de campo o experimentos; código y notebooks son opciones,
no supuestos. Se parte del acceso del alumnado a IA y se piden evidencias de
comprensión, sin inventar obligación de uso ni sanciones. El registro vincula
versión, enunciado, plantillas y rúbrica completa reservada.

Los bancos enlazan materiales y actividades mediante identificadores,
localizadores, objetivos y dificultad estimada. Los exámenes históricos ayudan
a calibrar; no fijan el temario vigente. La composición aplica cuotas comunes,
semilla y trazabilidad entre banco, papel y Moodle. El feedback solo propone
materiales estudiantiles y prioriza dificultades según puntos y evidencias.

La orientación consulta índices y configuración sin exigir conocer nombres de
skills. Recomienda el mapa con las fuentes elegidas, sin crearlo automáticamente,
y permite tareas con adjuntos suficientes. El ejemplo de 0.8 combina
humanidades, ciencias y una actividad experimental con plantillas diferentes
de un notebook. Las comprobaciones de comportamiento y ejecución se distinguen
en [Validación](VALIDACION.md).

## Revisión base de 0.6 y 0.7
El plugin organiza procedimientos docentes; el contenido y los criterios de
validez proceden del encargo y de sus fuentes. No incluye una base universal
de conocimientos ni sustituye la revisión del profesor.

| Aspecto | Resultado de la revisión |
| --- | --- |
| Materia | TI aparece en la procedencia histórica, no como requisito de ejecución. |
| Nivel | Se elige en cada encargo. El ejemplo universitario es sintético. |
| Evaluación | Rúbrica y escala explícitas; también se admite análisis cualitativo provisional. No se presume escala 0–10. |
| Idioma | Apuntes y materiales siguen el idioma solicitado. Español claro se aplica a textos en español. |
| Identidad | Se usa el identificador acordado; no se exige una matrícula institucional. |
| Fuentes | Carpetas elegidas por el usuario; sin rutas personales ni corpus descubierto por defecto. |
| Herramientas | Notebooks opcionales. La wiki usa Markdown estándar. Moodle interviene solo en sus flujos. |
| Ejemplos | Humanidades y ciencias son demostraciones, no valores predeterminados. Hay una ficha vacía. |

## Adaptación a un encargo

Precisar la tarea, la audiencia y las fuentes. Incorporar objetivos, duración,
formato o rúbrica cuando afecten al resultado. No exigir todos esos campos para
una petición simple. Conservar la profundidad necesaria: una demostración,
un análisis literario, una interpretación musical o una práctica de laboratorio
pueden necesitar criterios distintos aunque utilicen la misma skill.

Ejemplos de uso sin convertirlos en pruebas realizadas:

- Historia en secundaria: comparar dos fuentes con evaluación cualitativa.
- Matemáticas universitarias: desarrollar una demostración con hipótesis explícitas.
- Formación profesional: preparar una práctica con criterios observables de ejecución.
- Música: elaborar una rúbrica de interpretación que admita alternativas válidas.

## Límites técnicos

La herramienta de bancos admite los tipos GIFT documentados; no convierte toda
forma de evaluación en un cuestionario. Imágenes, audio, interpretación de
partituras, demostraciones físicas o lectura de archivos especializados dependen
de las capacidades del anfitrión y de las fuentes accesibles. Enunciados GIFT con
contenido activo o formatos no soportados se diagnostican, no se eliminan.
Las instrucciones están escritas en español y los rótulos fijos de los exportadores
siguen en español; la CLI no ofrece todavía una localización completa.

La validación de generalidad combina revisión de instrucciones y ejemplos
sintéticos existentes; no acredita resultados pedagógicos en todas las disciplinas.
Los cambios concretos fueron condicionar español claro al idioma del encargo y
permitir identificadores acordados fuera de una institución. La fuente pública
incluye instrucciones de mantenimiento autocontenidas.

## Organización común desde 0.7.0

El árbol del curso organiza responsabilidades, no el contenido de una disciplina.
Asignatura, nivel, idioma, objetivos, escala y criterios siguen procediendo del
encargo. `proyecto-docente.json` guarda selección de fuentes y rutas; no impone un
temario. Los campos pedagógicos permanecen en la ficha opcional o la conversación.

Las tareas con texto o adjuntos suficientes siguen disponibles sin inicializar
un curso ni crear una wiki. La selección y las exclusiones se aplican cuando se
utiliza el corpus del proyecto. Véase [Proyecto docente](PROYECTO-DOCENTE.md).
