# Catálogo y casos de aceptación

El plugin contiene doce skills. La selección puede ser automática por descripción
o explícita por nombre. No se necesita un enrutador que cargue todas las
instrucciones para cada petición. Los siguientes casos son una guía de evaluación del comportamiento
del agente; las pruebas Python no sustituyen su ejecución en el anfitrión.

| Skill | Petición representativa | Resultado esperado |
| --- | --- | --- |
| `iniciar-proyecto-docente` | Poner en marcha un proyecto con material docente. | Estructura de curso, configuración de fuentes, LEEME y AGENTS.md respetado; consulta ante conflictos, español claro y datos pendientes explícitos, sin iniciar el mapa. |
| `crear-mapa-docente` | Crear un Mapa docente de dos carpetas elegidas: materiales actuales y archivo de evaluaciones. | Índice, páginas Markdown y fuentes trazables; bloque en AGENTS.md para consultar desde el índice; originales intactos, acceso y lectura explícitos, lector y grafo cuando hay capacidades. |
| `consultar-mapa-docente` | Localizar material y criterios vigentes para diseñar una práctica y evaluarla. | Respuesta con evidencia original, distinción de histórico/vigente y contexto para el siguiente encargo; sin editar el mapa ni regenerar el grafo. |
| `visualizar-mapa-docente` | Regenerar el grafo docente y una vista para estudiantes. | HTML autónomos con arrastre, zoom, búsqueda, filtros y panel; la exportación estudiantil excluye datos reservados y sus dependencias transitivas, sin enlaces a archivos. |
| `preparar-actividades-docentes` | Crear un taller de análisis histórico con fuentes aportadas. | Enunciado autónomo y solución docente separados; objetivos y evidencias de aprendizaje. |
| `generar-apuntes-estudio` | Preparar apuntes de ecología para primer curso a partir de un capítulo. | Explicación sustentada, símbolos definidos y Markdown/PDF; sin inventar fuentes. |
| `evaluar-entregas` | Evaluar tres ensayos sintéticos con una rúbrica. | Justificación individual por criterio; sin imponer escala sobre diez ni penalizar uso supuesto de IA. |
| `crear-bancos-preguntas` | Generar preguntas de literatura con distractores razonados. | Banco GIFT válido con IDs y metadatos conceptuales, sin añadir hechos no sustentados. |
| `preparar-examenes-papel-moodle` | Crear dos modelos impresos de un banco. | PDFs, solucionarios, GIFT ofuscados, snapshot y manifiesto con idéntico orden. |
| `generar-feedback-evaluaciones` | Devolver comentarios conceptuales a partir de exportaciones. | CSV preservado, orientación sustentada y bloqueo de duplicados/ausencias ambiguas. |
| `redactar-espanol-claro` | Simplificar una explicación manteniendo todas sus condiciones. | Español natural y preciso, sin resumir ni declarar certificación STE. |
| `crear-infografias-didacticas` | Crear una diapositiva dibujada sobre una cadena causal. | Imagen revisada si hay generador; diseño y prompt claramente identificados si no lo hay. |

## Casos de aceptación de la puesta en marcha

- Proyecto nuevo sin mapa: crear el árbol `curso-v1`, configuración, LEEME y
  AGENTS.md con español claro. Preguntar por ubicación, tipos y selección de
  materiales que falten; dejar la carpeta del mapa vacía, sin proponer una wiki.
- Proyecto con instrucciones propias: modificar solo lo indicado, conservando
  texto y organización ajenos al encargo. Repetir sin duplicar reglas.
- Regla existente incompatible con la petición o el estilo predeterminado:
  explicar el conflicto y preguntar; no sobrescribir mientras falta la respuesta.
- Orígenes y tipos ya indicados: reutilizarlos sin volver a preguntar. Si solo
  falta el tipo de material, pedir únicamente ese dato.
- Redacción: registrar `redactar-espanol-claro` como opción predeterminada
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
entradas necesarias. Las equivalencias de nombres están en [migración](MIGRACION-0.7.md).

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
