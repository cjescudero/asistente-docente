# Dos preguntas principales y cuatro variantes

Ejemplo sintético de ciencias y humanidades: dos familias, cuatro variantes
por familia y ocho ítems GIFT. Se proponen dos preguntas por modelo porque este
material mínimo desarrolla dos actuaciones: calcular una media y delimitar el
alcance de una fuente. No es una recomendación de extensión para un curso real.

El banco se conserva como [GIFT](banco.gift) y [metadatos JSON](metadatos.json)
individuales, sin ZIP. El GIFT contiene las preguntas; el JSON relaciona sus
variantes con conceptos y fuentes.

La principal `01` tiene las variantes `01-A`, `01-B`, `01-C` y `01-D`;
la principal `02`, `02-A` a `02-D`. Los metadatos conservan `family_id` numérico
y `variant_id` en letra. Esas letras no son las opciones de respuesta.

Duración orientativa para este ejemplo: 4–6 minutos entre lectura, cálculo,
razonamiento y revisión, ajustable al nivel y necesidades del alumnado. El
registro posterior de respuestas en Moodle requiere un tiempo aparte.

Desde la raíz del plugin, guardar resultados fuera de la instalación:

```sh
python scripts/docencia.py validate-catalog examples/cuestionarios-variantes/catalogo.json
mkdir -p ../demo-variantes/_datos_internos
cp examples/cuestionarios-variantes/seleccion.json ../demo-variantes/_datos_internos/seleccion.json
python scripts/docencia.py build-cuestionarios --catalog examples/cuestionarios-variantes/catalogo.json --selection ../demo-variantes/_datos_internos/seleccion.json --questions 2 --output ../demo-variantes --title "Fuentes y medición" --layout curso-v3 --html-only
```

Al omitir `--models`, se crean cuatro modelos. Cada uno contiene una variante de
cada principal; las cuatro variantes se agotan antes de repetir una. Los modelos
son distintos en sus ítems, pero comparten las dos principales: `coverage.json`
permite comprobarlo sin confundir variantes con diversidad de conocimientos.
Retirar `--html-only` cuando exista capacidad PDF. Los HTML no equivalen a PDF.

Para comprobar diversidad de principales cuando sobran familias, las pruebas
sintéticas de selección utilizan ocho principales y cuatro modelos de dos
preguntas; verifican que no se repiten principales entre modelos.
