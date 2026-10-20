# Migración a Asistente docente 0.7.0

La versión 0.7.0 simplifica los nombres y añade una puesta en marcha guiada.
La versión publicada 0.6.0 se conserva. Actualizar el plugin no reorganiza los
cursos ni cambia sus instrucciones automáticamente.

## Nombres de las doce skills

| Nombre anterior | Nombre desde 0.7.0 |
| --- | --- |
| `skill-consultar-mapa-docente` | `consultar-mapa-docente` |
| `skill-crear-bancos-preguntas` | `crear-bancos-preguntas` |
| `skill-crear-infografias-didacticas` | `crear-infografias-didacticas` |
| `skill-crear-mapa-docente` | `crear-mapa-docente` |
| `skill-evaluar-entregas` | `evaluar-entregas` |
| `skill-generar-apuntes-estudio` | `generar-apuntes-estudio` |
| `skill-generar-feedback-evaluaciones` | `generar-feedback-evaluaciones` |
| `skill-iniciar-proyecto-docente` | `iniciar-proyecto-docente` |
| `skill-preparar-actividades-docentes` | `preparar-actividades-docentes` |
| `skill-preparar-examenes-papel-moodle` | `preparar-examenes-papel-moodle` |
| `skill-redactar-espanol-claro` | `redactar-espanol-claro` |
| `skill-visualizar-mapa-docente` | `visualizar-mapa-docente` |

Son equivalencias documentadas, no alias instalados. Los anfitriones pueden
necesitar una actualización del plugin y una sesión nueva para mostrar los
nombres actuales. No mantener copias de ambas versiones de las skills dentro
del mismo paquete. Consultar la [instalación](INSTALACION.md).

Cuando el profesor solicite actualizar un proyecto anterior, revisar las
referencias a estos nombres en sus instrucciones y ejemplos. Cambiar solo las
referencias operativas afectadas; conservar citas, historial y contenido ajeno.
No editar las cachés del anfitrión ni instrucciones globales. Si una regla del
proyecto exige un nombre o flujo anterior, explicar la diferencia y preguntar
antes de sustituirla.

## Incorporar la organización del curso

1. Leer `AGENTS.md`, localizar materiales y mapa existente y preguntar solo por
   las ubicaciones y tipos desconocidos. Mostrar la estructura de
   [Proyecto docente](PROYECTO-DOCENTE.md), sin mover originales.
2. Preparar una tabla con origen, destino propuesto, motivo, colisiones y enlaces
   afectados. Por ejemplo, una carpeta de teoría puede corresponder a
   un destino nuevo `docente/fuentes/teoria/`. Para la wiki, proponer la ubicación
   definitiva antes de inicializar o movimientos individuales a la carpeta ya
   creada `docente/mapa-docente/`. Los nombres
   de los archivos no bastan para clasificar acceso, vigencia o soluciones.
3. Solicitar aprobación de esa propuesta concreta. Mientras no llegue, conservar
   archivos y configuración previos; avanzar únicamente con partes independientes.
4. Aplicar los movimientos aprobados sin sobrescribir destinos ni duplicar
   materiales como exportaciones. Revisar rutas relativas de los Markdown,
   `fuentes.json`, configuración e instrucciones. Resolver cambios con contenido
   previo preservado y comprobar que cada original sigue accesible.
5. Comprobar enlaces, colisiones y correspondencia de fuentes; registrar el mapa
   solo si existe un índice real. Actualizar el lector y el grafo únicamente
   dentro de un encargo que incluya su mantenimiento y tras validar el mapa.

El ayudante `plan-migration` recibe un archivo JSON de movimientos y emite un
informe de previsualización. No ejecuta movimientos ni modifica enlaces. La
aplicación corresponde al agente tras aprobar la propuesta. Los enlaces internos
de PDF, diapositivas y otros formatos binarios requieren revisión específica;
no se promete una reescritura universal.

Ejemplo de `movimientos.json`:

```json
[
  {"from": "teoria-antigua", "to": "docente/fuentes/teoria"},
  {"from": "examen-2025.pdf", "to": "docente/evaluaciones/examen-2025.pdf"}
]
```

El ayudante rechaza destinos existentes, incluso carpetas vacías, para evitar
fusiones implícitas. Elegir destinos nuevos o proponer movimientos individuales
de archivos sin colisiones. Cada informe contiene huellas y enlaces afectados;
comprobarlos de nuevo antes de aplicar la propuesta aprobada.

Seleccionar explícitamente las carpetas del corpus y sus exclusiones. Los
resultados, borradores y el propio mapa quedan fuera. `archivo/` no se incluye
por defecto. Si se retira una fuente ya usada, revisar las páginas que dependen
de ella antes de volver a consultarlas o generar derivados.

## Conservar el mapa y las instrucciones

`fuentes.json` mantiene su versión 2 y el formato de mapas anteriores. La nueva
configuración `proyecto-docente.json` no reemplaza ese inventario. Los mapas de
versión 1 conservan la vía de migración descrita en [Mapa docente](MAPA-DOCENTE.md).

Respetar el `AGENTS.md` existente y su bloque de consulta. Incorporar estructura,
selección y nombres dentro del alcance solicitado, sin reformatear lo ajeno.
Preguntar ante conflictos. Inicializar de nuevo no crea ni propone una wiki y
no reemplaza un mapa real por un estado pendiente.

Tras actualizar, comprobar los nombres visibles en el anfitrión y realizar una
petición pequeña con fuentes sintéticas. La validación local de paquetes no
sustituye esa comprobación. Registrar por separado las pruebas locales, la
instalación real y cualquier publicación de una nueva release.
