---
name: cuestionarios-bancos-preguntas-creacion
description: Crear, ampliar y revisar bancos GIFT asociados a materiales o actividades de cualquier asignatura, con preguntas principales y variantes, procedencia, objetivos, conceptos y dificultad para combinar después en cuestionarios. No usar para corregir entregas, generar feedback posterior ni preparar por sí sola los modelos impresos.
---

# Cuestionarios: creación de bancos de preguntas

Construir un banco cuya cobertura, dificultad y soluciones puedan revisar el profesor. El formato de Moodle es **GIFT**, no GIF.

Usar por defecto [español conciso](../espanol-conciso-redaccion/SKILL.md) en la
conversación y los documentos, salvo que el profesor indique otro idioma o estilo.
Respetar citas, identificadores y términos que deban conservarse literalmente.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

Ante dudas sobre el uso, flujo, archivos o resultados del plugin, o preguntas
sobre siguientes pasos y posibilidades, invocar
[Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) antes de responder.
Transferirle el objetivo, las decisiones conocidas y los resultados de esta tarea;
tras resolver la duda, retomar el encargo ya autorizado.

En `curso-v3`, guardar cada banco nuevo en `materiales_generados/bancos/<id>/` y registrarlo
en `materiales_generados/bancos/_datos_internos/catalogo.json`. Sus metadatos y
`material-docente.json` van en `<id>/_datos_internos/`; el registro de tipo `banco`
y `LEEME.md` muestran el estado; un borrador permanece en esa carpeta al revisarse.
El catálogo admite `path_base: "project"` para enlazar bancos aportados en
`fuentes/evaluaciones/bancos/` y creados, sin copiarlos ni moverlos. El banco y sus
metadatos completos son docentes aunque algunas fuentes sean estudiantiles.

## Archivos de entrega

Guardar el banco como **archivos normales en su carpeta de trabajo**: `banco.gift`,
`_datos_internos/metadatos.json`, `_datos_internos/material-docente.json` y `LEEME.md`, además de actualizar la
entrada del catálogo. Entregar enlaces directos al GIFT y a los metadatos;
identificar el GIFT como archivo de preguntas para Moodle y los JSON como apoyo
docente. No crear ni entregar un ZIP por defecto. Comprimir solo si el profesor
lo pide o una limitación comprobada de la entrega lo exige; explicar esa limitación
y mantener disponibles los archivos individuales. Un ZIP para distribuir el plugin
es un artefacto distinto del banco de preguntas.

## Proponer cobertura, cantidad y variantes

Distinguir **pregunta principal** (familia que evalúa una actuación concreta) y
**variante** (otra instancia equivalente de esa pregunta). Contar por separado
las familias, las variantes por familia y las preguntas GIFT totales. Cambiar
solo el orden de opciones no crea una variante de contenido.

Antes de redactar el banco completo, identificar los conceptos y objetivos de
los materiales seleccionados. Proponer al profesor una cantidad de preguntas
principales con un reparto por conceptos, importancia, complejidad y actuaciones
que evaluar. Explicar por qué esa cantidad ofrece cobertura suficiente; no usar
una cifra fija ni una pregunta por cada concepto de manera mecánica. Mostrar las
carencias de cobertura si el profesor prefiere una cantidad menor y ajustar el
reparto si solicita más. Reutilizar una cantidad ya acordada.

El punto de partida son **cuatro modelos** de cuestionario, salvo otra indicación.
Proponer **hasta cuatro variantes equivalentes por principal** para ese uso,
concretando cuáles aportan diversidad válida. El profesor puede pedir otro
número; no forzar variantes que los materiales no permitan justificar. Explicar
el tamaño: por ejemplo, 10 principales × 4 variantes = 40 preguntas GIFT, no
40 conocimientos diferentes. Cuatro variantes facilitan modelos distintos, pero
no garantizan que sus preguntas principales sean diferentes.

Cada variante debe mantener objetivo, conceptos, dificultad estimada, demanda
cognitiva y tiempo comparable. Variar datos, casos o contextos sustentados por
las fuentes; revisar su resolución y distractores independientemente. No crear
variantes que solo cambien palabras o que revelen otra respuesta del modelo.

