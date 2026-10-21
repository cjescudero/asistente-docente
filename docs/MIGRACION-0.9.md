# Migración a 0.9: procedencia, estado y continuidad

La versión 0.9.0 usa `curso-v2` para proyectos nuevos. Un curso declarado
`curso-v1` sigue funcionando con sus rutas anteriores. Actualizar el plugin o
repetir «Inicia mi proyecto docente» no mueve sus archivos ni lo convierte a v2.
Tampoco se crea un segundo árbol paralelo para aparentar una migración completa.

## Qué cambia

- `fuentes/` reúne originales aportados; `creados/` reúne materiales elaborados
  por tipo. La audiencia se separa dentro de actividades y exámenes.
- Un borrador se guarda desde el inicio en su destino por tipo, con estado visible
  en `LEEME.md` y `material-docente.json`; aprobarlo no cambia sus enlaces.
- El mapa está en `mapa-docente/`. Las descargas y la corrección están separadas
  bajo `resultados/<actividad>/<convocatoria>/{recibidos,correccion}/`.
- Las skills sugieren próximos pasos según resultados comprobados y usan español
  claro por defecto, respetando idioma y estilo del profesor.

## Preparar una propuesta revisable

Antes de reorganizar un curso existente, inventariar únicamente lo necesario
para proponer correspondencias y leer sus instrucciones. No deducir procedencia,
acceso o estado por la carpeta antigua, antigüedad, extensión o nombre «final».
`docente/evaluaciones/` puede mezclar exámenes históricos y recién creados;
`docente/borradores/` puede contener material ya utilizado.

La propuesta debe enumerar por archivo o conjunto indivisible:

1. Ruta actual, destino propuesto y razón de clasificación: aportado o creado,
   tipo, destinatario y versión. Dejar pendiente lo que no pueda determinarse.
2. Estado real del conjunto y comprobaciones que lo sustentan. No marcar como
   revisado un borrador solo porque vaya a usarse como fuente.
3. Colisiones, enlaces entrantes y salientes, registros y selecciones afectados.
4. Tratamiento de derivados, snapshots y exámenes ya utilizados, sin alterar
   calificaciones, numeración ni correspondencia papel–GIFT–manifiesto.
5. Cambios concretos de `proyecto-docente.json`, `AGENTS.md` y `LEEME.md`.

Por ejemplo, un examen histórico puede ir a
`fuentes/evaluaciones/examenes/2025-2026/`, mientras que un nuevo examen se
propone bajo `creados/examenes/parcial-01/`. El nombre de la carpeta original no
resuelve por sí solo esa diferencia. No ejecutar movimientos hasta que el
profesor apruebe la propuesta concreta; conservar reglas incompatibles y consultar
cómo conciliarlas. La autorización para actualizar el plugin no migra los cursos.

## Aplicar y comprobar

`plan-migration` previsualiza movimientos, colisiones y enlaces; no los aplica.
Su informe incluye `metadata_reviews` para señalar configuraciones, registros,
catálogos y manifiestos que requieren revisión semántica. Cada entrada identifica
el documento, su ruta prevista, tipo y motivo; no sustituye texto JSON a ciegas
ni demuestra que los metadatos ya se hayan actualizado.
La guía no presupone un migrador automático de curso-v1 a curso-v2. Tras la
aprobación, el agente aplica el plan y comprueba los resultados:

- Conservar contenidos originales; no sobrescribir colisiones ni crear copias de
  exportación por sistema. Mantener los respaldos acordados fuera del corpus.
- Actualizar enlaces Markdown relativos, fuentes registradas, catálogo de bancos,
  rutas de actividad y configuración del curso. Verificar los archivos reales.
- Conservar los identificadores y versiones. Mover el registro `actividad.json`
  obliga a recalcular todas sus rutas relativas.
- Para bancos en varias ramas, usar `path_base: "project"` y rutas relativas al
  curso; los catálogos antiguos sin ese campo conservan su base en el catálogo.
  No usar `..` ni copiar un banco histórico para que encaje en el catálogo.
- Conservar exámenes ya generados como unidades con sus snapshots, huellas y
  manifiesto originales. Pueden mantenerse en una distribución plana antigua
  dentro de su carpeta de examen. No repartir automáticamente sus archivos entre
  `alumnado/` y `docente/`; eso rompería referencias y podría alterar su integridad.
  Los exámenes nuevos usan `--layout curso-v2`.
- Regenerar lector y grafo solo dentro del mantenimiento autorizado, tras validar
  el índice y sus dependencias. No presentar una vista antigua como actual.
- Mantener `resultados/`, datos personales y borradores fuera de la wiki. Incorporar
  materiales creados requiere selección expresa y estado revisado o listo.
- Actualizar `structure` a `curso-v2` cuando la nueva organización y su selección
  sean coherentes. Ejecutar las comprobaciones de proyecto, mapa y catálogos que
  correspondan; distinguir lo revisado de lo pendiente.

El resultado de la migración debe incluir cambios realizados, elementos
conservados, conflictos pendientes y enlaces comprobados. Mantener el proyecto
utilizable aunque alguna parte requiera decisión docente; no afirmar que se ha
migrado completamente mientras queden correspondencias sin resolver.

## Continuar sin migrar

Un curso v1 puede usar las mejoras de orientación y español claro manteniendo
sus rutas. Las skills consultan su configuración y sus instrucciones antes de
elegir destinos. No trasladar nuevos materiales a rutas v2 de manera aislada sin
acuerdo sobre la organización del curso. Las versiones del registro del mapa,
manifiesto, actividad y catálogo son independientes del nombre `curso-v2`.

## Nombres agrupados desde 0.9.0

Estas equivalencias no crean alias en el anfitrión. Actualizar referencias en cursos solo durante una adaptación solicitada; conservar instrucciones y consultar conflictos. No modificar instalaciones anteriores.

| Identificador anterior | Identificador actual | Nombre visible |
| --- | --- | --- |
| `evaluar-entregas` | `actividades-evaluacion` | Actividades: evaluación |
| `preparar-actividades-docentes` | `actividades-preparacion` | Actividades: preparación |
| `generar-apuntes-estudio` | `apuntes-estudio-creacion` | Apuntes estudio: creación |
| `crear-bancos-preguntas` | `bancos-preguntas-creacion` | Bancos de preguntas: creación |
| `redactar-espanol-claro` | `espanol-conciso-redaccion` | Español conciso: redacción |
| `generar-feedback-evaluaciones` | `evaluaciones-observaciones-alumnado` | Evaluaciones: observaciones para el alumnado |
| `preparar-examenes-papel-moodle` | `evaluaciones-preparacion-modelos` | Evaluaciones: preparación modelos a partir de bancos de preguntas |
| `crear-infografias-didacticas` | `infografias-didacticas-creacion` | Infografías didácticas: creación |
| `consultar-mapa-docente` | `mapa-docente-consulta` | Mapa docente: consulta |
| `crear-mapa-docente` | `mapa-docente-creacion-visualizacion` | Mapa docente: creación y visualización |
| `orientar-docente` | `proyecto-docente-ayuda` | Proyecto docente: ayuda |
| `iniciar-proyecto-docente` | `proyecto-docente-inicializacion-adaptacion` | Proyecto docente: inicialización y adaptación |
| `visualizar-mapa-docente` | `mapa-docente-creacion-visualizacion` | Mapa docente: creación y visualización |

Las doce carpetas y nombres visibles comienzan por su categoría. El orden efectivo depende del anfitrión. La consulta conserva su comportamiento de solo lectura.
