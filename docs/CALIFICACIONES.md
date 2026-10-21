# Corrección de actividades y feedback para Moodle

El agente valora las entregas con el enunciado, los entregables pedidos, la
rúbrica docente y la resolución disponible. Las utilidades comprueban los
cálculos y las correspondencias y preparan archivos para importar manualmente.
No ejecutan código del alumnado ni asignan notas basándose en supuestos de uso
de IA.

## Recorrido del profesor

1. Al terminar la actividad, acepta la oferta de preparar su carpeta de recepción
   o pide «Prepara la carpeta para recibir las entregas de esta actividad».
   Tendrá el mismo identificador y nombre de carpeta, bajo
   `resultados/<actividad>/<convocatoria>/`, y un LEEME con los pasos y criterios.
2. Descarga las entregas y el CSV de calificaciones de la misma actividad y
   convocatoria. Guarda los trabajos en `recibidos/entregas/` y la hoja original
   en `recibidos/`, conservando nombres e identificadores.
3. Pide: «Evalúa estas entregas con el enunciado y la rúbrica de esta actividad
   y prepara la hoja de Moodle con notas y feedback».
   El agente identifica los criterios disponibles; si faltan, presenta una
   propuesta antes de calcular notas definitivas.
4. Revisa las evidencias y puntuaciones por criterio, el feedback y las
   incidencias. Los resultados de corrección se guardan en `correccion/`, separada de `recibidos/`
   dentro del lote; los identificadores y su correspondencia con las entregas se
   conservan junto a los originales.
5. Importa manualmente la copia CSV de `correccion/` siguiendo la vía Moodle
   elegida. Comprueba la vista previa antes de confirmar la importación.

El agente prepara el perfil de columnas y la evaluación estructurada; el profesor
no tiene que escribir JSON. Si el encargo incluye notas y feedback para Moodle,
la copia CSV forma parte de esa misma tarea. Si falta la hoja o una correspondencia,
se explica qué aportar y se conserva el análisis cualitativo disponible.

La utilidad acepta **CSV**, no `.xlsx` directamente. Excel puede abrir un CSV,
pero eso no lo convierte en un libro Excel. Si solo se aporta `.xlsx`, conservar
el original y solicitar el CSV de Moodle o convertir una copia con herramientas
disponibles, verificando identificadores como texto, ceros iniciales, columnas,
filas y notas. No confundir una conversión de formato con cambiar entre hoja de
tarea y libro de calificaciones.

El identificador puede ser el de participante de la hoja de tareas, el ID de
usuario, el nombre de usuario o el identificador institucional de un libro,
siempre que figure explícitamente en ambos archivos. No se atribuye una entrega
por semejanza del nombre del estudiante. Una valoración grupal declara todos
sus miembros con esos mismos identificadores; no se infiere la pertenencia por
el nombre de una carpeta.

Una entrega ausente, ilegible o pendiente conserva su nota y comentario
anteriores. No se convierte en cero. Una fila sin valoración también se
conserva y queda registrada como incidencia. Las correspondencias ambiguas o
los datos obligatorios inconsistentes bloquean todo el CSV del lote; el informe
conserva las valoraciones para poder revisarlas.

## Dos vías de importación distintas

| Perfil | Archivo y uso |
| --- | --- |
| `worksheet` | Hoja de calificación sin conexión descargada desde una tarea. Conserva sus identificadores de participante y columnas. |
| `gradebook` | CSV exportado desde el libro de calificaciones, con columna de nota y columna de comentario de la actividad elegida. |

