# Contribuir a Asistente docente

Las propuestas pueden llegar como issues o pull requests al repositorio
[cjescudero/asistente-docente](https://github.com/cjescudero/asistente-docente).
Usa ejemplos sintéticos: no adjuntes nombres, entregas, notas ni exámenes reservados.
Describe la versión, el anfitrión, el sistema operativo, los pasos y el resultado
esperado. Para problemas sensibles, utiliza el aviso privado de seguridad de
GitHub si el repositorio lo tiene habilitado; no publiques datos ni credenciales.

## Preparar el entorno

Se necesita Python 3.10 o posterior. Desde la raíz:

```sh
python scripts/setup_environment.py --dev
```

En macOS/Linux ejecuta las comprobaciones con `.venv/bin/python`; en Windows,
con `.venv\Scripts\python.exe`. Si ya has activado ese entorno, los comandos son:

```sh
python scripts/sync_manifests.py --check
python scripts/validate_plugin.py --public
python -m unittest discover -s tests -v
python scripts/validate_library.py examples/mapa-docente/mapa-docente
python scripts/build_release.py --source
```

Para comprobar los PDF añade `--pdf` al instalador y establece `RUN_PDF_TESTS=1`.
Para cambios visuales ejecuta las pruebas de navegador documentadas en
[validación](docs/VALIDACION.md). Registra los límites de lo probado.

## Mantener una fuente común

Edita `plugin.json` y ejecuta `python scripts/sync_manifests.py`. Los manifiestos
Claude/Codex y catálogos son derivados versionados para que GitHub pueda servirlos
sin que el usuario construya nada. No modifiques solo un adaptador. Los ZIP de
release no contienen catálogos; el archivo de fuentes sí incluye catálogos y CI.

Mantén las skills independientes de materia, nivel, institución y escala.
Un caso particular debe ser un ejemplo identificado o una opción del encargo.
Conserva el español natural de las instrucciones y respeta el idioma solicitado
para los resultados. Las fuentes, rúbricas y datos del docente viven fuera del
plugin. No conviertas los ejemplos en valores predeterminados.

Mantén doce skills con nombres sin prefijo. Conserva coherencia entre la inicialización,
las utilidades y el [contrato común](docs/PROYECTO-DOCENTE.md), sin introducir una
segunda configuración de fuentes en la ficha pedagógica. El modo de
previsualización no debe mutar el curso; las migraciones solo aplican propuestas
concretas aprobadas. Comprueba fuentes excluidas y dependencias retiradas, no solo
el caso de una carpeta vacía.

Añade pruebas cuando cambie un comportamiento observable. Una nueva skill debe
indicar cuándo usarla, qué necesita y qué entrega, con recursos relativos al
paquete. Documenta capacidades ausentes y conserva originales y contenido ajeno.

## Licencias

El contenido propio usa [MIT](LICENSE). Al contribuir, debes poder distribuir
tus aportaciones bajo esa licencia. Los componentes externos conservan sus
licencias y avisos; registra cualquier nueva dependencia en [NOTICE](NOTICE.md).
