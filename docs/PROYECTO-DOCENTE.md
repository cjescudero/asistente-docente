# Cómo organizar una asignatura

Abre la carpeta del curso y pide **«Inicia mi proyecto docente»** o **«Adapta mi curso conservando mis carpetas»**. Indica dónde trabajas, qué carpetas contienen material de referencia y dónde recibes las entregas. Puedes asignar varias carpetas existentes a un mismo uso. Se mantienen los nombres y la organización que ya utilizas.

| Espacio | Qué se guarda |
| --- | --- |
| Material de la asignatura | Material aportado por el docente y documentos incorporados expresamente como referencia del curso. |
| Material generado por IA | Apuntes, actividades, bancos, cuestionarios, propuestas y wiki producidos durante el trabajo. |
| Entregas | Originales del alumnado y hojas Moodle en `<actividad>/<convocatoria>/recibidos/`, calificaciones y comentarios privados en `correccion/`. |
| Notas del curso (opcional) | Ideas de clase o de examen, notas de planificación y borradores que el profesor quiere guardar y editar. |
| Archivos de gestión del proyecto | Configuración, catálogo, historial y estado de actualización. Al iniciar un curso nuevo se crea oculta en macOS y Windows. La configuración y el catálogo se guardan cuando hacen falta. |

En un curso vacío se crean los tres primeros espacios, la carpeta de gestión y `AGENTS.md`. En un curso existente, se pueden asignar por ejemplo «Temas» y «Laboratorio» al primero y «Producción» al segundo. Las raíces deben ser carpetas independientes dentro del curso. Los archivos sueltos en la raíz conservan su ubicación. Si deben quedar dentro de un espacio, el agente propone una carpeta raíz que los abarque o un traslado que el docente pueda aprobar. Los espacios definen el destino y el tratamiento de los archivos. Los permisos siguen correspondiendo al sistema de almacenamiento. El agente conserva las instrucciones del profesor y consulta los conflictos antes de modificarlas. `.agents/` solo se necesita si el curso utiliza recursos específicos.

En la estructura propuesta, «Alumnado» y «Salidas de campo» son carpetas de uso docente reservado situadas directamente en `02 Organización del curso/`. «Alumnado» reúne listados, informes de la oficina de apoyo a la diversidad (ADI) y documentación similar sobre las circunstancias del alumnado. Ambas carpetas quedan fuera de las fuentes del Mapa docente.

## Guardar ideas y borradores del profesor

Puedes pedir **«Añade un espacio para mis notas del curso»** o **«Usa mi carpeta Cuaderno docente para mis ideas»**, tanto al empezar como en un curso ya configurado. El nombre sugerido es `Notas del curso`. Elige una carpeta independiente dentro del proyecto. Si ya existe, conserva sus archivos y subcarpetas. Una pregunta como «¿Dónde guardo mis ideas de examen?» sirve para conocer las opciones antes de elegir.

Puedes editar las notas con tus herramientas habituales. Si te ayuda, pide «Propón cómo agrupar mis notas por tema, ideas de cuestionario y planificación». El agente puede sugerir esa agrupación manteniendo los archivos en su sitio. El catálogo de materiales, el Mapa docente y las vistas para el alumnado excluyen este espacio. El acceso efectivo a la carpeta depende de los permisos del disco o del servicio donde la guardes.

Cuando una idea esté lista, concreta qué quieres incorporar. Por ejemplo: «Incorpora la nota sobre el debate del tema 2 a mi carpeta de actividades». El agente revisa contigo el contenido, el destino y quién podrá verlo. Tras la decisión expresa, incorpora únicamente el documento acordado, comprueba posibles colisiones y registra la nueva fuente. La selección para la wiki y la entrega al alumnado requieren sus propias decisiones.

## Clasificar sin mover los originales

El catálogo distingue **identidad, versión, ubicación, procedencia, acceso, clasificación y estado**. Se inspecciona primero la agrupación del profesor. Una práctica con enunciado, cuaderno y datos puede clasificarse como unidad. En una carpeta mixta se conserva el tema común y se clasifican sus componentes. Las categorías principales y secundarias son Organización, Teoría, Práctica, Actividades y proyectos, Evaluaciones, Recursos, y Soluciones y feedback. Las entregas se mantienen fuera del catálogo y del mapa.

Un material puede recibir una clasificación directa, heredarla de su agrupación lógica o quedar pendiente. Una confirmación docente prevalece sobre las inferencias. El nombre, la extensión y las fechas ayudan a localizar pistas. Para clasificar o declarar un contenido revisado se necesitan evidencias. Pedir «Agrupa lógicamente estas lecturas bajo el tema de la memoria» cambia su relación en el catálogo y conserva su ubicación física.

