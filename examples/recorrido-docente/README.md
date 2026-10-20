# Del material al feedback: ejemplo de 0.8.0

Todos los materiales, participantes, entregas y calificaciones son **sintéticos**.
Este curso breve reúne humanidades, ciencias y una actividad experimental para
comprobar que las skills no dependen de prácticas de programación.

La [carpeta del curso](curso/LEEME.md) contiene:

- Dos materiales de referencia y una actividad con enunciado, plantilla de
  informe, rúbrica completa y guía docente separadas. Su
  [registro](curso/docente/evaluaciones/medir-y-justificar/actividad.json)
  asocia los documentos a la versión 1.0.0.
- Tres bancos con cuatro preguntas cada uno. Repiten los identificadores
  originales `Q01`–`Q04` entre bancos, y el banco experimental utiliza dos fuentes.
  El [catálogo](curso/docente/evaluaciones/bancos/catalogo.json) enlaza las fuentes
  mediante metadatos con huellas, sin copiarlas.
- Un [reparto](curso/docente/evaluaciones/reparto.json) de seis preguntas:
  una básica y una intermedia de cada ámbito, común a tres modelos. Doce preguntas
  para dieciocho posiciones obligan a reutilizar algunas; el informe lo muestra.
- Un lote grupal identificado explícitamente para dos estudiantes y un caso sin
  entrega. Se ofrecen tanto hoja de tarea como libro de calificaciones, con
  perfiles y evaluaciones correspondientes. Son dos demostraciones alternativas:
  no se deben importar ambas sobre una misma actividad real.

## Probarlo conversando

Copia `curso/` a una carpeta de trabajo fuera de la instalación del plugin.
Pide «Inicia mi proyecto docente» y después «¿Qué puedo hacer ahora?». Se
recomendará el mapa sin crearlo automáticamente. Este ejemplo deja el mapa vacío;
el [ejemplo del mapa](../mapa-docente/README.md) permite probar su navegación.

Para diseñar una actividad nueva puedes pedir:

- «Diseñemos un comentario histórico a partir de los testimonios; quiero
  evaluar contraste de fuentes. Dispongo de 50 minutos».
- «Adapta la actividad experimental para trabajo individual. El alumnado puede
  consultar IA; quiero evidencias de comprensión y un informe con datos reales».

El agente debe preguntar solo por lo que falte, presentar tareas y evidencias
antes de generar documentos y entregar la rúbrica completa al docente. No debe
elegir un notebook para un comentario histórico ni inventar sanciones por IA.

## Reproducir las utilidades

El profesor puede pedir al agente que ejecute este recorrido. Para desarrollo,
desde la raíz del plugin:

```sh
python examples/recorrido-docente/comprobar.py ../demo-0.8
```

El destino debe ser nuevo y estar fuera del plugin. La prueba copia los datos,
valida el catálogo, produce tres exámenes HTML con solucionarios separados y GIFT
ofuscados, exporta ambas hojas de actividad y cruza detalle de examen con un
libro separado para generar feedback. Añadir `--pdf` exige los PDF reales y
necesita las dependencias opcionales y Chromium. El enunciado de la actividad
también se convierte a HTML y, con esa opción, a PDF dentro de su carpeta
`impresion/`; el PDF generado queda asociado en el registro de actividad.

La carpeta resultante incluye:

| Ruta | Resultado |
| --- | --- |
| `curso/` | Fuentes e instrucciones conservadas; ningún mapa creado. |
| `examen/` | HTML/PDF según capacidad, GIFT, manifiesto, bancos congelados e informe de cobertura. |
| `correccion-tarea/`, `correccion-libro/` | Copias para Moodle e informes con cálculos y auditoría. |
| `detalle-examen.csv`, `libro-examen.csv`, `perfil-feedback.json` | Entradas explícitas para reproducir el cruce. |
| `feedback/` | Un CSV por modelo, conservando las notas e indicando dificultades y repaso. |
| `comprobacion.json` | Resumen del recorrido y conservación de originales. |

La actividad evaluada obtiene **8,75/10**: registro 4/4 e interpretación 3/4,
cada criterio con peso del 50 %. La persona sin entrega conserva sus celdas
previas. En el examen se simulan dos fallos de crítica de fuentes y una evidencia
aislada en medición: el primero se considera dificultad acusada, el segundo
aspecto a revisar. Las notas del libro se conservan literalmente; la persona no
presentada recibe comentario vacío.

No se han subido estos archivos a Moodle. Antes de una importación real, revisar
el perfil, los identificadores y la vista previa según la [guía de Moodle](../../docs/MOODLE.md).
