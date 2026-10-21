# Bancos asociados a materiales y cuestionarios combinados

Un banco nuevo combina un archivo GIFT, metadatos pedagógicos y referencias a
los materiales que lo sustentan. Cada material conserva su ubicación original.
Los bancos y exámenes anteriores pueden orientar la dificultad y el estilo;
el profesor decide qué contenidos siguen vigentes.

Pide, por ejemplo: «Crea un banco sobre estas diapositivas y esta actividad.
Utiliza el examen del año pasado para calibrar la dificultad». El agente debe
acordar los objetivos y la cobertura, comprobar las fuentes autorizadas y
proponer las preguntas antes de incorporarlas a una evaluación.

## Archivos y raíces

En cursos v2, cada banco nuevo se guarda en `creados/bancos/<id>/`, con GIFT,
metadatos, `material-docente.json` de tipo `banco` y estado visible en `LEEME.md`.
Un borrador conserva ese destino al revisarse. El catálogo está en
`creados/bancos/catalogo.json` y puede enlazar bancos aportados bajo
`fuentes/evaluaciones/bancos/` sin copiarlos. La presencia en el catálogo no
acredita revisión pedagógica ni autoriza entregar el banco con soluciones.
Los cursos anteriores mantienen sus ubicaciones y contratos.

Los bancos se entregan **sin comprimir**, con enlaces directos a `banco.gift` y
`metadatos.json`, y su guía y registro en la misma carpeta. El GIFT es el archivo
de preguntas que se usa con Moodle; los JSON documentan procedencia y variantes
para las utilidades docentes. El ZIP solo es opcional ante petición del profesor
o una limitación comprobada de entrega, explicada y sin sustituir los archivos
individuales. Los ZIP de la release distribuyen el plugin, no son el formato
predeterminado de los bancos.

Los contratos JSON usan UTF-8 y `schema_version: 1`:

| Archivo | Contrato |
| --- | --- |
| Catálogo | `banks`: lista de objetos con `id`, `gift` y `metadata`; `path_base` opcional. |
| Metadatos de banco | `materials`, `concepts` y `questions`: objetos por identificador. |
| Selección | `banks`: identificadores elegidos; `quotas`: reparto común a cada modelo. |

`path_base: "project"` permite que `gift` y `metadata` sean relativos a la raíz
del curso y enlacen bancos de distintas ramas. Es la opción de los catálogos
nuevos de curso-v2. Si el campo falta o vale `"catalog"`, las rutas siguen siendo
relativas a la carpeta del catálogo, conservando compatibilidad.

Las rutas de materiales y recomendaciones son relativas a la raíz del curso.
La utilidad localiza `proyecto-docente.json` en los antecesores del catálogo;
`--project` permite indicar esa raíz. `path_base: "project"` requiere una raíz
explícita o descubierta en la configuración. Para un catálogo antiguo fuera de
un proyecto, la raíz predeterminada sigue siendo su carpeta. No se admiten rutas
absolutas, `..`, unidades de Windows ni enlaces simbólicos bajo esas raíces.
Las rutas escritas en JSON usan `/`, también en Windows.

Ejemplo de catálogo:

```json
{
  "schema_version": 1,
  "path_base": "project",
  "banks": [
    {"id": "historia-fuentes", "gift": "fuentes/evaluaciones/bancos/historia.gift", "metadata": "fuentes/evaluaciones/bancos/historia.metadata.json"},
    {"id": "actividad-medicion", "gift": "creados/bancos/medicion/banco.gift", "metadata": "creados/bancos/medicion/metadatos.json"}
  ]
}
```

Cada identificador de banco usa minúsculas, cifras, guiones, puntos o guiones
bajos y empieza por letra o cifra. No puede repetirse ni registrar dos veces
el mismo archivo GIFT. El título GIFT identifica cada pregunta dentro de su
banco: dos bancos distintos pueden conservar el mismo título original.

## Metadatos pedagógicos y procedencia

Cada entrada de `materials` incluye:

- `path`: ruta del original relativa al curso.
- `title`: nombre comprensible.
- `access`: `estudiante` o `docente`, declarado por el profesor.
- `sha256`: huella SHA-256 actual de sus bytes, en 64 caracteres hexadecimales.

La utilidad comprueba las exclusiones y la selección del curso antes de leer
el original para verificar su huella. Si cambia, exige revisar las preguntas
dependientes antes de crear otro examen; no actualiza la huella automáticamente.
Una selección de fuentes aplazada, una fuente excluida, ilegible o inexistente
impide usar el banco afectado. Las entregas y resultados permanecen fuera del
corpus. Elegir una fuente no autoriza su publicación.