## Elegir cómo organizar las carpetas

La opción inicial es mantener el árbol existente. También puedes pedir que se preparen las siete carpetas de categorías vacías o una reorganización completa. El agente explica las unidades que se conservan, carpetas y archivos afectados, destinos, excepciones, colisiones y dudas. Los detalles quedan en el plan de gestión. Puedes pedir «Acepto los movimientos de Laboratorio, salvo los del tema 3», cambiar un destino o rechazar la propuesta. Solo se ejecutan las operaciones identificadas en la aceptación. Si la identidad o el contenido han cambiado, se revisa la operación afectada.

Para **consolidar** un documento generado, pide por ejemplo «Incorpora esta guía revisada a mi carpeta de teoría». El agente muestra el destino y conserva el identificador, la procedencia IA y las relaciones. Seleccionar una fuente para la wiki, consolidar su contenido y conceder acceso al alumnado son decisiones independientes.

## Trabajar con una wiki actualizada

Elige las carpetas y exclusiones para la wiki, incluso si has catalogado un espacio mayor. El mapa y las entregas quedan fuera del corpus. Una fuente nueva seleccionada, incluida una consolidación, queda pendiente de lectura. Ante un cambio de contenido, el agente relee la versión afectada, los localizadores y las páginas que dependían de ella, revisa sus síntesis y vuelve a validar el mapa. Ante un traslado reconocido conserva la versión y repara enlaces. Para índices adicionales, cada fragmento debe apuntar al par `material_id` y `content_version`. Esta distribución gestiona la wiki, su lector y grafo. No incluye un motor vectorial.

## Configuración y utilidades

Los siguientes comandos son para el agente. El profesor puede pedir las operaciones en lenguaje natural. Ejecutarlos con el Python del plugin y rutas explícitas. Una inicialización mínima con selección aplazada se reconoce por el bloque del curso en `AGENTS.md`. Las asignaciones personalizadas y la selección se guardan en `Archivos de gestión del proyecto/proyecto-docente.json`. En cursos existentes se reutiliza también `Gestión del proyecto/` y se conserva la visibilidad elegida. Se admite una sola carpeta de gestión por curso, incluso oculta en Finder. Los espacios pueden llamarse `01 Material docente`, `03 Material generado por IA`, `04 Entregas` y `05 Anotaciones durante el curso`. La selección explícita determina qué ramas alimentan el mapa. Organización, datos reservados, referencias y archivo se mantienen fuera de esa selección. Las rutas de configuración se interpretan desde la raíz del curso.

```sh
python scripts/docencia.py init-project "/ruta/curso" --dry-run
python scripts/docencia.py init-project "/ruta/curso" --spaces espacios.json --include "Temas"
python scripts/docencia.py check-project "/ruta/curso"
python scripts/docencia.py catalog-sync "/ruta/curso"
python scripts/docencia.py catalog-show "/ruta/curso"
python scripts/docencia.py catalog-classify "/ruta/curso" UUID "Práctica" --evidence "Guion de laboratorio confirmado por el docente"
python scripts/docencia.py organize-plan "/ruta/curso" --mode moves --moves movimientos.json
python scripts/docencia.py organize-apply "/ruta/curso" ID_PLAN --operation ID_OPERACION
```

Un curso con tres espacios conserva su configuración al actualizar el plugin. Cuando el profesor pida habilitar notas, usa `init-project "/ruta/curso" --notes` para el nombre recomendado o `init-project "/ruta/curso" --notes "Cuaderno docente"` para una carpeta elegida. En una asignación completa con `--spaces`, la clave opcional `"notes": ["Cuaderno docente"]` identifica las raíces editoriales del profesor. Cada raíz debe quedar separada de las fuentes, la producción, las entregas y la gestión. Si ya existe un `AGENTS.md`, consulta la propuesta para incorporar la nueva regla y conserva las instrucciones propias del profesor.

`espacios.json` contiene por ejemplo `{"sources":["Temas","Laboratorio"],"generated":["Producción"],"submissions":["Trabajos recibidos"]}`. Cada entrada de la lista en `movimientos.json` contiene `material_id` y `destination` desde la raíz. Para categorías vacías usa `--mode categories --directory "Temas"`. Para consolidar una producción de IA ya catalogada usa `--mode promote`. Para cambiar destinos al aplicar usa `--changes` con un objeto de identificadores de operación y rutas. Un plan interrumpido se reanuda con el mismo identificador y la selección autorizada.

