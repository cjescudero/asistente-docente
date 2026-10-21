# Puntuación de los cuestionarios

Valores predeterminados para bancos nuevos, salvo indicación del docente. Cada
pregunta vale como máximo 1 punto; una respuesta en blanco vale 0.

| Tipo | Criterio |
| --- | --- |
| Opción única | +1 por acierto; −0,5 por respuesta incorrecta. |
| Selección múltiple | Si hay N opciones correctas y L incorrectas: +1/N por cada correcta marcada y −1/L por cada incorrecta marcada. Las no marcadas no suman ni restan. |
| Verdadero/falso | +1 por acierto y 0 por error. |
| Numérica | +1 dentro del valor o tolerancia aceptados; 0 fuera. |
| Emparejamiento | Para P pares solicitados: +1/P por par correcto, −1/P por par incorrecto y 0 por par sin responder. |

En múltiple, N cuenta las opciones correctas, no todas las opciones ofrecidas.
Con cuatro correctas, marcar una aporta 0,25. Marcar todas las correctas sin
incorrectas da 1; marcar todas las incorrectas sin correctas da −1. Sumar ambos
componentes cuando se mezclan aciertos y errores. En emparejamiento el denominador
es el número de pares solicitados, no todas las combinaciones posibles.

## Banco, papel y Moodle

Codificar selección única con `=Correcta` y `~%-50%Incorrecta`. En múltiple,
usar `~%100/N%` y `~%-100/L%`, sustituyendo las divisiones por valores numéricos;
comprobar redondeo y que los positivos suman 100 y los negativos −100.
Verdadero/falso y numéricas usan crédito completo o cero. No sustituir pesos
explícitos de bancos aportados silenciosamente: contrastarlos con este criterio,
informar de diferencias y preparar una adaptación antes de componer si procede.
Conservar siempre originales y snapshots de cuestionarios utilizados.

**Pesos negativos y nota final son cosas distintas.** Moodle admite pesos negativos
en GIFT, tanto en opción única como múltiple. Por ejemplo, cuatro opciones de
+25 % y una de −50 % suman 50 % al marcarlas todas; seleccionar solo la negativa
produce una suma de −50 %, que Moodle estándar limita a cero en múltiple.
Estos pesos de ejemplo no sustituyen los valores predeterminados de arriba.

**Configuración docente de Moodle:** GIFT no configura la puntuación máxima ni el comportamiento
del cuestionario. Establecer 1 punto por pregunta y comprobar la escala final.
La [selección múltiple estándar](https://docs.moodle.org/en/Multiple_Choice_question_type)
limita a cero un total negativo por pregunta; los pesos negativos no garantizan
que se descuente del total del cuestionario. La selección única con nota negativa
requiere un comportamiento compatible, como retroalimentación diferida.
El [emparejamiento estándar](https://docs.moodle.org/en/Matching_question_type)
y su GIFT no codifican la penalización proporcional aquí solicitada.
No confundir estas deducciones con penalizaciones por reintentos.

Si se necesita la puntuación neta negativa en múltiple o emparejamiento, comunicar
la incompatibilidad y acordar un mecanismo de calificación compatible o un cálculo
externo explícito antes del uso. No prometer que importar GIFT basta ni cambiar el
criterio a cero sin avisar. Emparejamiento sigue fuera del circuito impreso actual.
El feedback posterior conserva las notas de Moodle: no recalcularlas por su cuenta.

## Presentación impresa

Separar visualmente título, modelo e identificación de las instrucciones mediante
líneas y espacio. Indicar por pregunta si se responde con una opción, varias o un
valor numérico; nunca imponer una sola opción a todo un cuestionario mixto.
Explicar puntuación y blancos, usando los pesos reales del banco, no una frase fija
«sin penalización». Si los pesos son especiales, detallarlos sin revelar la clave.
Comprobar el comportamiento efectivo de Moodle antes de entregar el papel y ajustar
las instrucciones a lo acordado. Revisar cortes de página y mantener cada pregunta
con sus opciones. No incluir soluciones en el documento del alumnado.

Las advertencias técnicas sobre importación, mínimos y comportamientos quedan en
la guía docente. El papel del alumnado contiene el criterio efectivo acordado,
sin solicitudes de confirmar configuraciones ni avisos técnicos de Moodle.
