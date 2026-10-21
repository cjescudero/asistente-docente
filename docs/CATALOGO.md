# Catálogo y casos de aceptación

El plugin contiene doce skills. La selección puede ser automática por descripción
o explícita por nombre. No se necesita un enrutador que cargue todas las
instrucciones para cada petición. Los siguientes casos son una guía de evaluación del comportamiento
del agente; las pruebas Python no sustituyen su ejecución en el anfitrión.

| Skill | Petición representativa | Resultado esperado |
| --- | --- | --- |
| `proyecto-docente-inicializacion-adaptacion` | Poner en marcha un proyecto con material docente. | Estructura de curso, configuración de fuentes, LEEME y AGENTS.md respetado; consulta ante conflictos, español claro, orientación y recomendación del mapa, sin crearlo automáticamente. |
| `proyecto-docente-ayuda` | ¿Qué puedo hacer ahora con mi asignatura? | Opciones según el estado del curso, ejemplos de peticiones y entradas que faltan; sin leer todo el corpus ni iniciar procesos por su cuenta. |
| `mapa-docente-creacion-visualizacion` | Crear un Mapa docente de dos carpetas elegidas: materiales actuales y archivo de evaluaciones. | Índice, páginas Markdown y fuentes trazables; bloque en AGENTS.md para consultar desde el índice; originales intactos, acceso y lectura explícitos, lector y grafo cuando hay capacidades. |
| `mapa-docente-consulta` | Localizar material y criterios vigentes para diseñar una práctica y evaluarla. | Respuesta con evidencia original, distinción de histórico/vigente y contexto para el siguiente encargo; sin editar el mapa ni regenerar el grafo. |
| `mapa-docente-creacion-visualizacion` | Regenerar el grafo docente y una vista para estudiantes. | HTML autónomos con arrastre, zoom, búsqueda, filtros y panel; la exportación estudiantil excluye datos reservados y sus dependencias transitivas, sin enlaces a archivos. |
| `actividades-preparacion` | Ayúdame a diseñar un taller de análisis histórico con estas fuentes. | Diálogo sobre conocimientos, materiales, ejemplos previos y uso de IA; enunciado, plantillas y rúbrica docente de la misma versión, con guía cuando corresponda. |
| `apuntes-estudio-creacion` | Preparar apuntes de ecología para primer curso a partir de un capítulo. | Explicación sustentada, símbolos definidos y Markdown/PDF; sin inventar fuentes. |
| `actividades-evaluacion` | Corregir ensayos descargados de Moodle con su enunciado y rúbrica. | Evidencia y puntuación por criterio, CSV de notas y feedback sobre copia, trazabilidad de cambios y casos pendientes; sin sancionar supuesto uso de IA. |
| `cuestionarios-bancos-preguntas-creacion` | Crear preguntas de estos apuntes y de una actividad de literatura. | Bancos GIFT, procedencia, localizadores, conceptos, objetivos, dificultad y repaso en catálogo; inspiración histórica diferenciada del contenido vigente. |
| `cuestionarios-modelos-imprimir-evaluar` | Combinar preguntas de dos temas y una práctica para tres modelos. | Reparto de cobertura acordado, modelos comparables y reproducibles, PDF, solucionarios, GIFT ofuscados, bancos congelados e informe de reutilización. |
| `cuestionarios-observaciones-calificaciones-alumnado` | Añadir comentarios al libro de calificaciones a partir del detalle del examen. | Hasta tres dificultades sustentadas y recomendaciones accesibles; notas preservadas y bloqueo de correspondencias ambiguas. |
| `espanol-conciso-redaccion` | Simplificar una explicación manteniendo todas sus condiciones. | Español natural y preciso, sin resumir ni declarar certificación STE. |
| `infografias-didacticas-creacion` | Crear una diapositiva dibujada sobre una cadena causal. | Imagen revisada si hay generador; diseño y prompt claramente identificados si no lo hay. |

## Nombres visibles

Los identificadores y nombres visibles comienzan por su categoría. La interfaz
se declara en `agents/openai.yaml`; el orden y su presentación dependen del anfitrión.

