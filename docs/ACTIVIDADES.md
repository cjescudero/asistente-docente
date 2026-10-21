# Actividades, plantillas y criterios docentes

Una actividad se diseña a partir de conocimientos que se quieren evaluar y de
evidencias que el alumnado puede aportar. Puede ser un análisis de fuentes,
experimento, caso, taller, práctica profesional o trabajo con código. La elección
depende del encargo y de la disciplina.

## Preparar la actividad mediante diálogo

El profesor puede empezar con «Quiero una actividad sobre estos materiales;
ayúdame a decidir qué pedir y cómo evaluarlo». El agente recupera el contexto
conocido y aclara por etapas:

1. Materia, nivel, objetivos y materiales actuales.
2. Ejemplos de otros años que sirvan de inspiración y dificultad deseada.
3. Duración, modalidad, recursos, entregables y condiciones de uso de IA.
4. Tareas propuestas, evidencias observables y criterios generales.

Los ejemplos históricos son opcionales. No fijan el temario ni la rúbrica del
curso vigente. Antes de producir los documentos, el profesor puede ajustar la
propuesta; si su petición ya especifica el diseño, no hace falta repetir todas
las preguntas.

El diseño considera que el alumnado tiene acceso a IA. Por ejemplo, se puede
pedir justificar una decisión, contrastar resultados con fuentes o revisar una
solución a la luz de observaciones propias. No se impone usar IA, una prohibición,
una defensa oral ni una sanción sin decisión del profesor. Esas evidencias evalúan
comprensión y proceso; no prueban la autoría de un texto por sí solas.

## Archivos entregados

- **Enunciado:** Markdown editable y PDF cuando pueda generarse y comprobarse.
  Incluye tareas, entregables y criterios generales de evaluación.
- **Plantillas:** las que necesite la actividad: informe, ficha de análisis,
  registro experimental, hoja de trabajo o notebook si procede.
- **Rúbrica docente:** criterios, niveles, pesos y evidencias esperadas. Se
  conserva completa como material reservado.
- **Guía docente:** solución orientativa, alternativas válidas y errores
  frecuentes cuando correspondan.
- **Registro `actividad.json`:** vincula los archivos y fuentes de una misma
  versión para preparar después la corrección.

En `curso-v2`, la carpeta estable es `creados/actividades/<id>/`:

```text
analisis-de-fuentes/
├── LEEME.md
├── material-docente.json
├── alumnado/
│   ├── enunciado.md
│   ├── enunciado.pdf
│   └── plantilla-informe.md
└── docente/
    ├── actividad.json
    ├── rubrica.md
    └── guia-correccion.md
```

El registro común es de tipo `actividad`; su estado (`borrador`, `revisado` o
`listo-para-entregar`) se muestra también en `LEEME.md`. La aprobación no mueve
archivos y no autoriza una publicación automática. `actividad.json` mantiene
la procedencia y versión de los archivos utilizados para evaluar, según el
[contrato del curso](PROYECTO-DOCENTE.md). Los cursos anteriores conservan su
organización hasta una migración aprobada. Las fuentes originales se enlazan;
si esta actividad se usa después para un banco, permanece en su misma carpeta.

El registro es docente porque puede revelar rutas de soluciones o rúbricas.
El enunciado y las plantillas estudiantiles no deben enlazarlo ni incluir
contenido reservado. Los nombres de carpetas y el campo `audience` expresan el
destino previsto, pero no configuran permisos.

## Registro ligero de actividad

La [plantilla JSON](../templates/actividad.json) es un ejemplo para adaptar,
no un lote listo para aplicar: sus rutas deben sustituirse por archivos reales.
El registro utiliza UTF-8, `schema_version: 1` y los siguientes campos:

