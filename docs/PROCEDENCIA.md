# Procedencia y adaptación

Asistente docente adapta flujos aportados por el propietario para usarlos en distintas asignaturas y en más de un anfitrión. Las skills originales permanecen independientes y no se modifican. Esta documentación distingue procedencia, decisiones de adaptación y dependencias incorporadas.

## Diez skills del proyecto de talleres de TI

La fuente de referencia es la carpeta exportada `.agents/skills` del proyecto de talleres de Teoría de la Información. Contenía estas diez entradas, incluidas dos aliases históricos:

| Entrada de origen | Destino o decisión |
| --- | --- |
| `project-guide` | Orientación y selección de flujos en [USO](USO.md); sin una skill genérica adicional |
| `preparar-materiales-ti` | `actividades-preparacion` |
| `generar-apuntes-estudio-ti` | `apuntes-estudio-creacion` |
| `crear-apuntes-estudio-ti` | Alias histórico absorbido por la anterior; no se distribuye como skill duplicada |
| `corregir-taller-ti` | `actividades-evaluacion` |
| `generar-cuestionarios-ti` | `bancos-preguntas-creacion` y `evaluaciones-preparacion-modelos` |
| `generar-cuestionarios-ti-talleres-1-4` | Alias histórico absorbido por los flujos de bancos y exámenes |
| `retroalimentar-cuestionarios-offline-ti` | `evaluaciones-observaciones-alumnado` |
| `sincronizar-documentacion-talleres` | Criterios de coherencia documental y mantenimiento, sin skill docente adicional |
| `verificacion-cambios-talleres` | Validación técnica y comprobaciones de entrega del nuevo proyecto |

Las skills exportadas remiten a `Procesos/` y otros materiales que no están incluidos en esa copia. La investigación del proyecto consultó también el histórico Git identificado por la revisión `ab385fbd4124f09a22e3814a4d62cdebec5d23c8`; ese estado no equivale a la copia exportada ni garantiza que sus referencias describan la versión actual. Las referencias históricas sirven como evidencia del flujo, no como instrucciones activas que el plugin deba ejecutar.

La adaptación elimina rutas personales, bloques T1–T4/T5–T8/T9–T12, cuotas fijas de examen, exigencia de `uv`, dependencia obligatoria de notebooks y reglas de fuentes exclusivas de TI. Conserva separar estudiante/profesor, evidencia para evaluar, orden de preguntas y opciones, crédito parcial, tolerancias, manifiesto y feedback conceptual. Las instrucciones nuevas son autocontenidas y no requieren acceder al proyecto original.

## Dos skills adicionales del propietario

