# Preparación de GitHub

Destino elegido por el propietario:
[https://github.com/cjescudero/asistente-docente](https://github.com/cjescudero/asistente-docente).
Contenido propio bajo [MIT](../LICENSE); terceros en [NOTICE](../NOTICE.md).
No se publica nada al instalar, validar ni construir este proyecto.

## Fuente que se debe subir

La raíz del repositorio debe ser la carpeta `asistente-docente`, con `README.md`,
`plugin.json`, `skills/`, `scripts/`, `.github/`, `.agents/`, `.claude-plugin/` y
`.codex-plugin/` directamente dentro. No subir el workspace de plugins completo.
El ZIP `*-source.zip` preparado por el proyecto reúne esa fuente con una única
carpeta envolvente. Incluye archivos ocultos necesarios para los catálogos y CI.

En un clon local del repositorio de destino, copiar esa fuente, revisar los
cambios y crear el commit. Si el remoto ya tiene contenido, integrarlo sin
sobrescribirlo ni forzar la historia. La creación del repositorio, el push y su
visibilidad son acciones posteriores que debe autorizar el propietario.

## Validación y paquetes

Preparar dependencias con `python scripts/setup_environment.py --dev`. Usando
el Python de ese entorno:

```sh
python scripts/sync_manifests.py --check
python scripts/validate_plugin.py --public
python -m unittest discover -s tests -v
python scripts/build_release.py --source
```

La comprobación pública exige licencia y URL, pero no certifica que el remoto
exista, sea público o se pueda instalar desde una cuenta concreta.
La carpeta `release/` incluye dos ZIP de plugin, uno de fuente y sus huellas;
los paquetes de plugin no llevan catálogos. Se excluyen entornos, cachés, archivos
`.env`, claves privadas habituales y ZIP anteriores. Esa exclusión no sustituye
revisar los archivos antes de un commit. No incluir materiales o datos de cursos.

La automatización de GitHub comprueba Linux, Windows y macOS y construye los
paquetes como artefactos; no publica releases. Para una release, etiquetar la
versión que coincide con `plugin.json`, adjuntar los tres ZIP y los ficheros
`SHA256SUMS` y `SOURCE-SHA256SUMS`, y usar el historial como notas. Publicar cuando
se hayan revisado los artefactos y las pruebas del anfitrión de destino.

## Mantenimiento y verificación real

`plugin.json` es la fuente única de identidad, versión, licencia y presentación.
Tras editarlo, ejecutar `python scripts/sync_manifests.py`, revisar los cuatro
archivos generados y guardarlos junto a la fuente. Los catálogos usan rutas
relativas, por lo que también sirven desde un clon o fork.

Comprobar los pasos de [instalación](INSTALACION.md) desde una copia limpia del
repositorio ya público y una cuenta de cada anfitrión. Registrar esos resultados
por separado de las pruebas locales. Si cambia el formato de un anfitrión,
actualizar su adaptador y la documentación, manteniendo las skills compartidas.

Configurar en GitHub la descripción, los temas docentes y los canales de issues.
Activar los avisos privados de seguridad si se ofrece ese canal. No se afirma
ninguna de estas configuraciones remotas hasta verificarla.
