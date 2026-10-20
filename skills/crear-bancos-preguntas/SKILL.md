---
name: crear-bancos-preguntas
description: Crear, ampliar y revisar bancos GIFT asociados a materiales o actividades de cualquier asignatura, con procedencia, objetivos, conceptos y dificultad para combinar después en evaluaciones. No usar para corregir entregas, generar feedback posterior ni preparar por sí sola los modelos impresos.
---

# Crear bancos de preguntas

Construir un banco cuya cobertura, dificultad y soluciones puedan revisar el profesor. El formato de Moodle es **GIFT**, no GIF.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

En un curso inicializado, preparar borradores en `docente/borradores/` salvo
destino explícito. Registrar los bancos incorporados al curso en el catálogo de
`docente/evaluaciones/bancos/`, conservando una sola ubicación de sus archivos.
El catálogo enlaza los materiales originales; no los copia junto al banco.

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

Para crear los modelos impresos y su GIFT ofuscado, continuar con [preparar exámenes](../preparar-examenes-papel-moodle/SKILL.md). No entregar a estudiantes el banco docente con soluciones codificadas.
