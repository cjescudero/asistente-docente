# Proyecto docente: puesta en marcha y contrato común

Instala el plugin, abre la carpeta del curso y pide **«Inicia mi proyecto docente»**.
El agente prepara el proyecto y explica lo que falta. El profesor no necesita
escribir comandos ni completar una ficha pedagógica para una petición sencilla.

## Estructura del curso

```text
curso/
├── AGENTS.md
├── proyecto-docente.json
├── LEEME.md
├── alumnado/
│   ├── materiales/
│   ├── actividades/
│   └── conocimientos/
├── docente/
│   ├── fuentes/
│   ├── evaluaciones/
│   ├── soluciones/
│   ├── rubricas/
│   ├── borradores/
│   ├── mapa-docente/
│   └── resultados/
│       └── entregas/
└── archivo/
```

`alumnado/` reúne los materiales destinados a estudiantes. `conocimientos/`
contiene dudas frecuentes, aclaraciones y otras ayudas; no es una copia de la
wiki. Las soluciones, rúbricas y evaluaciones reservadas tienen su lugar en
`docente/`. Los borradores nuevos se preparan en `docente/borradores/`; pasarlos
a `alumnado/` requiere un encargo que incluya esa entrega. Mantener una ubicación
para cada material, con sus derivados necesarios, sin copias de exportación por
sistema. Un archivo Markdown y su PDF son formatos del mismo material.

`docente/resultados/` contiene entregas, calificaciones y feedback. No alimenta
la wiki. Cada lote se guarda en `entregas/<actividad>/<convocatoria>/` con
`originales/`, `identificacion/` y `correccion/` cuando se recibe. Se conservan
las descargas y sus identificadores; no se reorganizan lotes previos sin acuerdo.
`archivo/` guarda materiales apartados del trabajo habitual y solo
alimenta el mapa si el profesor selecciona explícitamente esa carpeta o una de
sus subcarpetas. Los nombres de las carpetas organizan contenidos: no conceden
ni restringen acceso.

La inicialización deja `docente/mapa-docente/` vacía. No crea el índice, el lector,
el grafo. Recomienda el mapa y ofrece orientación, sin invocar su creación. Cuando el profesor encargue
crear el mapa, esa skill incorporará el índice real a `AGENTS.md`.

## Configuración operativa

`proyecto-docente.json` utiliza UTF-8 y rutas relativas dentro de la raíz del
curso, sin segmentos `..`. Las fuentes externas requieren elegir una raíz de
curso que las contenga o acordar su integración mediante una propuesta de
movimientos; no se trasladan originales automáticamente.
La versión del formato es independiente de la versión del plugin. Ejemplo:

```json
{
  "schema_version": 1,
  "structure": "curso-v1",
  "sources": {
    "selected": true,
    "include": ["docente/fuentes", "alumnado/materiales"],
    "exclude": ["docente/fuentes/examen-pendiente.pdf"]
  },
  "map": null
}
```

- `sources.include` contiene carpetas elegidas expresamente. Se incluyen sus
  archivos descendientes, salvo las exclusiones. No seleccionar toda la raíz del
  curso ni `docente/` completo: elegir las carpetas concretas.
- `sources.exclude` contiene rutas exactas de archivos o carpetas; no admite
  patrones glob. Excluir una carpeta excluye sus descendientes. Resolver también
  enlaces y rutas secundarias contra estas restricciones antes de abrir fuentes.
- `docente/resultados/`, `docente/borradores/` y `docente/mapa-docente/` quedan
  siempre fuera del corpus. No reintroducir su contenido mediante otra raíz o un
  enlace. Una tarea de evaluación puede leer sus entradas expresamente aportadas
  sin convertirlas en fuentes de la wiki.
- `sources.selected: false`, con `include` y `exclude` vacíos, indica selección
  aplazada. `selected: true` con listas vacías registra la decisión explícita de
  trabajar sin fuentes por ahora. Ninguno de esos estados selecciona todas las
  carpetas. Completar las partes independientes y preguntar por las fuentes
  cuando sean necesarias.
- `map` es `null` hasta que exista un mapa con `index.md` real. Después contiene
  la ruta relativa de su carpeta. La mera existencia de la carpeta vacía no
  permite registrarla como mapa creado.

La selección autoriza a usar un corpus en encargos que lo necesiten; no declara
sus documentos leídos ni autoriza su publicación. `fuentes.json` conserva su
formato: registra lo inventariado, los estados de lectura y las páginas del
mapa. No sustituye la selección operativa ni convierte fuentes antiguas en
fuentes todavía admitidas. La ficha de asignatura es opcional y contiene nivel,
objetivos, idioma y criterios pedagógicos, sin duplicar esta configuración.

Si una ruta no puede representarse de forma relativa, como entre unidades de
Windows, explicar la limitación y acordar una ubicación accesible. No mover ni
copiar originales para resolverla por iniciativa propia.

## Recorrido del agente

1. Identificar la raíz del curso y leer las instrucciones existentes. Preguntar
   solo por contexto, ubicaciones, tipos de materiales y selección que falten.
2. Crear la estructura en un proyecto nuevo. Para reorganizar uno existente,
   presentar correspondencias y movimientos concretos antes de aplicar cambios.
3. Guardar la selección o su estado pendiente, preparar `LEEME.md` y conciliar
   `AGENTS.md` dentro del alcance autorizado. Conservar texto ajeno al encargo;
   preguntar ante reglas incompatibles. Repetir sin duplicar ni sobrescribir.
4. Incorporar `redactar-espanol-claro` para textos en español. Conservar cualquier
   bloque de mapa existente y sus rutas; no añadir una entrada ficticia.
