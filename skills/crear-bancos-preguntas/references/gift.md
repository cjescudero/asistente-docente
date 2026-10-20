# Perfil GIFT y revisión didáctica

## Autoría

Separar preguntas con una línea en blanco, usar títulos `::identificador::` únicos y categorías `$CATEGORY:` explícitas. Usar UTF-8. Escapar los caracteres de control GIFT cuando sean texto literal; no hacer sustituciones globales sobre un banco ya escapado. La utilidad `validate-bank` detecta los errores de formato que admite el parser del plugin y rechaza entradas incompatibles; no equivale a una importación real en Moodle.

Ejemplo sintético de selección única:

```gift
$CATEGORY: Métodos de investigación/Fuentes

::fuentes-001::¿Qué actuación ayuda a valorar el contexto de una fuente histórica? {
~Contar únicamente sus palabras.
=Identificar quién la produjo, cuándo y con qué propósito.
~Suponer que todos sus testimonios son neutrales.
}
```

Para selección múltiple, definir explícitamente los porcentajes positivos y, cuando correspondan, los negativos conforme al criterio del curso. No suponer que toda respuesta que empieza por `~` es completamente incorrecta: puede llevar crédito parcial. En numéricas, conservar valor o intervalo, tolerancia y peso.

## Formato y matemáticas

Usar texto claro o `[html]` con HTML simple: párrafos, listas, énfasis, tablas pequeñas, subíndices, superíndices y entidades. Para fórmulas, el motor PDF admite `\(...\)` en línea y `\[...\]` en bloque mediante MathJax local; no usa `$` como delimitador. El perfil incorpora `base`, `ams` y `newcommand`, sin carga dinámica de extensiones. Los errores matemáticos bloquean el PDF y conservan el HTML. Verificar por separado el filtro matemático de Moodle: una fórmula que se ve como código literal no está renderizada.

Las llaves, signos y barras de una expresión matemática pueden coincidir con la sintaxis GIFT. Validar su recorrido completo desde banco a examen; no reemplazar fórmulas por imágenes generadas mediante IA.

## Metadatos para el aprendizaje

Los metadatos se guardan aparte del GIFT y siguen el [contrato](../../../docs/CONTRATOS.md). Una pregunta puede vincular varios conceptos, un objetivo y una orientación de repaso; cada concepto puede tener una etiqueta y un consejo general. Escribir consejos accionables sin revelar el examen: «Contrasta la procedencia y el propósito de las fuentes» resulta más útil que «La opción B era la correcta».

Sin metadatos suficientes, informar de esa carencia. No atribuir a un error un concepto ni una causa psicológica que los datos no sostengan.

## Control didáctico

Comprobar cobertura, precisión, datos suficientes, distractores, sesgos irrelevantes para el objetivo y carga de lectura. En preguntas numéricas, resolver independientemente y revisar unidades y tolerancias. En preguntas interpretativas, delimitar el marco que hace defendible la solución. Registrar las dudas para revisión docente; no ocultarlas tras una validación de formato correcta.