Cada pregunta del GIFT debe tener exactamente una entrada de `questions`, con:

- `source_refs`: una o más referencias `{ "material_id": "...", "locators": ["..."] }`.
  Un mismo material figura una sola vez, con todos sus localizadores. Estos
  pueden describir páginas, diapositivas, apartados o fases de una actividad.
- `concepts`: uno o más identificadores declarados en `concepts`.
- `objective`: conocimiento o actuación que se evalúa.
- `difficulty`: `basica`, `intermedia` o `avanzada`; estimación pedagógica,
  revisable con ejemplos históricos y resultados.
- `guidance`: orientación de repaso redactada para el estudiante, sin incluir
  soluciones reservadas.

Los conceptos requieren `label`; pueden incluir `guidance` y `references`.
Las preguntas también pueden añadir `references` específicas para el repaso.
En ambos lugares, cada referencia lleva `title`, `path` y `access`; debe
corresponder a un material declarado y tener su mismo acceso. El feedback solo podrá recomendar enlaces
marcados explícitamente como `estudiante`. La etiqueta no cambia los permisos
reales del archivo.

Ejemplo parcial —el agente debe calcular la huella y completar todas las
preguntas del banco—:

```json
{
  "schema_version": 1,
  "materials": {
    "carta-historica": {
      "path": "fuentes/teoria/carta.md",
      "title": "Carta y contexto histórico",
      "access": "estudiante",
      "sha256": "<huella SHA-256 calculada sobre el archivo>"
    }
  },
  "concepts": {
    "interpretar-fuentes": {
      "label": "Interpretación de fuentes",
      "guidance": "Distingue la información explícita de las inferencias.",
      "references": [
        {
          "title": "Revisar la carta",
          "path": "fuentes/teoria/carta.md",
          "access": "estudiante"
        }
      ]
    }
  },
  "questions": {
    "01-A": {
      "family_id": "01",
      "variant_id": "A",
      "source_refs": [
        {"material_id": "carta-historica", "locators": ["párrafos 2 y 3"]}
      ],
      "concepts": ["interpretar-fuentes"],
      "objective": "Distinguir hechos documentados e inferencias.",
      "difficulty": "intermedia",
      "guidance": "Señala qué fragmentos respaldan cada interpretación."
    }
  }
}
```

Los identificadores de materiales y conceptos son comunes al curso. Si aparecen
en varios bancos, sus declaraciones deben coincidir. Ante definiciones distintas
de un mismo identificador se detiene la composición para resolver la diferencia;
no se toma silenciosamente la primera ni se pierde su procedencia.

## Preguntas principales y variantes

La skill propone cuántas preguntas **principales** necesita el banco a partir de
los conceptos, objetivos, relevancia y diversidad de actuaciones de las fuentes.
Explica ese reparto y permite aumentarlo o reducirlo; informa de las carencias
si la cantidad elegida no cubre todo. No fija una cantidad universal.

El uso previsto son **cuatro modelos**, salvo otra indicación. Una principal
puede tener hasta cuatro variantes equivalentes como punto de partida, ajustable
al número de modelos y a las posibilidades reales del material. Cambiar letras
o barajar opciones no crea una variante de contenido. Por ejemplo, 8 principales
con 4 variantes cada una son 32 ítems GIFT, pero 8 familias, no 32 objetivos.

Cada variante conserva un ID GIFT único y añade en su entrada de `questions`:

```json
{"family_id": "01", "variant_id": "A"}
```

En bancos nuevos, la principal tiene un número estable y sus variantes se
identifican con letras mayúsculas. La clave de metadatos y el título GIFT
combinan ambos, con al menos dos cifras para las principales iniciales:

| Principal | Variante | Título GIFT y clave de metadatos |
| --- | --- | --- |
| `01` | `A` | `01-A` |
| `01` | `B` | `01-B` |
| `01` | `C` | `01-C` |
| `01` | `D` | `01-D` |
| `02` | `A` | `02-A` |

Así, `::01-A::` corresponde a `questions["01-A"]`, con `family_id: "01"` y
`variant_id: "A"`. Una sola variante usa `A`; después de `Z`, continuar `AA`,
`AB`… si procede. A partir de 100 principales, usar `100-A` sin modificar IDs
anteriores. Mantener los identificadores al reordenar y no reutilizar números
retirados para preguntas distintas. La identidad completa del ítem incluye el
banco; dos bancos pueden tener su propio `01-A`.

