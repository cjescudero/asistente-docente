# Instalación y primer uso

Repositorio de distribución:
[github.com/cjescudero/asistente-docente](https://github.com/cjescudero/asistente-docente).
Los ZIP de instalación y de fuente están en las
[versiones publicadas](https://github.com/cjescudero/asistente-docente/releases).

## Elegir qué instalar

| Uso | Requisito |
| --- | --- |
| Instrucciones y generación de materiales mediante el agente | Anfitrión que admita skills/plugins y acceso autorizado a archivos |
| Bancos GIFT, feedback CSV, validar mapa y generar grafo | Python 3.10 o posterior |
| Lector HTML de la wiki y conversión de Markdown | Dependencias básicas de `requirements.txt` |
| Generar PDF | Dependencias PDF y Chromium/Chrome compatible |
| Imágenes o lectura de PDF, diapositivas y otros originales | Capacidades del anfitrión; no se incluyen lectores universales ni generador de imágenes |

No hacen falta claves API, servidor MCP, Notion ni una conexión a Moodle.
Moodle solo interviene si se utilizan sus formatos de importación/exportación.
La cuenta y las políticas del anfitrión pueden limitar plugins y ejecución.

## Obtener la fuente

Clona el repositorio:

```sh
git clone https://github.com/cjescudero/asistente-docente.git
cd asistente-docente
```

También puedes descargar el código desde GitHub o el ZIP `*-source.zip` de una
release y extraerlo. Conserva toda la carpeta: las skills comparten scripts,
referencias y recursos. Copiar únicamente un `SKILL.md` rompe esas dependencias.
No clones ni extraigas el plugin dentro de la carpeta que contiene los datos de
alumnos para después subirlo todo junto.

## Claude Cowork y Claude Code

El repositorio contiene `.claude-plugin/marketplace.json` y el manifiesto Claude,
generados desde `plugin.json`. En Claude, abre **Customize → Plugins → Add → Add
marketplace → Add from a repository**, indica
`https://github.com/cjescudero/asistente-docente` y selecciona **Asistente docente**.
Los nombres de los menús y su disponibilidad dependen de la versión y la cuenta.
Consulta [la guía oficial de Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

En Claude Code:

```text
/plugin marketplace add cjescudero/asistente-docente
/plugin install asistente-docente@asistente-docente
```

Para probar una copia local, sustituye el repositorio del primer comando por la
ruta de la carpeta clonada. Inicia una sesión nueva y comprueba que aparecen doce
skills. Véase [instalación mediante marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).
El ZIP `*-claude.zip` contiene el plugin, sin el catálogo; úsalo solo en una
interfaz que ofrezca carga de archivos de plugin.

## ChatGPT Work y Codex

La fuente incluye `.agents/plugins/marketplace.json`, con una entrada local a la
raíz del repositorio. En el escritorio, abre un proyecto sobre la carpeta clonada,
reinicia la aplicación si es necesario y busca **Asistente docente** en las
fuentes del directorio de plugins. El catálogo no lo instala ni lo habilita solo.
En versiones de Codex CLI que admitan la gestión de marketplaces se puede
registrar el repositorio con:

```sh
codex plugin marketplace add https://github.com/cjescudero/asistente-docente.git
```

Instala después el plugin desde el catálogo visible del anfitrión. La fuente usa
Agent Plugins 1.0 y añade un adaptador `.codex-plugin/plugin.json` para clientes
compatibles con ese manifiesto. El ZIP `*-agent-plugins.zip` conserva ambos.
Estas vías siguen la [documentación de empaquetado de OpenAI](https://developers.openai.com/plugins/build/plugins).

En cuentas con un espacio de trabajo administrado, importar un repositorio como
marketplace puede requerir intervención del administrador. No se presupone que
cualquier cuenta web permita cargar un ZIP. Consulta los
[controles de plugins de la cuenta](https://help.openai.com/en/articles/20001256).
No es necesario publicar el plugin en el directorio universal para distribuir
su código en GitHub; tampoco se garantiza su instalación en todos los planes.

## Preparar las utilidades Python

Esto prepara herramientas locales; es independiente de instalar las skills en
el anfitrión. En macOS/Linux usa un Python 3.10 o posterior:

```sh
python3 scripts/setup_environment.py
.venv/bin/python scripts/docencia.py doctor
```

En Windows PowerShell:

```powershell
py -3 scripts/setup_environment.py
.venv\Scripts\python.exe scripts/docencia.py doctor
```

`doctor` distingue `basic_ready` y `pdf_ready`; usa `doctor --pdf` para exigir
las capacidades PDF. Un PDF concreto requiere comprobar su generación.

La opción básica no descarga un navegador. Para PDF, añade `--pdf` al mismo
comando. `--dev` instala las herramientas de validación y pruebas, y `--dry-run`
muestra las operaciones sin ejecutarlas. Si la instalación es de solo lectura,
usa `--venv` con una carpeta externa. El script no cambia configuraciones globales.
En Linux pueden hacer falta bibliotecas del sistema: consulta el
[instalador de Playwright](https://playwright.dev/python/docs/browsers#install-system-dependencies)
antes de usar su opción `--with-deps`.

También puede usarse el Python del anfitrión cuando ya tenga las dependencias.
`ASISTENTE_DOCENTE_CHROMIUM` permite seleccionar un navegador existente. Si faltan
capacidades, se conservan fuentes y HTML y se declara el PDF pendiente.

## Primer proyecto

Crea una carpeta independiente para el curso y facilita al agente solo el acceso
necesario. Puedes pedir:

> Prepara este proyecto para una asignatura de Historia de secundaria. La carpeta
> «materiales» contiene teoría y «actividades» contiene prácticas. Conserva mis
> instrucciones existentes y pregunta antes de resolver un conflicto.

Después, si quieres organizar las fuentes:

> Crea un Mapa docente de esas dos carpetas, separando los materiales del estudiante
> y los reservados. Usa el mapa como punto de partida para los próximos trabajos.

No es obligatorio usar el mapa para un encargo sencillo con fuentes aportadas.
El [catálogo](CATALOGO.md) ofrece ejemplos de las doce skills. Revisa siempre los
resultados docentes, los PDF y las importaciones Moodle antes de utilizarlos.

## Actualizar o retirar

Actualiza la fuente con Git o descarga la nueva versión y usa el mecanismo de
actualización/reinstalación del anfitrión. No edites su caché interna ni copies un
paquete sobre otro abierto. Los datos del curso se conservan fuera del plugin.
Desinstalarlo desde el anfitrión no elimina esos materiales. El entorno `.venv`
local se puede retirar cuando ya no se utilice, sin tocar las carpetas del curso.
