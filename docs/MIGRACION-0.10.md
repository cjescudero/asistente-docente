# Migración a 0.10.0

La versión 0.10.0 se publica conservando la release anterior 0.9.0. Instalar una nueva
versión no reorganiza cursos ni modifica cuestionarios usados automáticamente.

## Skills agrupadas como cuestionarios

| Identificador de 0.9.0 | Identificador actual | Nombre visible |
| --- | --- | --- |
| `bancos-preguntas-creacion` | `cuestionarios-bancos-preguntas-creacion` | Cuestionarios: creación de bancos de preguntas |
| `evaluaciones-observaciones-alumnado` | `cuestionarios-observaciones-calificaciones-alumnado` | Cuestionarios: observaciones sobre calificaciones para el alumnado |
| `evaluaciones-preparacion-modelos` | `cuestionarios-modelos-imprimir-evaluar` | Cuestionarios: creación de modelos para imprimir y evaluar |

Son equivalencias documentadas, sin alias duplicados del anfitrión. Actualizar
referencias operativas durante una adaptación solicitada y consultar conflictos.
No modificar instalaciones anteriores ni instrucciones globales.

## Rutas y registros

En cursos nuevos, `fuentes/evaluaciones/examenes/` pasa a
`fuentes/evaluaciones/cuestionarios/` y `creados/examenes/` pasa a
`creados/cuestionarios/`. Los cursos existentes conservan sus rutas hasta una
propuesta aprobada, comprobando colisiones, enlaces, selecciones y registros.
`questionnaire_paths` declara los destinos del curso-v2 nuevo o migrado. Su
ausencia conserva las rutas antiguas. El tipo de material nuevo es `cuestionario`;
`examen` sigue siendo válido en registros existentes.

## Bancos y modelos

Los bancos anteriores siguen admitidos y no se inventan familias. Para registrar
variantes, revisar cada pregunta y añadir `family_id` y `variant_id` a sus
metadatos, conservando los IDs GIFT. No modificar snapshots de cuestionarios ya
utilizados. La selección imprime como máximo una variante de cada familia por
modelo, prioriza principales diferentes y conserva cuotas y semilla.

El valor predeterminado de modelos pasa de 2 a 4 en las utilidades. Indicar
`--models 2` si se requiere el comportamiento anterior. La CLI requiere ahora
`--questions`: el agente propone y razona la cantidad y duración antes de
invocarla. Se conserva el nombre técnico `build-exams` y la API `build_exams`.
La cantidad de preguntas de la API conserva su valor anterior por compatibilidad;
el flujo de la skill siempre pasa la cantidad acordada explícitamente.

## Mapas existentes

La nueva instrucción crea explicaciones suficientes para comprender los conceptos
sin abrir cada fuente. Mejorar una wiki anterior exige un encargo de actualización
y lectura suficiente; mostrar o regenerar HTML no reescribe sus páginas. Mantener
acceso reservado y estados de lectura, sin llenar vacíos con supuestos.
