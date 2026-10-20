---
name: crear-bancos-preguntas
description: Crear, ampliar y revisar bancos de preguntas GIFT para Moodle a partir de objetivos y materiales de cualquier asignatura, con categorías y metadatos conceptuales. No usar para evaluar entregas, generar feedback posterior ni preparar por sí sola los modelos de examen impresos.
---

# Crear bancos de preguntas

Construir un banco cuya cobertura, dificultad y soluciones puedan revisar el profesor. El formato de Moodle es **GIFT**, no GIF.

## Contexto del proyecto

Aplicar el [contrato común del proyecto](../../docs/PROYECTO-DOCENTE.md) solo en
lo necesario para el encargo: respetar selección y exclusiones, consultar el
índice del mapa existente y comprobar las entradas requeridas. Un texto o
adjuntos suficientes permiten avanzar sin exigir una wiki ni carpetas llenas.
No incorporar entradas de este encargo al corpus automáticamente.

En un curso inicializado, preparar nuevos materiales en `docente/borradores/`
salvo destino explícito. Pasarlos a `alumnado/` requiere un encargo que incluya
esa entrega; mantener soluciones y criterios docentes separados.

## Flujo

1. Leer las fuentes autorizadas y delimitar contenidos, audiencia, objetivos y uso: práctica, autoevaluación o examen. Usar materiales anteriores solo como fuente complementaria cuando el profesor lo permita; no heredar contenido fuera del temario actual.
2. Preparar un reparto por objetivos y categorías. Variar operaciones cognitivas cuando el curso lo requiera: reconocer, interpretar, aplicar, comparar o justificar. No inventar cuotas ni convertir todos los temas en memorización.
3. Redactar preguntas autónomas. Incluir los datos necesarios, definir siglas poco conocidas y evitar referencias como «en el taller» si el documento no estará disponible. No regalar una fórmula si identificarla es precisamente lo evaluado.
4. Redactar opciones comparables y distractores basados en errores plausibles. Evitar pistas por longitud, concordancia o repetición; comprobar que una selección única tiene una sola respuesta correcta bajo las condiciones expresadas.
5. Asignar identificadores únicos y estables. Especificar pesos, soluciones y tolerancias, con explicación docente cuando se disponga de ella. Vincular conceptos y consejos de repaso en metadatos JSON para el feedback posterior.
6. Guardar GIFT UTF-8 y validar con `python "$ASISTENTE_DOCENTE/scripts/docencia.py" validate-bank banco.gift`. Revisar el [perfil GIFT](references/gift.md) y el [contrato de datos](../../docs/CONTRATOS.md). `ASISTENTE_DOCENTE` identifica la raíz instalada; el banco pertenece al espacio del curso, fuera del plugin. Véase [uso](../../docs/USO.md).
7. Revisar una muestra de cada tipo y categoría, y todas las preguntas ambiguas. La validación sintáctica no verifica la verdad ni la calidad didáctica. Entregar banco, metadatos si se crearon y una nota de cobertura e incidencias.

## Soporte y límites

El banco admite selección única, selección múltiple, verdadero/falso, numéricas y emparejamiento. El flujo de papel y respuestas ofuscadas no admite emparejamiento en esta versión; no convertirlo silenciosamente a otro tipo.

Para crear los modelos impresos y su GIFT ofuscado, continuar con [preparar exámenes](../preparar-examenes-papel-moodle/SKILL.md). No entregar a estudiantes el banco docente con soluciones codificadas.
