---
name: bancos-preguntas-creacion
description: Crear, ampliar y revisar bancos GIFT asociados a materiales o actividades de cualquier asignatura, con procedencia, objetivos, conceptos y dificultad para combinar después en evaluaciones. No usar para corregir entregas, generar feedback posterior ni preparar por sí sola los modelos impresos.
---

# Bancos de preguntas: creación

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

En `curso-v2`, guardar cada banco nuevo en `creados/bancos/<id>/` y registrarlo
en `creados/bancos/catalogo.json`. Su `material-docente.json` de tipo `banco`
y `LEEME.md` muestran el estado; un borrador permanece en esa carpeta al revisarse.
El catálogo admite `path_base: "project"` para enlazar bancos aportados en
`fuentes/evaluaciones/bancos/` y creados, sin copiarlos ni moverlos. Conservar los
catálogos y rutas de cursos anteriores salvo migración aprobada. El banco y sus
metadatos completos son docentes aunque algunas fuentes sean estudiantiles.

## Flujo

1. Identificar los materiales concretos o actividades que sustentan el banco: diapositivas, apuntes, ejercicios, talleres u otros. Leer las fuentes autorizadas y delimitar audiencia, objetivos y uso. Consultar el mapa para localizar evidencia, sin tratar su resumen como sustituto de la fuente.
2. Preguntar por ejemplos de bancos o exámenes anteriores si ayudan a acordar estilo y dificultad. Registrar su papel de inspiración; el contenido y los criterios del curso vigente determinan lo evaluable. Preparar con el profesor el reparto por objetivos, categorías y dificultad estimada; no imponer cuotas ni convertir todos los temas en memorización.
3. Redactar preguntas autónomas. Incluir los datos necesarios, definir siglas poco conocidas y evitar referencias como «en el taller» si el documento no estará disponible. No regalar una fórmula si identificarla es precisamente lo evaluado.
4. Redactar opciones comparables y distractores basados en errores plausibles. Evitar pistas por longitud, concordancia o repetición; comprobar que una selección única tiene una sola respuesta correcta bajo las condiciones expresadas.
5. Asignar identificadores estables al banco y únicos dentro de él a las preguntas. Especificar pesos, soluciones y tolerancias. Cada banco nuevo debe tener metadatos: materiales de origen y localizadores, conceptos, objetivos, dificultad estimada y orientaciones de repaso. Una pregunta puede basarse en varias fuentes. Las recomendaciones dirigidas al alumnado solo deben enlazar materiales accesibles para él.
6. Guardar GIFT UTF-8 y metadatos conforme al [catálogo de bancos](../../docs/BANCOS.md). Validar el GIFT y el catálogo mediante las utilidades documentadas allí; comprobar que sus rutas relativas resuelven los originales. Revisar el [perfil GIFT](references/gift.md). `ASISTENTE_DOCENTE` identifica la raíz instalada; las entradas y salidas pertenecen al curso, fuera del plugin.
7. Revisar una muestra de cada tipo, dificultad y categoría, y todas las preguntas ambiguas. La validación sintáctica no verifica la verdad ni la calidad didáctica. Entregar GIFT, metadatos, entrada del catálogo y una nota de cobertura, calibración e incidencias.

## Soporte y límites

El banco admite selección única, selección múltiple, verdadero/falso, numéricas y emparejamiento. El flujo de papel y respuestas ofuscadas no admite emparejamiento en esta versión; no convertirlo silenciosamente a otro tipo.

Un banco anterior sin metadatos sigue siendo legible. Identificar qué procedencia
o dificultad falta y proponer completarla antes de prometer una composición
equilibrada basada en esos datos. No inventar etiquetas para que pase la validación.

Para crear los modelos impresos y su GIFT ofuscado, continuar con [preparar exámenes](../evaluaciones-preparacion-modelos/SKILL.md). No entregar a estudiantes el banco docente con soluciones codificadas.

## Sugerir el siguiente paso

Aplicar el [cierre contextual de los flujos](../../docs/FLUJOS-DOCENTES.md):
proponer de uno a tres pasos pertinentes basados en resultados comprobados,
sin iniciar otra tarea por el mero hecho de sugerirla. Proponer modelos impresos con el banco validado y los demás bancos pertinentes. Si ya existen modelos, ofrecer revisarlos o, con resultados detallados, manifiesto y hoja Moodle, preparar su feedback.
