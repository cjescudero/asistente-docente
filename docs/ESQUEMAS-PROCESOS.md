# Guía visual de los procesos docentes

Estos esquemas muestran qué aportar, qué hace el agente y qué revisa el profesor.
Las flechas indican el recorrido posible: no autorizan a ejecutar el siguiente
paso sin encargo. Moodle se utiliza mediante archivos e importación manual.

La organización sigue los procesos explicados en la charla **XIGAID — «E agora
que a IA pode facelo, que facemos nós?»**, especialmente las fichas sobre mapa,
actividades, bancos, modelos y devolución de comentarios. Los diagramas se han
redactado para el funcionamiento actual del plugin; no requieren los archivos
privados de la charla ni presentan sus demostraciones pendientes como verificadas.

## Elige tu recorrido

```mermaid
flowchart TD
    A[Inicializar o adaptar el proyecto] --> B[Elegir fuentes y exclusiones]
    B --> C[Crear y revisar el mapa docente]
    C --> D[Consultar explicaciones, fuentes y grafo]
    D --> E[Preparar actividad]
    E --> F[Recibir y evaluar entregas]
    D --> G[Crear banco de preguntas]
    G --> H[Crear modelos impresos y GIFT]
    H --> I[Preparar Moodle y realizar el cuestionario]
    I --> J[Devolver observaciones sobre las calificaciones]
    D --> K[Crear apuntes o apoyos visuales]
```

El mapa facilita reutilizar conocimiento, pero una tarea con adjuntos suficientes
puede hacerse sin él. En cualquier punto: **«¿Qué puedo hacer ahora?»** activa la
ayuda contextual. Se usa español conciso por defecto, salvo otra indicación.

## 1. Inicializar o adaptar el proyecto

**Petición:** «Prepara esta carpeta para mi asignatura y revisa cómo organizar lo que contiene».

```mermaid
flowchart TD
    A[Profesor indica carpeta y propósito] --> B[Agente lee instrucciones e inventaría materiales]
    B --> C{¿Hace falta reorganizar?}
    C -->|Sí| D[Proponer origen, destino, motivo y dudas]
    D --> E{Profesor decide}
    E -->|Acepta todo o parte| F[Comprobar colisiones y mover solo lo aprobado]
    E -->|Conserva organización| G[Respetar ubicación de los materiales]
    C -->|No| G
    F --> H[Acordar fuentes y exclusiones]
    G --> H
    H --> I[Preparar configuración, AGENTS y LEEME]
    I --> J[Orientar y recomendar crear el mapa]
```

**Resultado:** originales en `fuentes/`, productos en `materiales_generados/`,
datos técnicos en `_datos_internos_proyecto/` y resultados en `resultados/`,
según la organización acordada. La inicialización no crea el mapa automáticamente.
[Skill de inicialización y adaptación](../skills/proyecto-docente-inicializacion-adaptacion/SKILL.md) ·
[Organización del proyecto](PROYECTO-DOCENTE.md).

## 2. Crear y consultar el mapa docente

**Petición:** «Crea el mapa con estas fuentes; explica los conceptos y enlaza sus referencias».

```mermaid
flowchart TD
    A[Fuentes elegidas y exclusiones] --> B[Inventariar y leer el contenido accesible]
    B --> C[Redactar explicaciones, relaciones y referencias]
    C --> D{¿Afirmaciones trazables?}
    D -->|No| E[Registrar dudas y revisar las fuentes]
    E --> C
    D -->|Sí| F[Profesor revisa una muestra]
    F --> G[Wiki Markdown, lector HTML y grafo]
    G --> H[Consultar desde el índice y seguir enlaces]
    H --> I[Volver al original para ampliar o verificar]
    J[Cambian las fuentes] --> K[Revisar las páginas dependientes]
    K --> C
```

**Resultado:** `mapa-docente/` contiene una síntesis explicativa, no solo un índice.
Las entregas y notas quedan fuera del corpus; las vistas estudiantiles excluyen
contenido reservado. Regenerar las vistas no exige reescribir la wiki.
[Crear y visualizar](../skills/mapa-docente-creacion-visualizacion/SKILL.md) ·
[Consultar](../skills/mapa-docente-consulta/SKILL.md).

## 3. Diseñar una actividad mediante diálogo

**Petición:** «Diseñemos una actividad sobre estos materiales; acuerda conmigo evidencias y entregables».