Es una convención de autoría, no una restricción nueva del lector: bancos
anteriores con otros identificadores siguen funcionando. No renumerarlos ni
modificar snapshots de cuestionarios usados. Las letras de las variantes no
indican opciones correctas, respuestas ni asignación fija a modelos A/B/C/D.
La numeración impresa de cada modelo sigue siendo independiente.

Ambos campos se declaran juntos. La pareja debe ser única dentro del banco;
las variantes de una familia comparten conceptos, objetivo y dificultad y deben
ser comparables en demanda cognitiva y duración. La comprobación semántica y la
verificación de soluciones corresponden al agente y al docente. Un banco sin
esos campos sigue siendo válido: cada pregunta se considera una principal
independiente, sin inferir parentescos por sus nombres. En catálogos, las familias
se identifican también por el banco para evitar colisiones.

## Selección y equilibrio

Antes de generar modelos, el agente propone al profesor cantidad de preguntas
y reparto razonados según los temas o prácticas, las familias y conceptos
realmente disponibles. Parte de cuatro modelos salvo otra petición. Propone
una duración aproximada con supuestos de lectura, razonamiento, cálculo y
revisión; el tiempo de trasladar respuestas a Moodle se indica aparte. No es
una medición ni una fórmula fija. El profesor puede ajustar cantidad y duración;
el agente revisa la cobertura antes de componer. Se acuerdan también título,
tipos y dificultad. El archivo de selección
recoge el reparto aprobado:

```json
{
  "schema_version": 1,
  "banks": ["historia-fuentes", "actividad-medicion"],
  "quotas": [
    {
      "label": "Interpretación de fuentes",
      "count": 3,
      "concepts": ["interpretar-fuentes"],
      "difficulty": "intermedia",
      "types": ["single", "multiple", "truefalse"]
    },
    {
      "label": "Medición experimental",
      "count": 2,
      "material_ids": ["actividad-medicion"],
      "difficulty": "basica",
      "types": ["numerical", "single"]
    }
  ]
}
```

`count` es un entero positivo; todas las cuotas suman el número de preguntas
solicitado. Las etiquetas son únicas. Una cuota puede omitir cualquiera de los
filtros. Los filtros presentes se cumplen conjuntamente; dentro de cada lista
basta coincidir con uno de sus valores. `material_ids` consulta las referencias
de las preguntas, no el nombre del banco. Los IDs de conceptos y materiales
deben estar declarados en los bancos seleccionados.

La misma pregunta puede cumplir varias cuotas, pero solo se asigna a una y
aparece una vez por modelo. El algoritmo resuelve las cuotas simultáneamente,
por lo que un solapamiento no provoca un fallo falso si existe un reparto
factible. Si las preguntas no alcanzan, el mensaje distingue la cuota insuficiente
del conflicto conjunto. El agente propone ajustar el reparto o ampliar bancos;
la composición nunca inventa nuevas preguntas.

En cada modelo aparece como máximo una variante de cada principal. Entre
modelos se priorizan familias menos utilizadas y después variantes menos
utilizadas, comparando propuestas para reducir el solapamiento. Si el fondo
permite preguntas principales diferentes para todos, se prefieren; si obliga a
reutilizar familias, se prefieren variantes distintas y se informa. No rellenar
con variantes de una familia que ya figura en el mismo modelo. La semilla reproduce la selección y el
orden de opciones. Es una preferencia reproducible, sin garantía de óptimo
global de diversidad. Las cuotas pueden obligar a reutilizar preguntas antes
que otras no elegibles para ese reparto.

Tipos imprimibles: `single`, `multiple`, `truefalse`, `numerical`. Los
emparejamientos se conservan en el banco congelado y se enumeran como excluidos
del examen; no pueden solicitarse como tipo de una cuota.

## Uso de las utilidades y resultados

El agente puede ejecutar las utilidades; el profesor no necesita conocer estos
comandos. Los destinos de resultados deben estar fuera del plugin instalado:

```sh
python scripts/docencia.py validate-catalog /curso/creados/bancos/catalogo.json
python scripts/docencia.py build-exams \
  --catalog /curso/creados/bancos/catalogo.json \
  --selection /curso/creados/cuestionarios/seleccion.json \
  --title "Evaluación de fuentes y medición" \
  --questions 5 --models 4 --seed 42 --layout curso-v2 --output /curso/creados/cuestionarios/parcial-01
```

La entrada antigua de un único GIFT y sus metadatos opcionales sigue disponible.
Los bancos antiguos sin procedencia completa pueden usarse por esa vía; el
agente debe completar sus metadatos antes de ofrecer el equilibrio por materiales
y dificultad del catálogo.