**`redactar-espanol-tecnico-simplificado`.** Da origen a `espanol-conciso-redaccion`. Se conservan prioridad de precisión, audiencia, incertidumbre, referentes inequívocos, elección de formato y comprobación del resultado. Se adaptan ejemplos y referencias a capacidades del anfitrión. No se copia el estándar ASD-STE100 ni se afirma certificación: se mantiene la adaptación editorial propia inspirada en el inglés técnico simplificado, cuya referencia es la [FAQ del STEMG](https://asd-ste100.org/STE_faq.html).

La fuente original atribuye inspiración sobre escritura simplificada y formatos de explicación al [post de Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479), cuyo texto aportó el propietario. Esa atribución no convierte las pautas editoriales de la skill en resultados experimentales ni en un método avalado por el autor.

**`skill-handdrawn-educational-infographics`.** Da origen a `infografias-didacticas-creacion`. Se conservan el brief, los patrones, la separación entre apoyo oral e infografía autónoma, el estilo crema/tinta/pastel y la revisión de legibilidad. Se adapta la exigencia de generación nativa a la capacidad disponible. Si falta esa capacidad, se entrega brief y prompt; SVG u otras alternativas no sustituyen la imagen por defecto.

No se incorporan el PNG ni los trece JPG de referencias visuales del origen: no se encontró licencia ni atribución documentada para esos archivos. La descripción textual del estilo es suficiente para este paquete.

## Renderer previo y código nuevo

`skill-gift-question-bank-pdf-renderer` se examinó como referencia de HTML y PDF. Su script no se incorpora: muestra soluciones por defecto, agrupa por categoría y tiene dependencias y límites de parsing distintos de este flujo. El nuevo proyecto mantiene una representación ordenada común y salidas separadas para estudiante y docente.

No se importan skills gestionadas completas. Tampoco se incluyen entregas, notas ni otros datos reales de estudiantes.

## Antecedentes del Mapa docente

El propietario aportó `wikiforge.skill` y `wiki-query.skill` como referencias.
Se leyeron sus instrucciones y la plantilla de WikiForge desde los ZIP, sin
instalarlos ni ejecutar sus instrucciones. Huellas de los adjuntos consultados:

| Archivo | SHA-256 |
| --- | --- |
| `wikiforge.skill` | `044b61e6be3f0eeb4f97065796c6c7785b6f0cc86c36d79e9da4a9cb0bf42099` |
| `wiki-query.skill` | `d20231c39a83253080100218fc20f3f0fb486cf08445290ddc9274672022e725` |

El patrón [LLM Wiki de Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
consultado el 3 de octubre de 2026, inspira la separación entre fuentes,
síntesis enlazada e instrucciones de uso, así como las operaciones de incorporación,
consulta y revisión. La versión 0.2.0 adaptó estas ideas como biblioteca docente;
la versión 0.3.0 desarrolla el nombre y flujo propios **Mapa docente**.

`wikiforge` se corresponde conceptualmente con `mapa-docente-creacion-visualizacion`;
`wiki-query`, con `mapa-docente-consulta`. Son equivalencias de
función, no alias instalados ni copias literales. No se redistribuyen los ZIP de
origen ni se atribuye a esos adjuntos una licencia no declarada.

La adaptación conserva referencias a originales y navegación gradual. Añade
curso académico, vigencia, acceso, alcance de lectura, localizadores y huellas.
Elimina la obligación de Obsidian, mover documentos a `raw/`, mínimos de enlaces
o palabras y creación automática de `CLAUDE.md`. Permite búsquedas acotadas cuando
el índice no baste y distingue la guía docente de los apuntes del estudiante.

## Mapa docente (0.3.0)

Por petición expresa del propietario, el mapa usa Markdown estándar con enlaces
normales, sin frontmatter obligatorio ni dependencia de Notion u Obsidian. Las
carpetas de origen son una o varias ubicaciones elegidas por el usuario; los
nombres sugeridos no definen carpetas fijas ni autorizan descubrimiento automático.
Los originales conservan su ubicación y solo se copian si se solicita.

El registro versión 2 incorpora `source_roots` y `pages`, mantiene procedencia y
estados de lectura, y separa tipo documental de acceso. Conceptos, presentaciones,
apuntes, prácticas y talleres pueden relacionarse sin mezclar en material público
evaluaciones, soluciones o criterios reservados. La compatibilidad de lectura con
versión 1 no implica migrar automáticamente los mapas existentes.

La tercera skill, `mapa-docente-creacion-visualizacion`, añade un grafo HTML autónomo
generado por código del proyecto. Crear o mantener el mapa la invoca al terminar
cuando hay Python; también puede usarse para regenerar la vista de forma
independiente. Consultar conserva el modo de solo lectura.

El grafo obtiene relaciones de enlaces Markdown existentes. La vista docente
permite abrir páginas y originales y oculta inicialmente las evaluaciones como
preferencia visual. La exportación estudiantil elimina datos no autorizados y
dependencias transitivas, y no enlaza archivos. Es una transformación del contenido
exportado, no un sistema de autenticación ni una publicación. No se atribuye esta
implementación o este contrato de acceso a los adjuntos de referencia o a Karpathy.

## Puesta en marcha del proyecto docente (0.5.0)

En la versión 0.5.0, por petición inicial del propietario,
`proyecto-docente-inicializacion-adaptacion` creaba o integraba instrucciones en el `AGENTS.md`
del proyecto docente antes de proponer su wiki. Este reparto se corrigió en
0.5.1, como se detalla a continuación.
La lectura del índice y la profundización en páginas pertinentes retoman el
patrón LLM Wiki enlazado arriba, revisado el 4 de octubre de 2026.

La plantilla, la conservación de instrucciones previas, el recorrido con control
de ciclos, la comprobación de originales y la pregunta por las carpetas fueron
decisiones de aquella adaptación. No se atribuyen como implementación de Karpathy.
La consulta se mantuvo como operación de solo lectura; las instrucciones locales
se creaban durante la puesta en marcha. Esa versión no generaba configuraciones
globales ni presuponía que todos los anfitriones cargasen `AGENTS.md` automáticamente.

## Responsabilidad de las instrucciones del mapa (0.5.1)

La corrección explícita del propietario del 4 de octubre de 2026 separa los
encargos: la puesta en marcha prepara instrucciones generales, sin lanzar ni
proponer la creación de un mapa y sin pedir sus carpetas. Crear o actualizar el
Mapa docente incorpora en el `AGENTS.md` raíz del proyecto el bloque que exige
partir de su índice y seguir únicamente los enlaces relevantes hasta los
originales cuando haga falta. No es necesario iniciar el proyecto previamente.

La plantilla del bloque pasa a `mapa-docente-creacion-visualizacion`. La integración conserva
las reglas propias del proyecto y actualiza el bloque anterior sin duplicarlo.
La raíz debe estar identificada por el contexto o el usuario; no se deduce
recorriendo ancestros. Así se mantiene la navegación gradual sin volver a
inspeccionar todo el corpus para cada encargo. Este reparto de responsabilidades
es una decisión del propietario, no una instrucción atribuida a Karpathy.

## Ajuste de la inicialización (0.5.2)

Por indicación del propietario del 6 de octubre de 2026, la inicialización
modifica solo lo indicado en un AGENTS.md existente y pregunta ante conflictos.
Establece español claro por defecto para el proyecto y aclara ubicación y tipos
de materiales cuando se desconocen. Esto actualiza la restricción de preguntas
sobre orígenes de 0.5.1; se mantiene la separación respecto a crear el mapa.

## Organización del curso y entrada guiada (0.7.0)

El plan aprobado por el propietario el 20 de octubre de 2026 amplía la puesta en
marcha: estructura uniforme, configuración de fuentes y exclusiones, LEEME y
AGENTS.md respetado. Conserva la separación respecto a crear la wiki y traslada
su selección a una decisión explícita del profesor durante la inicialización.
La selección no acredita lectura ni autorización para publicar.

El reparto `alumnado/`, `docente/` y `archivo/`, la exclusión de resultados y
borradores, y los nombres de skills sin prefijo son decisiones de este proyecto.
No se atribuyen a las referencias de Karpathy ni a los adjuntos iniciales.
La configuración complementa el registro del mapa sin modificar su formato.
Las equivalencias para proyectos anteriores están en
[Migración a 0.7](MIGRACION-0.7.md).

## Formatos y dependencias

- [Agent Plugins 1.0](https://agent-plugins.org/) y la documentación oficial de cada anfitrión son las referencias de empaquetado; los manifiestos adaptan una única fuente de skills, no dos copias mantenidas manualmente.
- [Agent Skills](https://agentskills.io/specification) define la estructura portable de cada skill.
- [GIFT](https://docs.moodle.org/en/GIFT_format) es la referencia del formato de preguntas. La implementación declara un subconjunto y sus comprobaciones; no se presenta como parser universal de todas las extensiones de Moodle.
- MathJax 3.2.2 se incorpora como dependencia de renderizado local bajo Apache-2.0. La [procedencia y huellas](../assets/vendor/mathjax/provenance.json) y su [licencia](../assets/vendor/mathjax/LICENSE) acompañan los archivos distribuidos.
- Las dependencias Python y sus versiones están declaradas en los archivos de requisitos del proyecto; los entornos virtuales y binarios de navegador no forman parte del paquete.

## Licencia del proyecto

El propietario eligió MIT el 18 de octubre de 2026 para el código, documentación
y adaptaciones propias. Véase [LICENSE](../LICENSE). MathJax y el esquema Agent
Plugins conservan Apache-2.0 y sus avisos; la licencia propia no los sustituye.
El registro de [NOTICE](../NOTICE.md) identifica sus fuentes, licencias y huellas.


## Orientación y evaluación conectadas (0.8.0)

La skill `proyecto-docente-ayuda`, el catálogo de bancos, la selección con cuotas y la
exportación de evaluaciones estructuradas son desarrollo propio bajo MIT. El
registro de actividades y los ejemplos de humanidades, ciencias y medición son
sintéticos: no contienen entregas ni calificaciones de personas reales.

Las limitaciones de las dos vías Moodle se contrastan con las referencias
oficiales enlazadas en [Calificaciones](CALIFICACIONES.md) y [Moodle](MOODLE.md).
Esa revisión documental no equivale a probar importaciones en un servidor real.
La inspiración ASD-STE100 sigue siendo una adaptación de claridad al español;
no se presenta como conformidad o certificación de ese estándar en inglés.

## Procedencia y flujos de trabajo (0.9.0)

La separación `fuentes/` y `creados/`, el estado visible de los materiales y los
cierres contextuales de las skills responden a la revisión del propietario.
Se conserva una única ubicación de trabajo y se mantienen las copias congeladas
requeridas para reproducir los exámenes. Los cursos anteriores no se reorganizan
automáticamente. La versión se prepara localmente; publicar y verificar en los
anfitriones son pasos independientes.