`catalogo_materiales.json` conserva UUID, padre físico, agrupación lógica, clasificación, procedencia y versión. `historial_operaciones.jsonl` registra decisiones y cambios. La reconciliación ligera compara los metadatos, conserva los registros desaparecidos e identifica los casos ambiguos. Pedir al profesor que resuelva duplicados antes de vincularlos (`catalog-resolve`). La selección conserva las identidades de carpetas incluidas y elementos excluidos que se hayan podido reconocer. Si una exclusión desaparece y no se puede localizar con seguridad, el agente pide aclarar el ámbito antes de aceptar nuevas fuentes. Un nuevo acuerdo permite sustituir la lista de exclusiones y `--no-exclusions` permite retirarlas expresamente. Para reconocer un traslado, el archivo debe haber sido observado al menos una vez. Un archivo creado y movido entre dos observaciones puede necesitar identificación por parte del docente. Los traslados automáticos usan un renombrado sin sobrescritura dentro del mismo volumen. Entre volúmenes el docente puede trasladar la unidad y pedir reconciliación. El catálogo registra evidencia de inventario. La lectura y sus localizadores figuran en el registro de la wiki. Consultar el catálogo y los índices pertinentes antes de repetir trabajo.

Una instalación anterior con un curso `curso-v3` puede conservar su organización o solicitar una adopción. El agente muestra las correspondencias, fuentes y dudas. Solo tras la aceptación aplica `init-project --adopt-v3` y reconcilia las raíces acordadas. Se conserva la configuración anterior y los cuestionarios utilizados. La adopción se puede probar en una copia.

## Rutas de cuestionarios

Elige la raíz de producción asignada y reúne en un solo conjunto el LEEME, los modelos del alumnado, los solucionarios y GIFT docentes, la selección, el manifiesto y los bancos congelados. Al construir modelos usa `--layout curso-v4`. Las rutas internas del manifiesto y los archivos congelados conservan las correspondencias con el papel y Moodle.

## Trabajo paralelo y elección de modelos

El `AGENTS.md` generado incorpora esta política local del curso:

- Usar subagentes cuando el anfitrión lo permita y haya subtareas independientes
  cuya paralelización aporte una ventaja: por ejemplo, evaluar entregas distintas
  o preparar feedback de estudiantes distintos. No fragmentar tareas pequeñas
  ni delegar dependencias que todavía no estén resueltas.
- El agente principal fija criterios comunes y asigna a cada subagente un alcance,
  entradas mínimas, salida propia y comprobaciones. Evitar que varios agentes
  escriban el mismo archivo o reciban datos de otros estudiantes sin necesidad.
  El principal integra y revisa evidencias, cálculos, coherencia de criterios e
  identificadores; solo él consolida la hoja Moodle. Mantener revisión docente.
- Si una subtarea permite un modelo más sencillo y potencialmente más económico,
  preguntar al docente antes de cambiarlo: indicar tarea, modelo disponible,
  motivo y límites. No prometer ahorro ni precios no comprobados. Esperar una
  respuesta explícita; el silencio no autoriza el cambio. Reutilizar una elección
  ya autorizada para el mismo alcance y no preguntar por cada estudiante.
  Sin autorización, conservar el modelo actual o heredado. Solo ofrecer modelos
  que el anfitrión permita seleccionar; si no permite subagentes o elegir modelo,
  explicar la limitación y continuar con las capacidades disponibles, sin simularlo.

La inicialización propone incorporar estas reglas a un archivo existente, sin
sobrescribir sus instrucciones ni resolver conflictos automáticamente. Esta
política no configura modelos ni crea subagentes durante la puesta en marcha.

Ejemplo de consulta: «Puedo repartir el feedback de este lote entre subagentes.
Para redactar los borradores, el modelo disponible X parece suficiente porque
los criterios y las evidencias ya están fijados. ¿Quieres usarlo para este lote
o mantener el modelo actual? Revisaré el conjunto antes de consolidar el CSV».
Sustituir X por una opción realmente disponible; no usar un modelo menos capaz
para resolver por defecto criterios ambiguos o evidencias contradictorias.


## Ayuda contextual durante el trabajo

Pide «¿Qué puedo hacer ahora?». El agente consulta las decisiones anteriores y los índices pertinentes. Puede recomendar crear o consultar el mapa, preparar una actividad, corregir entregas, elaborar bancos y modelos o generar feedback. Las instrucciones de inicio no crean la wiki automáticamente. Puedes pedir español conciso o inglés técnico claro para la prosa de cualquiera de estos encargos. [Idiomas y estilos](LANGUAGES.md).

[Ejemplo con carpetas propias](../examples/curso-v4/README.md) · [Flujos docentes](FLUJOS-DOCENTES.md) · [Mapa docente](MAPA-DOCENTE.md).