Una rúbrica local usada para revisar trabajos no implica que la tarea tenga
activada la calificación avanzada de Moodle. Si la tarea sí utiliza una rúbrica
o guía de evaluación avanzada, Moodle no admite la subida de notas y comentarios
mediante la hoja sin conexión. El perfil `worksheet` exige declarar
`advanced_grading`; si es `true`, se conserva el análisis y se bloquea esa
exportación. El profesor debe decidir el procedimiento; la utilidad no cambia
al perfil de libro automáticamente. Consulta la
[documentación de tareas de Moodle](https://docs.moodle.org/en/Using_Assignment).

La importación desde el libro equivale a editar sus calificaciones manualmente
y puede impedir la posterior edición de la nota desde la tarea. Al importar
feedback deben mapearse **la columna de comentario y la nota de esa misma
actividad**: omitir la nota puede hacer que se pierda. Por eso los archivos de
feedback conservan la nota original, incluso cuando solo cambia el comentario.
Revisa también los permisos y la vista previa de la importación.
[Documentación de importación de calificaciones](https://docs.moodle.org/en/Grade_import).

Estas limitaciones se han contrastado con la documentación oficial; no equivalen
a una importación real verificada en la instalación Moodle del profesor.

## Contrato de evaluación de actividades

API Python:

```python
from docencia.grading import export_grades

report = export_grades(
    evaluation_path="evaluacion.json",
    input_path="calificaciones-originales.csv",
    config_path="perfil-moodle.json",
    output_dir="revision"
)
```

CLI equivalente para agentes y usuarios avanzados:

```sh
python scripts/docencia.py export-grades evaluacion.json \
  --input calificaciones-originales.csv --config perfil-moodle.json \
  --output revision
```

El agente prepara los JSON; el profesor no necesita escribirlos. Los siguientes
ejemplos son sintéticos. El contrato es estricto: los campos desconocidos se
rechazan para no ignorar errores de escritura en criterios o perfiles.

`evaluacion.json`:

```json
{
  "schema_version": 1,
  "activity_id": "analisis-de-fuentes",
  "attempt_id": "2026-ordinaria",
  "activity_version": "1",
  "sources": ["enunciado.md", "rubrica-docente.md"],
  "rubric": [
    {"id": "evidencia", "max_score": 4, "weight": 60},
    {"id": "argumentacion", "max_score": 5, "weight": 40}
  ],
  "evaluations": [
    {
      "student_id": "Participante 001",
      "status": "evaluated",
      "criteria": [
        {"id": "evidencia", "score": 3,
         "evidence": ["Informe, página 2: contrasta dos fuentes, pero omite el contexto de una."]},
        {"id": "argumentacion", "score": 4,
         "evidence": ["Informe, conclusión: delimita la tesis y distingue observación e interpretación."]}
      ],
      "total_points": 7,
      "feedback": "Explica cómo el contexto afecta a la fiabilidad de cada fuente.",
      "justification": "La rúbrica exige contraste contextual y argumentación sustentada."
    },
    {
      "student_id": "Participante 002",
      "status": "unreadable",
      "justification": "El documento descargado no se puede abrir; hace falta una entrega legible."
    }
  ]
}
```

- `activity_id` y `attempt_id` identifican el lote completo y deben coincidir
  exactamente con el perfil. `activity_version` y `sources` son opcionales y
  documentan los materiales de revisión.
- `rubric` contiene criterios con ID único, máximo positivo y peso positivo.
  Los pesos suman exactamente 100; `label` es opcional.
- Cada valoración usa `student_id` o la pareja `group_id` y `members`, nunca
  ambas. `members` es una lista de identificadores de participantes. La misma
  valoración se aplica a cada miembro; para notas diferentes se necesitan
  valoraciones individuales.
- `status` admite `evaluated`, `absent`, `unreadable` o `pending`.
  `justification` es obligatorio en todos los casos.
- Una valoración `evaluated` necesita todos los criterios, puntuación entre
  cero y su máximo, evidencias textuales con localización y `feedback`.
  `total_points` es opcional; si aparece, debe coincidir con la suma sin ponderar.
- Los otros estados no pueden contener puntuaciones ni `total_points`.
  Su comentario de revisión puede guardarse en el JSON, pero no sustituye el
  comentario del CSV.

Para una entrega grupal se sustituye `student_id` por:

```json
{
  "group_id": "grupo-01",
  "members": ["Participante 001", "Participante 003"]
}
```

No pueden repetirse miembros dentro de un grupo ni entre valoraciones del mismo
lote. Debe existir una fila inequívoca para cada miembro.

`perfil-moodle.json`:

```json
{
  "schema_version": 1,
  "profile": "worksheet",
  "advanced_grading": false,
  "activity_id": "analisis-de-fuentes",
  "attempt_id": "2026-ordinaria",
  "identifier_column": "Identificador",
  "grade_column": "Calificación",
  "feedback_column": "Comentarios",
  "grade_max": 10,
  "decimals": 2,
  "rounding": "half_up",
  "decimal_separator": ",",
  "delimiter": ";"
}
```

Las cabeceras deben coincidir con la exportación real; no se asumen traducciones.
`profile` puede ser `gradebook` con sus columnas equivalentes. Se requieren la
escala numérica desde cero (`grade_max`), los decimales de salida (0 a 8) y el
redondeo: `half_up` (mitades hacia arriba), `half_even` (mitades al par) o `down`
(truncamiento). El máximo debe poder representarse con esos decimales: una
escala hasta `2.5` requiere al menos un decimal. Se bloquean perfiles que podrían
redondear la nota por encima de su máximo. La nota se calcula como:

```text
nota = grade_max × Σ(puntuación del criterio / máximo del criterio × peso) / 100
```

En el ejemplo, `3/4 × 60 + 4/5 × 40 = 77 %`, que da `7,70` sobre diez.
`decimal_separator` es opcional, con punto por defecto. `delimiter` admite
coma, punto y coma o tabulador; si falta, se exige una detección inequívoca.
`activity_column` y `attempt_column` son opcionales: cuando se declaran, solo
se actualizan filas que coincidan con los ID del lote, conservando las demás.
Sin esas columnas, el perfil declara que el archivo corresponde al lote.

Si existe el registro de la actividad, añade al perfil
`"activity_record": "../../../../materiales_generados/actividades/analisis-de-fuentes/_datos_internos/actividad.json"`,
para un perfil situado en `resultados/analisis-de-fuentes/ordinaria/correccion/`;
si está en otra ubicación, adaptar la ruta relativa a su carpeta. La evaluación debe incluir
`activity_version`: se comprueban el `id` y la `version` del registro, la existencia
de enunciado, rúbrica, plantillas y guía declarada, y sus audiencias. Los PDF
registrados también deben existir. Las huellas de estos archivos y del registro
quedan en el informe. Esta comprobación verifica procedencia, sin interpretar
semánticamente el Markdown de la rúbrica ni declarar que el agente lo haya leído.

Cuando se encuentra la configuración `_datos_internos_proyecto/proyecto-docente.json`
en un curso antecesor del perfil,
el registro y sus documentos deben permanecer dentro del curso, también después
de resolver enlaces simbólicos. Sin una raíz conocida se informa de que no se ha
verificado ese límite. Sin un registro de actividad disponible se emite un aviso explícito: solo se han comprobado los ID de actividad y
convocatoria, sin vincular los documentos ni su versión.

La salida es `calificaciones_<actividad>_<convocatoria>.csv`, UTF-8 con BOM,
conservando delimitador, orden de filas y columnas, identificadores y textos
ajenos a la nota y el comentario configurados. El informe `grading-report.json`
incluye las huellas de entradas, evaluación original, incidencias y auditoría
por participante: valores anteriores, nuevos, cálculo y justificación.
Repetir el proceso nunca sobrescribe un CSV; los informes reciben un nombre
numerado cuando hace falta. La salida debe quedar fuera del plugin.

## Feedback posterior a cuestionarios

`build-feedback` usa el manifiesto y su banco congelado para interpretar el
detalle de puntuaciones por pregunta. Una nota global sin ese detalle no permite
atribuir dificultades a conceptos.

La configuración existente admite:

```json
{
  "feedback_priority": {
    "max_concepts": 3,
    "marked_threshold": 0.5,
    "min_evidence": 2
  }
}
```

Para cada concepto se suman las puntuaciones y máximos de **todas** sus
preguntas, incluidas las acertadas. Se ordenan por proporción de puntos perdidos
y, en caso de empate, por cantidad de preguntas. Se priorizan hasta tres.
Solo se denomina «dificultad acusada» un resultado estrictamente inferior al
50 % apoyado en al menos dos preguntas. Los demás fallos se presentan como
aspectos a revisar. Un token declarado expresamente como respuesta en blanco
aporta cero puntos para esta orientación, conservando su texto original; una
puntuación ausente sin esa declaración bloquea el lote.

Los metadatos de conceptos o preguntas pueden aportar referencias:

```json
{
  "label": "Balance de cantidades",
  "guidance": "Distingue acumulación, tasa y unidades.",
  "references": [
    {"title": "Guía de unidades",
     "path": "alumnado/materiales/unidades.md", "access": "estudiante"},
    {"title": "Solución docente",
     "path": "docente/soluciones/balance.md", "access": "docente"}
  ]
}
```

Solo se incluyen referencias con `access: "estudiante"`. Las rutas se expresan
desde la raíz del curso o como URL HTTP(S), sin credenciales, rutas absolutas,
retrocesos `..` ni accesos a `docente/`. Los enlaces docentes o sin clasificación
se omiten antes de producir el comentario. El agente comprueba que las
orientaciones también sean aptas para el alumnado; no debe copiar soluciones
reservadas en `guidance`. Si el manifiesto incluye `metadata.materials`, las
referencias de conceptos **y de preguntas** deben coincidir con un material
declarado cuyo acceso sea estudiantil; un enlace etiquetado como estudiantil no
puede anular la clasificación docente del material. Los accesos contradictorios
bloquean la exportación sin trasladar el contenido reservado al comentario.
En manifiestos antiguos sin `materials` se conservan únicamente las referencias
explícitamente estudiantiles que superen la comprobación de destino seguro;
esa declaración no acredita permisos reales y debe revisarla el docente.
Los enlaces relativos se revisan antes de importar:
el CSV no publica los archivos locales en Moodle. Si se desea un enlace que
funcione dentro de Moodle, el profesor proporciona la URL accesible del recurso.

El detalle de opciones elegidas es optativo y necesita las columnas de
respuestas; el feedback conceptual habitual no revela enunciados ni soluciones.
Los no presentados reciben comentario vacío y conservan la nota original.

## Cruce con un libro de calificaciones separado

La API `build_feedback(..., gradebook_path="libro-original.csv")` permite usar
un CSV de respuestas/puntuaciones como evidencia y otro CSV como destino.
La CLI ofrece `build-feedback --gradebook libro-original.csv`. En este caso,
el CSV de evidencia no necesita columna de comentarios.

A la configuración existente se añade:

```json
{
  "gradebook": {
    "identifier_column": "ID",
    "feedback_column": "Comentarios de la evaluación",
    "grade_column": "Nota de la evaluación",
    "model_column": "Modelo papel",
    "delimiter": ";"
  }
}
```

Si todo el libro corresponde a un único modelo, sustituye `model_column` por
`"default_model": "A"`; se exige exactamente una de las dos opciones. Las
correspondencias usan el identificador exacto y el modelo. Un mismo participante
puede aparecer en modelos distintos solo cuando esa correspondencia es explícita;
dos filas del mismo participante y modelo bloquean la salida.

Se conserva el orden del libro y todas sus notas, incluidos los textos vacíos
o no numéricos que Moodle ya hubiera exportado. Las filas sin detalle mantienen
su comentario y generan un aviso; un detalle sin fila de destino bloquea el
lote. Se produce un CSV por modelo y solo se añade el consolidado cuando se pide.
El informe documenta el comentario anterior, el nuevo y la nota conservada.
El flujo anterior, con un solo tipo de CSV que ya contiene puntuaciones y
comentarios, sigue siendo válido.