| Campo | Contenido |
| --- | --- |
| `id` | Identificador estable de la actividad, sin depender de su título. |
| `version` | Versión de enunciado, plantillas y criterios utilizados conjuntamente. |
| `title`, `objectives` | Título y objetivos evaluables. |
| `sources` | Fuentes con `id`, `path`, `locator`, `role` y `audience`. |
| `files.statement` | Enunciado con `path` y `audience: "estudiante"`. |
| `files.templates` | Lista de plantillas con `id`, `path` y `audience: "estudiante"`; puede estar vacía si no se necesita plantilla. |
| `files.rubric` | Rúbrica completa con `path` y `audience: "docente"`. |
| `files.teaching_guide` | Guía con `path` y `audience: "docente"`, solo cuando exista. |

Todas las rutas se resuelven desde la carpeta del registro; si está en
`docente/`, el enunciado se enlaza como `../alumnado/enunciado.md`. Las rutas
del registro son distintas de las rutas del catálogo y de la configuración. Las fuentes usan
`role: "current"` para el contenido vigente o `"inspiration"` para ejemplos
históricos. Su `audience` indica `"estudiante"` o `"docente"` según el acceso
autorizado, independientemente de su vigencia.

Los documentos pueden añadir un campo `pdf` con una ruta relativa cuando ese
PDF exista. Un HTML, un intento de renderizado fallido o la previsión de generar
un PDF no justifican ese campo. Si falta capacidad de PDF, entregar fuentes y
HTML disponibles y declarar el PDF pendiente.

Es un contrato documental: la revisión comprueba rutas, versiones, separación
de audiencias y coherencia pedagógica. La calificación estructurada y la
exportación a Moodle tienen su propio [contrato](CALIFICACIONES.md).

## Corrección posterior

Cada lote de entregas se organiza en
`resultados/<actividad>/<convocatoria>/` en cursos v2, con originales
descargados y correspondencias explícitas de identificación en `recibidos/`,
y resultados, CSV modificados e incidencias en `correccion/`. Los lotes de cursos
v1 conservan sus ubicaciones. Este contenido queda fuera del corpus de la wiki.

La evaluación consulta el enunciado y los criterios de la versión aplicada,
además de la guía o resolución disponible. Si faltan criterios suficientes,
el agente propone una rúbrica antes de calcular notas definitivas; puede
entregar mientras tanto un análisis cualitativo.

En trabajos abiertos no se exige coincidencia literal con una solución modelo.
El informe relaciona cada puntuación con evidencias de la entrega y conserva
casos pendientes o ilegibles. Los CSV de Moodle se preparan sobre copias y se
revisan antes de una importación manual, conforme a [Moodle](MOODLE.md).

## Comprobaciones docentes representativas

- **Humanidades:** comparar testimonios con conclusiones distintas pero
  argumentadas; comprobar que la rúbrica evalúa evidencia y razonamiento y no
  obliga a una conclusión única. La ficha de comparación no incluye la solución.
- **Ciencias:** interpretar un experimento con controles; comprobar que la
  plantilla recoge observaciones, unidades e incertidumbres y que el enunciado
  proporciona condiciones suficientes para distinguir hipótesis y resultados.
- **Actividad experimental:** diseñar una medición con recursos limitados;
  comprobar que se evalúan decisiones y anomalías observadas sin inventar datos
  ni tratar una simulación como una experiencia realizada.
- **Programación, cuando se solicite:** entregar un notebook inicial sin
  soluciones en celdas, salidas ni metadatos, con tareas y comprobaciones
  compatibles con los criterios anunciados.

Estas comprobaciones requieren revisar documentos reales del caso. La existencia
de los archivos o de una plantilla válida no demuestra por sí sola calidad
didáctica ni validación en el aula.

## Siguiente paso

Al entregar la actividad, ofrecer corregir sus entregas con esta versión de los
criterios cuando estén disponibles; indicar entregas e identificación pendientes
y, para la salida importable, la hoja Moodle y sus columnas. Si ya hay una
corrección válida, ofrecer revisarla en lugar de repetirla. Aplicar el
[cierre contextual](FLUJOS-DOCENTES.md) sin iniciar la corrección automáticamente.
