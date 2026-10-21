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

En `curso-v3`, la carpeta estable es `materiales_generados/actividades/<id>/`:

```text
analisis-de-fuentes/
├── LEEME.md
├── alumnado/
│   ├── enunciado.md
│   ├── enunciado.pdf
│   └── plantilla-informe.md
├── docente/
│   ├── rubrica.md
│   └── guia-correccion.md
└── _datos_internos/
    ├── material-docente.json
    └── actividad.json
```

El registro común es de tipo `actividad`; su estado (`borrador`, `revisado` o
`listo-para-entregar`) se muestra también en `LEEME.md`. La aprobación no mueve
archivos y no autoriza una publicación automática. `actividad.json` mantiene
la procedencia y versión de los archivos utilizados para evaluar, según el
[contrato del curso](PROYECTO-DOCENTE.md). Las fuentes originales se enlazan;
si esta actividad se usa después para un banco, permanece en su misma carpeta.
Al ubicar `actividad.json` en `_datos_internos/`, ajustar sus rutas relativas
según la misma base contractual; no reinterpretarlas desde la raíz del curso.

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
`_datos_internos/`, el enunciado se enlaza como `../alumnado/enunciado.md`. Las rutas
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

## Recepción y corrección

Al terminar la actividad, el agente ofrece preparar su carpeta de recepción.
Al aceptar, crea el siguiente árbol, con el mismo nombre de carpeta e identificador
que la actividad. Reutiliza la convocatoria conocida; si no se ha concretado
y no hay ambigüedad, usa `ordinaria` e indica ese destino. Ante una diferencia entre el identificador registrado y el
nombre de la carpeta, aclara la correspondencia antes de crear el lote.

```text
resultados/analisis-de-fuentes/
└── ordinaria/
    ├── LEEME.md
    ├── recibidos/
    │   ├── entregas/                    trabajos descargados de Moodle
    │   └── calificaciones-originales.csv  hoja original, cuando se aporte
    └── correccion/                     notas, comentarios e incidencias
```

El CSV del árbol representa el archivo que aportará el profesor, no un archivo
vacío que deba generar el agente. Conservar su nombre original al descargarlo.
Si hacen falta correspondencias grupo–miembros o entrega–participante, guardarlas
en `recibidos/identificacion/`. No atribuir identidades por parecido de nombres.

Adaptar la [plantilla de recepción](../templates/recepcion-actividad.md) como
`LEEME.md` del lote: actividad, convocatoria, estado comprobado, enlaces relativos
al enunciado, rúbrica y guía disponibles, dónde colocar cada entrada y petición
para evaluar. El LEEME docente de la actividad enlaza a su lote. No copiar los
criterios ni añadir estos enlaces a documentos estudiantiles. Si el lote existe,
conservar sus archivos, integrar solo información necesaria y mostrar qué falta;
no duplicar carpetas, reglas o enlaces ni sobrescribir descargas o correcciones.
La estructura vacía significa «pendiente de entregas», no «recibido» ni «evaluado».

El profesor coloca las entregas y el CSV de la misma actividad y convocatoria en
`recibidos/` y pide: «Evalúa estas entregas y prepara la hoja de Moodle con notas
y feedback». El agente consulta los criterios, comprueba identificadores y
columnas, corrige y produce una copia importable en `correccion/`, junto con la
evaluación por criterio y las incidencias. Un encargo completo no exige pedir la
exportación una segunda vez. El profesor revisa el resultado y lo importa en Moodle.

La utilidad trabaja con CSV, aunque pueda abrirse en Excel. Un `.xlsx` necesita
conversión verificada o una nueva descarga CSV; no se admite directamente.
Los JSON de evaluación, perfil de columnas y auditoría son preparados por el
agente y no tiene que rellenarlos el profesor. Todo el lote queda fuera del
corpus de la wiki. Los originales se conservan intactos.

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

Al entregar la actividad, ofrecer preparar la carpeta de recepción si falta y
corregir sus entregas con estos criterios cuando estén disponibles; indicar entregas e identificación pendientes
y, para la salida importable, la hoja Moodle y sus columnas. Si ya hay una
corrección válida, ofrecer revisarla en lugar de repetirla. Aplicar el
[cierre contextual](FLUJOS-DOCENTES.md) sin iniciar la corrección automáticamente.
