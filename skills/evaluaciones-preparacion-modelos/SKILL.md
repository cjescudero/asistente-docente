---
name: evaluaciones-preparacion-modelos
description: Combinar bancos GIFT de materiales o actividades para preparar modelos de examen equilibrados, PDF de estudiante, solucionarios y GIFT ofuscados coherentes con su manifiesto Moodle. Usar también con un único banco. No inventar preguntas durante la composición ni importar automáticamente en Moodle.
---

# Evaluaciones: preparación modelos a partir de bancos de preguntas

Generar todos los derivados desde una única representación ordenada del modelo: pregunta impresa, opción visible, puntuación y correspondencia Moodle deben coincidir.

Usar por defecto [español conciso](../espanol-conciso-redaccion/SKILL.md) en la
conversación y los documentos, salvo que el profesor indique otro idioma o estilo.
Respetar citas, identificadores y términos que deban conservarse literalmente.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

En `curso-v2`, guardar cada evaluación en `creados/examenes/<id>/`, con modelos
imprimibles en `alumnado/` y solucionarios, GIFT, manifiesto y snapshots en
`docente/`. Mantener `material-docente.json` y `LEEME.md` con el estado visible
en la raíz del examen. Conservar rutas coherentes con el manifiesto y las
utilidades. Respetar destinos explícitos y cursos anteriores según el contrato.

## Flujo

1. Recuperar lo ya conocido y preguntar únicamente por lo que falte: título, temas o actividades que evaluar, número de preguntas y modelos, tipos admitidos, dificultad y restricciones. No asumir cantidades fijas ni una asignatura técnica.
2. Localizar los bancos asociados a esos materiales en el [catálogo](../../docs/BANCOS.md), validar sus archivos y leer sus objetivos y metadatos. Preparar un reparto de cobertura y dificultad común a todos los modelos y presentarlo al profesor antes de generar. Un banco anterior puede usarse como entrada única; si faltan metadatos, solicitar completarlos antes de prometer equilibrio por contenido o dificultad.
3. Comprobar disponibilidad para cada cuota. La selección debe ser reproducible mediante semilla, sin duplicados dentro de un modelo y con preferencia por preguntas menos usadas y menor solapamiento. El informe expresa el equilibrio y reutilización obtenidos; no afirmar que sean un óptimo matemático. Ante un fondo insuficiente, proponer ajustar el reparto o ampliar bancos con la skill correspondiente. No relajar cuotas ni inventar preguntas durante la composición.
4. Preparar una salida nueva fuera del plugin y usar `build-exams` con el catálogo y selección acordados conforme a [Bancos y composición](../../docs/BANCOS.md). En `curso-v2` añadir `--layout curso-v2`, que crea `alumnado/` y `docente/`, y conservar sus rutas relativas; no reorganizar archivos después de generar el manifiesto. Se conserva la entrada de un GIFT: `python "$ASISTENTE_DOCENTE/scripts/docencia.py" build-exams banco.gift --metadata metadatos.json --output examen --title "Evaluación de fuentes" --models 2 --questions 5 --seed 42 --layout curso-v2`. Localizar la raíz instalada en `ASISTENTE_DOCENTE`; resolver entradas y salidas en el curso.
5. Conservar todos los bancos utilizados congelados, sus huellas, metadatos y manifiesto junto con los modelos. La procedencia distingue banco y pregunta original aunque dos bancos reutilicen un mismo título GIFT. No reconstruir categorías, numeración, opciones ni pesos por semejanza de texto o leyendo solo un PDF.
6. Revisar cada modelo: número y orden de preguntas, letras, unidades, fórmulas, saltos de página y legibilidad. Contrastar papel, solucionario y GIFT con el manifiesto. La respuesta correcta debe permanecer en su posición, también en verdadero/falso y selección múltiple.
7. Entregar PDF de estudiante y solucionario en archivos claramente separados, GIFT ofuscado, manifiesto e informe de cobertura, dificultad y reutilización. Los HTML son derivados útiles para inspección; `--html-only` no completa una petición de PDF.
8. Explicar la importación y configuración manual de [Moodle](../../docs/MOODLE.md): sin barajar preguntas ni respuestas, y sin revelar soluciones o feedback durante la evaluación. Verificar el cuestionario con una cuenta o vista de estudiante antes de usarlo.

## Límites que conservar

- El GIFT ofuscado muestra únicamente números y etiquetas de respuesta. El archivo sigue conteniendo pesos y claves para Moodle; es material docente, no un archivo para entregar a estudiantes.
- En verdadero/falso se generan dos opciones de selección única en el orden impreso. En preguntas numéricas se conserva entrada numérica, valor esperado y tolerancia; no inventar letras para ellas.
- Emparejamiento queda fuera del flujo ofuscado de esta versión. Revisar y comunicar los identificadores excluidos antes de dar la selección por válida.
- Tras aplicar el examen, el feedback debe usar su manifiesto y snapshot, aunque el banco de trabajo haya cambiado.
- La ofuscación reduce la información mostrada en pantalla; no demuestra por sí sola ausencia de consulta externa o de uso de IA.

Consultar [uso](../../docs/USO.md) para rutas, dependencias y comprobaciones. Para resultados posteriores, usar [generar feedback](../evaluaciones-observaciones-alumnado/SKILL.md).

## Sugerir el siguiente paso

Aplicar el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md):
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Proponer revisar los modelos y la configuración de Moodle; el siguiente paso posterior al examen es añadir feedback con detalle por pregunta, manifiesto y hoja Moodle. Si ya están disponibles, ofrecer ese encargo sin regenerar modelos.