| Nombre visible | Identificador |
| --- | --- |
| Actividades: evaluación | `actividades-evaluacion` |
| Actividades: preparación | `actividades-preparacion` |
| Apuntes estudio: creación | `apuntes-estudio-creacion` |
| Cuestionarios: creación de bancos de preguntas | `cuestionarios-bancos-preguntas-creacion` |
| Español conciso: redacción | `espanol-conciso-redaccion` |
| Cuestionarios: observaciones sobre calificaciones para el alumnado | `cuestionarios-observaciones-calificaciones-alumnado` |
| Cuestionarios: creación de modelos para imprimir y evaluar | `cuestionarios-modelos-imprimir-evaluar` |
| Infografías didácticas: creación | `infografias-didacticas-creacion` |
| Mapa docente: consulta | `mapa-docente-consulta` |
| Mapa docente: creación y visualización | `mapa-docente-creacion-visualizacion` |
| Proyecto docente: ayuda | `proyecto-docente-ayuda` |
| Proyecto docente: inicialización y adaptación | `proyecto-docente-inicializacion-adaptacion` |

## Casos de aceptación de la puesta en marcha

- Proyecto nuevo sin mapa: crear el árbol `curso-v2`, configuración, LEEME y
  AGENTS.md con español claro. Preguntar por ubicación, tipos y selección de
  materiales que falten; dejar la carpeta del mapa vacía, recomendar su creación
  y ofrecer orientación. Crear el mapa requiere un encargo del profesor.
- Curso anterior: conservar su estructura hasta una migración concreta aprobada.
  Distinguir originales y documentos creados sin inferir procedencia por su carpeta.
- Cierre: seguir los [flujos docentes](FLUJOS-DOCENTES.md), comprobar indicios
  de resultados y proponer el siguiente paso pendiente sin ejecutarlo. Ofrecer
  apuntes y diapositivas visuales individuales; español claro salvo otra preferencia.
- Proyecto con instrucciones propias: modificar solo lo indicado, conservando
  texto y organización ajenos al encargo. Repetir sin duplicar reglas.
- Regla existente incompatible con la petición o el estilo predeterminado:
  explicar el conflicto y preguntar; no sobrescribir mientras falta la respuesta.
- Orígenes y tipos ya indicados: reutilizarlos sin volver a preguntar. Si solo
  falta el tipo de material, pedir únicamente ese dato.
- Redacción: registrar `espanol-conciso-redaccion` como opción predeterminada
  del proyecto, sin cambiar su activación global ni inventar su disponibilidad.
- Proyecto con un bloque de consulta del mapa: conservarlo sin reemplazarlo ni
  regenerar la documentación.

- Selección aplazada: guardar `selected: false` y listas vacías; no interpretar
  la ausencia de selección como permiso para recorrer el curso.
- Entradas: distinguir carpeta inexistente, vacía, sin archivos seleccionados y
  no accesible. Resolver una corrección con texto suficiente aunque estén vacías.
- Migración: informar movimientos, colisiones y enlaces sin aplicar cambios;
  esperar aprobación de la propuesta antes de mover originales.

El [contrato común](PROYECTO-DOCENTE.md) se aplica a las doce skills según las
entradas necesarias. Las equivalencias están en [migración a 0.10](MIGRACION-0.10.md) y [migración a 0.9](MIGRACION-0.9.md).

## Casos de aceptación de orientación, actividades y evaluación

- Curso recién iniciado: recomendar el mapa, explicar cómo pedirlo y ofrecer
  ayuda. No leer originales, crear páginas ni ejecutar otra skill solo porque
  el usuario pregunte qué puede hacer.
- Curso con mapa y bancos: consultar configuración e índices relevantes y
  ofrecer preparar evaluaciones a partir de los materiales asociados. Si falta
  una fuente, explicar la carencia sin buscar en carpetas vecinas.
- Taller de historia con dos fuentes y un ejemplo antiguo: preguntar por nivel
  y objetivos pendientes, distinguir material vigente de inspiración y proponer
  evidencias de comparación. Entregar ficha, enunciado y rúbrica reservada; no
  convertirlo en una tarea de programación.
- Actividad de ciencias experimentales: acordar recursos y observaciones que se
  recogerán; preparar registro de mediciones y rúbrica. Comprobar que no aparecen
  datos inventados como resultados realizados y que hay alternativas válidas.