Identificar cada principal con un número estable dentro del banco y cada
variante con una letra mayúscula: `01-A`, `01-B`, `01-C`, `01-D`; después
`02-A`, `02-B`, etc. Usar el identificador completo como título GIFT
(`::01-A::`) y clave de `questions`. Registrar `family_id: "01"` y
`variant_id: "A"` según [Bancos](../../docs/BANCOS.md). Una principal con una
sola variante usa `01-A`. Ampliar a `AA`, `AB`… si se necesitan más de 26;
a partir de 100 principales, continuar `100-A` sin renumerar las anteriores.
Las letras de variante no son letras de opciones de respuesta ni el modelo
impreso. Mantener números y letras al ampliar o reordenar el banco; los números
retirados no se reutilizan para otra principal. No renumerar bancos anteriores
ni snapshots ya utilizados por aplicar esta convención. No
inferir familias por semejanza de nombres de bancos históricos. Documentar la
cantidad propuesta, la acordada y los límites de diversidad del fondo disponible.

## Flujo

1. Identificar los materiales concretos o actividades que sustentan el banco: diapositivas, apuntes, ejercicios, talleres u otros. Leer las fuentes autorizadas y delimitar audiencia, objetivos y uso. Consultar el mapa para localizar evidencia, aprovechando su explicación como contexto. Consultar los originales necesarios para redactar y verificar respuestas, localizadores y ambigüedades, sin releer por sistema materiales ya suficientemente documentados.
2. Preguntar por ejemplos de bancos o cuestionarios anteriores si ayudan a acordar estilo y dificultad. Registrar su papel de inspiración; el contenido y los criterios del curso vigente determinan lo evaluable. Preparar con el profesor el reparto por objetivos, categorías y dificultad estimada; no imponer cuotas ni convertir todos los temas en memorización.
3. Redactar preguntas autónomas. Incluir los datos necesarios, definir siglas poco conocidas y evitar referencias como «en el taller» si el documento no estará disponible. No regalar una fórmula si identificarla es precisamente lo evaluado.
4. Redactar opciones comparables y distractores basados en errores plausibles. Evitar pistas por longitud, concordancia o repetición; comprobar que una selección única tiene una sola respuesta correcta bajo las condiciones expresadas.
5. Asignar identificadores estables al banco y únicos dentro de él a las preguntas. Especificar pesos, soluciones y tolerancias. Cada banco nuevo debe tener metadatos: materiales de origen y localizadores, conceptos, objetivos, dificultad estimada y orientaciones de repaso. Una pregunta puede basarse en varias fuentes. Las recomendaciones dirigidas al alumnado solo deben enlazar materiales accesibles para él.
6. Guardar GIFT UTF-8 y metadatos conforme al [catálogo de bancos](../../docs/BANCOS.md). Validar el GIFT y el catálogo mediante las utilidades documentadas allí; comprobar que sus rutas relativas resuelven los originales. Revisar el [perfil GIFT](references/gift.md). `ASISTENTE_DOCENTE` identifica la raíz instalada; las entradas y salidas pertenecen al curso, fuera del plugin.
7. Revisar una muestra de cada tipo, dificultad y categoría, y todas las preguntas ambiguas. La validación sintáctica no verifica la verdad ni la calidad didáctica. Entregar enlaces individuales al GIFT y los metadatos, la entrada del catálogo y una nota de cobertura, calibración e incidencias; informar cantidades de principales y variantes y no comprimir por defecto.

## Soporte y límites

El banco admite selección única, selección múltiple, verdadero/falso, numéricas y emparejamiento. El flujo de papel y respuestas ofuscadas no admite emparejamiento en esta versión; no convertirlo silenciosamente a otro tipo.

Un banco anterior sin metadatos sigue siendo legible. Identificar qué procedencia
o dificultad falta y proponer completarla antes de prometer una composición
equilibrada basada en esos datos. No inventar etiquetas para que pase la validación.

Para crear los modelos impresos y su GIFT ofuscado, continuar con [crear modelos de cuestionario](../cuestionarios-modelos-imprimir-evaluar/SKILL.md). No entregar a estudiantes el banco docente con soluciones codificadas.

## Sugerir el siguiente paso

Invocar [Proyecto docente: ayuda](../proyecto-docente-ayuda/SKILL.md) para preparar
el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md), una sola vez
por respuesta y reutilizando el contexto y las comprobaciones disponibles:
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Proponer modelos impresos con el banco validado y los demás bancos pertinentes. Si ya existen modelos, ofrecer revisarlos o, con resultados detallados, manifiesto y hoja Moodle, preparar su feedback.