```mermaid
flowchart TD
    A[Materiales, objetivos, nivel y ejemplos anteriores] --> B[Profesor y agente acuerdan duración, recursos y uso de IA]
    B --> C[Proponer tareas, hitos y evidencias]
    C --> D[Definir criterios y rúbrica]
    D --> E{¿Objetivos, tareas y criterios están alineados?}
    E -->|No| C
    E -->|Sí, revisión docente| F[Preparar archivos de la actividad]
    F --> G[Alumnado: enunciado, plantillas y criterios generales]
    F --> H[Docente: rúbrica completa y guía de corrección]
    F --> I[Ofrecer preparar la recepción de entregas]
```

**Resultado:** conjunto en `materiales_generados/actividades/<actividad>/`.
Se diseña teniendo en cuenta el acceso a IA, sin exigir su uso por defecto:
justificaciones, contrastes y decisiones permiten observar comprensión.
[Preparar actividades](../skills/actividades-preparacion/SKILL.md) · [Guía](ACTIVIDADES.md).

## 4. Recibir y evaluar entregas

**Petición:** «Evalúa estas entregas con el enunciado y la rúbrica y prepara la hoja Moodle con notas y comentarios».

```mermaid
flowchart TD
    A[Profesor descarga entregas y hoja CSV de Moodle] --> B[Guardar originales en recibidos]
    C[Enunciado, rúbrica y solución disponible] --> D[Identificar trabajos y valorar evidencias por criterio]
    B --> D
    D --> E{¿Identificación y datos obligatorios válidos?}
    E -->|No| F[Registrar incidencias y resolverlas sin asignar ceros automáticos]
    F --> D
    E -->|Sí| G[Propuesta de nota y feedback individual]
    G --> H{Revisión del profesor}
    H -->|Corregir| D
    H -->|Aprobar| I[Copia del CSV con notas y comentarios; auditoría]
    I --> J[Profesor importa y comprueba en Moodle]
```

**Dónde poner los archivos:**

```text
resultados/<actividad>/<convocatoria>/
├── LEEME.md
├── recibidos/
│   ├── entregas/
│   └── hoja-original-moodle.csv
└── correccion/
    └── Informes, incidencias y copia del CSV para importar
```

La hoja puede abrirse en Excel, pero el intercambio de la utilidad es CSV.
No asociar personas por semejanza de nombres. La valoración cualitativa puede
avanzar mientras se resuelven incidencias; la exportación ambigua se bloquea.
[Evaluar actividades](../skills/actividades-evaluacion/SKILL.md) · [Calificaciones](CALIFICACIONES.md).

## 5. Crear bancos asociados a materiales

**Petición:** «Propón un banco para estos temas, con cobertura y variantes justificadas».

```mermaid
flowchart TD
    A[Fuentes y objetivos; ejemplos históricos si existen] --> B[Acordar cobertura, dificultad y cantidad de principales]
    B --> C[Redactar preguntas, variantes, claves y explicaciones]
    C --> D[Vincular cada pregunta con materiales y conceptos]
    D --> E{¿Formato válido y contenido revisado?}
    E -->|No| C
    E -->|Sí| F[GIFT, metadatos y registro en el catálogo]
    F --> G[Disponibles para combinar en cuestionarios]
```

**Resultado:** `materiales_generados/bancos/<banco>/`, con archivos individuales,
sin ZIP por defecto. `01-A`, `01-B`… son variantes de una principal. Se parte de
cuatro modelos y se proponen hasta cuatro variantes pertinentes por principal;
el profesor ajusta la cantidad. Validar sintaxis no demuestra calidad pedagógica.
[Crear bancos](../skills/cuestionarios-bancos-preguntas-creacion/SKILL.md) · [Catálogo](BANCOS.md).

## 6. Componer los modelos para imprimir y evaluar

**Petición:** «Prepara modelos que cubran estos temas; propón cantidad de preguntas y duración».

```mermaid
flowchart TD
    A[Bancos revisados y objetivos del cuestionario] --> B[Acordar cuotas, preguntas, modelos, duración y puntuación]
    B --> C{¿Hay preguntas suficientes?}
    C -->|No| D[Profesor ajusta cuotas o encarga ampliar bancos]
    D --> B
    C -->|Sí| E[Seleccionar reproduciblemente y variar entre modelos]
    E --> F[Congelar bancos y correspondencias en el manifiesto]
    F --> G[PDF del alumnado]
    F --> H[Solucionarios docentes]
    F --> I[GIFT ofuscados con categorías por modelo]
    G --> J[Revisar orden, opciones, pesos y legibilidad]
    H --> J
    I --> J
```