- Uso de IA sin política indicada: proponer evidencias de decisiones y contraste
  y preguntar las condiciones relevantes. No imponer prohibiciones, sanciones
  ni uso obligatorio.
- Banco de diapositivas y banco de una actividad: cada pregunta conserva sus
  fuentes y localizadores; una pregunta con varias fuentes no se reduce a una
  asociación inventada. El histórico calibra dificultad sin ampliar el temario.
- Dos bancos con el mismo título GIFT: conservar ambas identidades mediante el
  banco de origen; detectar duplicados dentro de cada banco.
- Fondo insuficiente para un reparto: informar la cuota que no puede cubrirse,
  ofrecer ajuste o ampliación de bancos y no producir un examen con cobertura
  distinta sin que el profesor lo acuerde.
- Varios modelos: mismos cupos de contenido y dificultad, ausencia de repetición
  dentro de un modelo y reutilización documentada entre ellos. Comparar cada
  opción y cada pregunta entre PDF, GIFT y manifiesto, incluido verdadero/falso.
- Entrega grupal: requerir miembros e identificadores explícitos y la política de
  nota común o individual. Un nombre parecido o una carpeta no constituye una
  correspondencia.
- Hoja Moodle de tarea y libro de calificaciones: conservar filas y columnas
  ajenas, registrar cambios y detectar IDs duplicados. Un caso ilegible o ausente
  queda pendiente; no se convierte en cero.
- Feedback de un concepto con dos fallos y otro con un fallo aislado: ordenar por
  proporción perdida y evidencia, distinguir dificultad acusada de aspecto a
  revisar y limitar a tres prioridades. Solo recomendar fuentes autorizadas para
  el alumnado; conservar las notas calculadas por Moodle.
- Exportación con una nota global únicamente: explicar que falta el detalle
  para atribuir dificultades conceptuales. No reconstruir respuestas ni temas
  fallados a partir de esa nota.

## Casos de aceptación del Mapa docente

- Crear el mapa sin haber ejecutado la puesta en marcha: escribir el bloque de
  consulta en el `AGENTS.md` de la raíz del proyecto, con rutas válidas desde él.
  Si no se conoce esa raíz, solicitarla sin inferirla desde los ancestros.
- Proyecto con instrucciones y bloque de la versión 0.5.0: actualizar ese bloque
  conservando lo ajeno al mapa; repetir la creación o actualización sin duplicarlo.
- Consulta con enlaces encadenados y un ciclo: partir del índice, recorrer solo
  las ramas útiles, llegar al original necesario y detenerse sin releer el ciclo
  ni todo el corpus.
- Una página parcial o antigua no basta para calificar: comprobar la rúbrica
  original vigente o identificar la ausencia de criterio aplicable.
- Elegir dos raíces con nombres distintos de los del ejemplo. Crear el registro
  versión 2 y abrir originales mediante rutas relativas sin moverlos.
- Excluir una fuente ya registrada: identificar dependencias directas e
  indirectas, no reutilizar síntesis afectadas antes de revisarlas y bloquear
  derivados mientras no se supere la validación. Un enlace no readmite la fuente.
- Cambiar una fuente después de registrarla. Detectar la huella distinta,
  revisar los contenidos afectados y actualizar el mapa y su grafo; no conservar
  una síntesis como actual sin volver a comprobarla.
- Abrir las páginas en un lector Markdown común. Comprobar enlaces normales,
  sin wikilinks, frontmatter obligatorio ni dependencia de Notion u Obsidian.
- Revisar un concepto, una presentación, una práctica y un taller. Separar tipo
  documental, acceso y vigencia, sin convertir un examen antiguo en criterio actual.
- Usar el grafo sin red: arrastrar nodos, ampliar, buscar, filtrar y leer el panel.
  La vista docente oculta evaluaciones al inicio pero permite mostrarlas y abrir
  sus páginas; ocultación no equivale a eliminación.
- Inspeccionar el HTML estudiantil y sus datos incrustados. No deben aparecer
  fuentes reservadas, páginas dependientes de ellas ni enlaces salientes a archivos.
  Verificar también un caso de dependencia indirecta entre varias páginas.