5. Comprobar capacidades y comunicar lo disponible y lo pendiente, sin lanzar
   otro flujo docente al cerrar la inicialización. Ofrecer `orientar-docente`,
   recomendar el mapa y esperar a que el profesor formule ese encargo.

Los ayudantes de archivos proponen texto cuando `AGENTS.md` ya existe; el agente
integra solo lo autorizado. No aceptar un bloque generado como sustitución de las
instrucciones del profesor. Verificar la carga de `AGENTS.md` en el anfitrión; si
no se incorpora automáticamente, pedir su lectura explícita o utilizar las
instrucciones de carpeta disponibles. No crear `CLAUDE.md` por sistema ni cambiar
la configuración global del anfitrión.

## Comprobaciones antes de cada encargo

Todas las skills aplican este contrato en la medida necesaria para la tarea.
No exigir un proyecto inicializado, una wiki o carpetas llenas para corregir un
texto o producir una actividad con adjuntos suficientes. Comprobar solo las
entradas necesarias y detener únicamente el trabajo que dependa de las ausentes.

Distinguir carpeta inexistente, carpeta vacía, carpeta con archivos pero ninguno
seleccionado y archivos no accesibles. Un problema de acceso o de lectura no
prueba ausencia de contenido y nunca es un fallo del estudiante. No buscar en
carpetas vecinas para completar entradas ni inventar el contenido que falta.

Cuando exista un mapa, empezar por su índice y seguir recursivamente solo los
enlaces pertinentes. Detenerse al reunir evidencia suficiente; evitar ciclos y
relecturas. Verificar originales para citas, calificaciones, preguntas evaluables,
contradicciones o elementos visuales relevantes. Los adjuntos aportados para un
encargo pueden usarse con sus límites, sin incorporarlos automáticamente al mapa.

Antes de crear, actualizar, consultar o visualizar el mapa, contrastar su registro
con la selección vigente. No seguir un enlace a una fuente excluida. Si una
fuente retirada ya sustentaba páginas, identificar sus dependencias directas e
indirectas y señalarlas como pendientes de revisión. Durante una consulta, emitir
la incidencia sin editar archivos; durante el mantenimiento autorizado, revisarlas
antes de volver a utilizarlas. No generar un lector o grafo actualizado si la
validación detecta dependencias fuera del corpus. No presentar HTML antiguos como
si reflejaran la selección nueva.

## Utilidades y capacidades

Los comandos siguientes son para el agente o para mantenimiento. Resolver la
instalación del plugin y las rutas del curso; el profesor puede pedir todas estas
operaciones en lenguaje natural:

```sh
python scripts/docencia.py init-project RUTA_CURSO --include docente/fuentes --exclude docente/fuentes/borrador.pdf --dry-run
python scripts/docencia.py init-project RUTA_CURSO --include docente/fuentes
python scripts/docencia.py init-project RUTA_CURSO
python scripts/docencia.py init-project RUTA_CURSO --no-sources
python scripts/docencia.py check-project RUTA_CURSO
python scripts/docencia.py doctor --project RUTA_CURSO
python scripts/docencia.py plan-migration RUTA_CURSO --moves movimientos.json
python scripts/docencia.py register-map RUTA_CURSO RUTA_MAPA --dry-run
```

`--include` y `--exclude` se pueden repetir. Sin opciones de selección, un
proyecto nuevo queda pendiente y uno existente conserva su selección.
`--no-sources` registra explícitamente una selección vacía (`selected: true`);
usarlo solo cuando esa sea la decisión del profesor. La previsualización no
modifica archivos. `plan-migration` produce un informe, no aplica movimientos.
`register-map` registra únicamente un índice ya creado; no genera la wiki ni
reescribe las instrucciones del profesor. Consultar la ayuda de cada comando
para los argumentos admitidos.

Los informes distinguen lo realizado de lo pendiente. `init-project` puede
crear carpetas y configuración y devolver `pending_approval` (código 2) porque
conserva un `AGENTS.md` o `LEEME.md` existente y propone su actualización.
Revisar `created`, `updated` y `proposals`; no repetir cambios por interpretar
ese estado como un fallo total. `check-project` devuelve código 2 para un
proyecto incompleto, incluidas fuentes pendientes, vacías o no seleccionadas;
código 1 indica configuración inválida y código 0 indica comprobación correcta.
`doctor` conserva además su diagnóstico de capacidades. Las tareas con entradas
suficientes pueden continuar aunque otra capacidad o carpeta esté pendiente.

La preparación de carpetas, configuración e instrucciones puede hacerse con las
herramientas de archivos del agente, sin Python. Mantener el mismo contrato y
comprobar manualmente los resultados. Python 3.10 o posterior es necesario para
las utilidades; el lector requiere las dependencias básicas. PDF sigue siendo
opcional. Reutilizar el entorno del anfitrión cuando sirva; si hay que preparar
otro, usar la caché de usuario fuera del curso y del plugin. El modo `--dev`
conserva un entorno `.venv` local para desarrollar el plugin; no es la preparación
normal de un curso.
Conservar Markdown y HTML cuando falte una capacidad; declarar PDF, grafo o
revisión pendientes según corresponda, sin afirmar que existen.

El proyecto puede estar en una carpeta local sincronizada con OneDrive o
SharePoint si los archivos están disponibles localmente. El plugin no configura
sincronización, conectores ni permisos remotos. Copilot Studio queda fuera de
esta versión.

Para adaptar un curso previo, seguir [Migración a 0.7](MIGRACION-0.7.md).
