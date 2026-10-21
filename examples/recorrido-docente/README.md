# Del material al feedback: ejemplo con organización curso-v2

Todos los materiales, participantes, entregas y calificaciones son **sintéticos**.
Este curso breve reúne humanidades, ciencias y una actividad experimental para
comprobar que las skills no dependen de prácticas de programación.

La [carpeta del curso](curso/LEEME.md) contiene:

- Dos materiales aportados en `fuentes/teoria/` y una actividad creada con enunciado, plantilla de
  informe, rúbrica completa y guía docente separadas. Su
  [registro reservado](curso/creados/actividades/medir-y-justificar/docente/actividad.json)
  asocia los documentos a la versión 1.0.0. La carpeta estable de la actividad
  contiene `alumnado/` y `docente/`; `material-docente.json` y `LEEME.md`
  indican su estado `listo-para-entregar`.
- Tres bancos con cuatro preguntas cada uno. Repiten los identificadores
  originales `Q01`–`Q04` entre bancos, y el banco experimental utiliza dos fuentes.
  El banco histórico de humanidades permanece en
  `fuentes/evaluaciones/bancos/humanidades-2025-2026/`; los bancos nuevos de ciencias
  y de la actividad están en `creados/bancos/`, con estado `revisado`.
  El [catálogo](curso/creados/bancos/catalogo.json) utiliza rutas relativas a la
  raíz del curso (`path_base: project`) para enlazarlos sin duplicarlos. Los
  metadatos también enlazan las fuentes con sus huellas de integridad.
- Un [reparto](curso/creados/bancos/reparto-ejemplo.json) de seis preguntas:
  una básica y una intermedia de cada ámbito, común a tres modelos. Doce preguntas
  para dieciocho posiciones obligan a reutilizar algunas; el informe lo muestra.
- Un lote grupal identificado explícitamente para dos estudiantes y un caso sin
  entrega. Se ofrecen tanto hoja de tarea como libro de calificaciones, con
  perfiles y evaluaciones correspondientes. Son dos demostraciones alternativas:
  no se deben importar ambas sobre una misma actividad real.

La configuración selecciona `fuentes/teoria/` y, de forma explícita, los
documentos estudiantiles de la actividad creada. La actividad permanece en
`creados/` aunque se utilice como fuente de un banco o de la wiki. Las rúbricas,
soluciones y resultados no se incluyen en esa selección.

## Probarlo conversando

Copia `curso/` a una carpeta de trabajo fuera de la instalación del plugin.
Pide «Inicia mi proyecto docente» y después «¿Qué puedo hacer ahora?». Se
recomendará el mapa sin crearlo automáticamente. Este ejemplo deja `mapa-docente/` vacío;
el [ejemplo del mapa](../mapa-docente/README.md) permite probar su navegación.

Para diseñar una actividad nueva puedes pedir:

- «Diseñemos un comentario histórico a partir de los testimonios; quiero
  evaluar contraste de fuentes. Dispongo de 50 minutos».
- «Adapta la actividad experimental para trabajo individual. El alumnado puede
  consultar IA; quiero evidencias de comprensión y un informe con datos reales».

El agente debe preguntar solo por lo que falte, presentar tareas y evidencias
antes de generar documentos y entregar la rúbrica completa al docente. No debe
elegir un notebook para un comentario histórico ni inventar sanciones por IA.

Después de cada tarea ofrecerá un siguiente paso apoyándose en los resultados
que pueda comprobar:

- Inicio → mapa docente → consulta o visualización y elección de un flujo.
- Actividad → evaluación, cuando se aporten las entregas identificadas y la hoja
  Moodle. Los archivos de ejemplo ya permiten demostrar la corrección.
- Banco → modelos impresos → feedback, cuando existan los resultados detallados
  y el manifiesto de los modelos.

Si una fase ya está acreditada, no la propondrá como pendiente. Si solo hay
indicios o falta una entrada, lo explicará; ninguna sugerencia inicia otra tarea.
También puedes pedir apuntes e infografías o diapositivas visuales individuales.
El español claro se aplica por defecto, salvo indicación del profesor.

## Reproducir las utilidades

El profesor puede pedir al agente que ejecute este recorrido. Para desarrollo,
desde la raíz del plugin:

```sh
python examples/recorrido-docente/comprobar.py ../demo-curso-v2
```

El destino debe ser nuevo y estar fuera del plugin. La prueba copia los datos,
valida el catálogo, produce tres exámenes HTML con solucionarios separados y GIFT
ofuscados, exporta ambas hojas de actividad y cruza detalle de examen con un
libro separado para generar feedback. Añadir `--pdf` exige los PDF reales y
necesita las dependencias opcionales y Chromium. El enunciado de la actividad
también se convierte a HTML y, con esa opción, a PDF dentro de su carpeta
`alumnado/impresion/`; el PDF generado queda asociado en el registro reservado
de la actividad. Los modelos usan la distribución `--layout curso-v2`: los
archivos para el alumnado están separados del manifiesto, GIFT, soluciones y
bancos congelados, que permanecen en `docente/`.

La carpeta resultante incluye:

| Ruta | Resultado |
| --- | --- |
| `curso/fuentes/` | Materiales aportados conservados; el banco histórico continúa en su ubicación. |
| `curso/creados/actividades/medir-y-justificar/` | Actividad con archivos estudiantiles y docentes separados, y estado visible. |
| `curso/creados/cuestionarios/fuentes-mediciones-evidencias/` | Modelos HTML/PDF en `alumnado/`; GIFT, manifiesto, bancos congelados e informe de cobertura en `docente/`. El examen recién generado queda en estado borrador. |
| `curso/resultados/medir-y-justificar/ordinaria/recibidos/` | Entrega grupal, identificación y hojas Moodle originales. |
| `curso/resultados/medir-y-justificar/ordinaria/correccion/` | Evaluaciones y perfiles; `tarea/` y `libro/` contienen las copias para Moodle con su auditoría. |
| `curso/resultados/fuentes-mediciones-evidencias/ordinaria/recibidos/` | Detalle sintético por pregunta y libro de calificaciones originales. |
| `curso/resultados/fuentes-mediciones-evidencias/ordinaria/correccion/` | Perfil de cruce y carpeta `feedback/` con un CSV por modelo, conservando las notas. |
| `comprobacion.json` | Resumen del recorrido y conservación de originales. |

Todo `resultados/` queda fuera del mapa. Las carpetas no gestionan permisos.
Los materiales no se mueven al cambiar de estado; solo los bancos congelados
del examen son copias necesarias para conservar la evaluación reproducible.

La actividad evaluada obtiene **8,75/10**: registro 4/4 e interpretación 3/4,
cada criterio con peso del 50 %. La persona sin entrega conserva sus celdas
previas. En el examen se simulan dos fallos de crítica de fuentes y una evidencia
aislada en medición: el primero se considera dificultad acusada, el segundo
aspecto a revisar. Las notas del libro se conservan literalmente; la persona no
presentada recibe comentario vacío.

No se han subido estos archivos a Moodle. Antes de una importación real, revisar
el perfil, los identificadores y la vista previa según la [guía de Moodle](../../docs/MOODLE.md).