- Consultar el mapa y comparar después sus archivos: no debe haber cambios en
  páginas, registro, incidencias, log ni grafo.

## Casos negativos

- No activar Mapa docente para resumir un capítulo como apuntes del estudiante.
- No descubrir raíces automáticamente, ampliar a carpetas vecinas ni copiar
  originales para resolver una limitación de rutas sin un encargo que lo autorice.
- No declarar leído un archivo solo por inventariarlo ni usar su resumen tras
  detectar una huella cambiada sin volver a la fuente.
- No usar soluciones reservadas en materiales del estudiante ni presentar
  material histórico como temario o rúbrica vigente.
- No guardar consultas, mover fuentes o crear instrucciones del anfitrión sin
  un encargo que autorice esas acciones.
- No presentar un filtro como control de acceso ni entregar el HTML docente
  filtrado como exportación para estudiantes.
- No activar corrección de entregas para fabricar una rúbrica sin entregas.
- No usar feedback posterior para reconstruir modelos sin manifiesto.
- No activar infografías para una mera corrección ortográfica.
- No resolver una importación Moodle incompleta atribuyendo ceros a datos ausentes.
- No declarar PDF, imagen, vídeo o instalación verificados cuando solo exista una
  fuente, un prompt, código o un manifiesto válido.

Las habilidades de mantenimiento del proyecto original se sustituyen por las
comprobaciones del paquete; sus alias no duplican skills públicas.

## Revisión de organización y aprobación (0.9.0)

Casos de aceptación para el agente, no un clasificador por nombres ni pruebas
reales de interfaz. La utilidad de migración prepara propuestas sin aplicarlas.

| Caso | Conducta que debe verificarse |
| --- | --- |
| Carpeta vacía | Confirmar que no hay errores de acceso, preparar estructura sin inventariar lecturas ficticias. |
| Carpeta mezclada con teoría, exámenes y entregas | Inventariar antes de crear; inspeccionar lo necesario, separar resultados y proponer tabla y árbol. |
| `final-2025.pdf` contiene una actividad vigente | El nombre es pista; preguntar procedencia, estado y audiencia que el contenido no acredite. |
| Archivo ilegible | Marcar pendiente, pedir aclaración y no incluir su traslado entre los movimientos ejecutables. |
| Aprobación completa | Aplicar solo la tabla acordada tras comprobar colisiones, enlaces y huellas. |
| Aprobación parcial | Mover solo lo seleccionado; presentar dependencias adicionales antes de intervenirlas. |
| Rechazo | Mantener ubicaciones; continuar ajustes compatibles sin imponer otro árbol. |
| Dos archivos con mismo destino | Detener esos movimientos y pedir una resolución, sin sobrescribir ni renombrar silenciosamente. |
| Examen usado con manifiesto y snapshot | Conservar el conjunto, versiones, pesos y correspondencias; revisar rutas sin sustituciones globales. |
| Curso configurado con AGENTS propio | Respetar v1/v2, consultar conflictos y repetir sin duplicar reglas ni movimientos. |

## Preguntas, modelos y wiki explicativa (0.10.0)

- Banco: proponer cantidad de principales según conceptos y objetivos, explicar
  el reparto, ofrecer cuatro variantes equivalentes como punto de partida y
  distinguir principales de ítems GIFT. Si el profesor cambia la cantidad,
  ajustar cobertura y señalar lagunas sin inventar contenidos.
- Modelos: cuatro por defecto; propuesta razonada de preguntas y duración
  estimada, ajustable a la duración disponible. No iniciar la generación con
  cinco preguntas silenciosamente ni contar variantes como conceptos nuevos.
- Diversidad: con familias suficientes, principales distintas entre modelos;
  con familias escasas, variantes distintas y reutilización documentada. Nunca
  dos variantes de la misma principal dentro de un modelo.
- Wiki: el lector puede explicar qué es la media, cómo se aplica, qué información
  pierde y sus límites a partir de la página del ejemplo. Solo abre el original
  para profundizar o verificar; no se declara cubierta la incertidumbre formal.
- Consulta: se conserva solo lectura y no convierte una explicación docente con
  fuentes reservadas en apuntes del alumnado ni reescribe una wiki esquemática
  al mostrar su HTML.