La API Python mantiene `build_exams(bank_path, output_dir, ...)`. Para el
catálogo usa `bank_path=None`, `catalog_path=...`, `selection_path=...` y,
opcionalmente, `project_root=...`. No se mezclan catálogo y selección con un
banco único, metadatos externos o cuotas antiguas por categoría.
`validate_catalog(catalog_path, project_root=None)` devuelve un resumen
serializable con recuentos; las inconsistencias producen `ValueError` y no
modifican los archivos.

En `--layout curso-v2`, la salida contiene `alumnado/` para modelos HTML/PDF
sin soluciones y `docente/` para solucionarios, GIFT, `manifest.json`, `source/`
y `coverage.json`. Las rutas del manifiesto se resuelven desde `docente/`;
los modelos estudiantiles se enlazan con `../alumnado/`. La raíz del examen
contiene `material-docente.json` de tipo `cuestionario` (se admite `examen` en registros anteriores), inicialmente `borrador`, y
`LEEME.md`. Revisar antes de cambiar el estado. Sin esa opción se conserva la
distribución plana anterior. No reorganizar manualmente archivos después de
generar el manifiesto.

Las salidas mantienen PDF estudiantil, solucionario separado, HTML y GIFT
ofuscado. Si falta la capacidad PDF, se conservan fuentes y HTML y se declara
la impresión pendiente. `manifest.json` conserva `schema_version: 1` y los
campos previos `bank_snapshot`, `bank_sha256`, `metadata` y `models`. Añade:

- IDs de pregunta compuestos como `historia-fuentes::carta-01`; los campos
  `source_bank_id` y `source_question_id` conservan ambos identificadores
  originales en cada pregunta y sus metadatos.
- `source_banks`: snapshots y SHA-256 de cada GIFT y sus metadatos originales.
- Copias exactas del catálogo y de la selección, con sus huellas.
- `coverage` por modelo, `quota_label` por pregunta y `selection_report` con
  cobertura, reutilización y coincidencias entre pares de modelos.
- `coverage.json`: copia legible del informe de selección.

`source/bank.gift` contiene el banco combinado con títulos escapados y preguntas
sin categoría al principio para respetar la sintaxis GIFT. Se comprueba que al
releerlo conserva enunciados, categorías, tipos, opciones, pesos, tolerancias y
feedback. Los originales GIFT y JSON también se congelan byte a byte. Los
materiales docentes no se duplican dentro del examen. Modificar los originales
después no altera un examen ya generado.

Estos archivos contienen datos docentes reservados. Solo las salidas identificadas
como estudiantiles se entregan al alumnado. La importación de GIFT no configura
por sí sola el orden de preguntas y respuestas del cuestionario: consulta
[la configuración de Moodle](MOODLE.md).

## Continuidad

Después de validar un banco, ofrecer preparar modelos con la cobertura elegida.
Después de los modelos, orientar a la revisión e importación manual del GIFT;
tras la evaluación, el feedback requiere detalle por pregunta, manifiesto y hoja
Moodle. Si esas salidas ya existen para la misma versión, ofrecer utilizarlas,
revisarlas o actualizarlas según [los flujos docentes](FLUJOS-DOCENTES.md).

La CLI conserva el nombre técnico `build-exams` por compatibilidad. `--models`
vale 4 cuando se omite; `--questions` es obligatorio y refleja la propuesta
acordada. La API `build_exams` conserva su nombre y la entrada antigua. Las
variantes y familias quedan registradas en los metadatos y el manifiesto.

## Leer el informe de diversidad

`validate-catalog` informa `main_questions` (familias o preguntas independientes)
y `questions` (ítems o versiones GIFT). Incluye todos los tipos del catálogo.
`selection_report` indica `available_main_questions` y
`available_question_versions` para el fondo imprimible cargado, no únicamente
los candidatos de una cuota; no interpretar esos totales como cobertura temática
sin aplicar el reparto solicitado. `family_usage` conserva identidad y uso por
modelos. En cada par, `shared_main_questions` cuenta principales compartidas y
`shared_questions` cuenta versiones exactas compartidas.

En un catálogo, `family_id` se identifica como `banco::familia` y
`source_family_id` conserva el ID original; `variant_id` es local a la familia.
Las preguntas sin familia tienen identidad independiente y no colisionan con
una familia que tenga el mismo nombre. El manifiesto conserva estos campos,
conceptos y procedencia para las observaciones posteriores.