**Resultado:** `materiales_generados/cuestionarios/<cuestionario>/`, con
`alumnado/`, `docente/` y `_datos_internos/`. Ningún modelo repite una principal;
se busca diversidad sin prometer un óptimo. Emparejamiento queda fuera del
circuito impreso. El GIFT contiene claves y permanece reservado al docente.
[Crear modelos](../skills/cuestionarios-modelos-imprimir-evaluar/SKILL.md) ·
[Puntuaciones y límites](PUNTUACION-CUESTIONARIOS.md).

## 7. Preparar Moodle: trabajo del profesor

```mermaid
flowchart TD
    A[GIFT ofuscados y manifiesto] --> B[Importar preguntas por categorías de modelo]
    B --> C[Crear un cuestionario Moodle para cada modelo]
    C --> D[Añadir preguntas y fijar el orden del papel]
    D --> E[Desactivar mezclas de preguntas y respuestas]
    E --> F[Comprobar puntuación y opciones de revisión]
    F --> G{¿Vista de estudiante coherente con el papel?}
    G -->|No| D
    G -->|Sí| H[Profesor habilita el cuestionario]
```

Categoría de ejemplo:
`RespuestasCuestionariosOffline/Talleres 5-8/Modelo 01`.
Importar GIFT no crea la actividad cuestionario ni garantiza su orden.
Los pesos negativos se conservan, pero hay que comprobar el comportamiento
real de la puntuación. [Preparación de Moodle](MOODLE.md).

## 8. Del papel a la nota: recorrido del alumnado

```mermaid
flowchart TD
    A[Recibir el modelo en papel] --> B[Resolver durante el tiempo acordado]
    B --> C[Abrir en Moodle el cuestionario del mismo modelo]
    C --> D[Transcribir opciones o valores por número de pregunta]
    D --> E[Comprobar modelo, numeración y respuestas]
    E --> F[Enviar respuestas]
    F --> G[Moodle aplica las claves y reglas configuradas]
```

Moodle muestra «Pregunta 01» y «Respuesta A», etc., sin el enunciado original.
La ofuscación reduce lo expuesto en pantalla; no elimina la consulta por otros
canales. El profesor debe prever tiempo de transcripción y accesibilidad.

## 9. De las calificaciones a las observaciones útiles

**Petición:** «Añade observaciones de mejora con este detalle de respuestas, el manifiesto y la hoja de calificaciones; conserva las notas».

```mermaid
flowchart TD
    A[Detalle por pregunta y calificaciones exportados de Moodle] --> C[Cruzar persona, modelo, número y respuesta]
    B[Manifiesto, banco congelado y metadatos] --> C
    C --> D{¿Datos obligatorios completos y sin ambigüedades?}
    D -->|No| E[Registrar incidencias; bloquear exportación hasta resolver]
    E --> C
    D -->|Sí| F[Priorizar hasta tres dificultades y recomendar repaso]
    F --> G[Profesor revisa comentarios y referencias]
    G --> H[CSV por modelo con notas e identificadores conservados]
    H --> I[Profesor importa comentarios y comprueba las calificaciones]
```

Una nota global no permite inferir dificultades conceptuales. No se reconstruye
la pregunta desde un banco modificado ni se deduce con certeza el razonamiento
del estudiante por una opción. Las recomendaciones enlazan material accesible al
alumnado y los no presentados quedan sin comentario.
[Observaciones sobre calificaciones](../skills/cuestionarios-observaciones-calificaciones-alumnado/SKILL.md).

## 10. Apuntes y apoyos visuales

```mermaid
flowchart TD
    A[Fuentes, objetivo y audiencia] --> B{¿Qué material hace falta?}
    B -->|Explicación para estudiar| C[Preparar apuntes con ejemplos y referencias]
    B -->|Síntesis visual| D[Definir una idea, relaciones y diseño]
    D --> E{¿Generación de imágenes disponible?}
    E -->|Sí| F[Crear infografía o diapositiva visual individual]
    E -->|No| G[Entregar diseño y prompt; imagen pendiente]
    C --> H[Revisión docente y entrega solicitada]
    F --> H
    G --> H
```

[Apuntes](../skills/apuntes-estudio-creacion/SKILL.md) e
[infografías](../skills/infografias-didacticas-creacion/SKILL.md) complementan los
recorridos anteriores. No se promete una presentación editable. Los borradores
no se incorporan automáticamente al corpus del mapa.

Para continuar: [ayuda y siguientes pasos](FLUJOS-DOCENTES.md),
[catálogo de skills](CATALOGO.md) y [ejemplo completo](../examples/recorrido-docente/README.md).
