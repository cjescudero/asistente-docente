# Instalación de Asistente docente

Asistente docente se incorpora desde su
[repositorio GitHub](https://github.com/cjescudero/asistente-docente) mediante
marketplaces personalizados. **No se publicará en el directorio público de
ChatGPT ni en el de Claude.** El repositorio es público; «personalizado» describe
el origen del catálogo, no una restricción de acceso al código.

Primero se añade el marketplace a la aplicación o al espacio de trabajo y,
después, se instala el plugin. Tener una cuenta en ChatGPT o Claude no realiza
ninguno de esos pasos automáticamente.

- [Instalación para profesores](#instalación-para-profesores): sin terminal.
- [Instalación para administradores](#instalación-para-administradores): permisos y actualizaciones.
- [Instalación avanzada](#instalación-avanzada): Codex CLI, Claude Code y Python.

Esta documentación corresponde a la versión 0.7.0 de la rama `main`. La release
0.6.0 se conserva como entrega anterior con ZIP. Si ya incorporaste el marketplace,
sincroniza su contenido y verifica la versión mostrada por la aplicación antes
de probar el recorrido de 0.7.0. Una referencia fijada a una revisión anterior
seguirá usando esa revisión hasta que su administrador la cambie.

## Instalación para profesores

### Elegir la vía adecuada

| Situación | Qué hacer |
| --- | --- |
| ChatGPT de tu organización | Pedir al administrador que incorpore el marketplace; después instalar el plugin desde los plugins de ese espacio de trabajo. |
| Claude con plugins disponibles | Añadir el marketplace desde Personalizar y después instalar Asistente docente. |
| ChatGPT individual, sin espacio administrado | Consultar la alternativa con [Codex CLI](#codex-cli); no se presupone una importación gráfica para cualquier cuenta. |

Los pasos con los nombres de menús están en el
[Inicio rápido del README](../README.md#inicio-rápido).
No necesitas descargar ZIP, clonar el repositorio ni preparar Python para seguir
ese recorrido. En Claude necesitas un plan con plugins; las políticas de tu
organización también pueden limitar las fuentes admitidas.
[Disponibilidad y menús de Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

### Si no aparece el plugin

En ChatGPT, comprueba que estás en el espacio de trabajo donde se importó el
marketplace y que su responsable lo habilitó para tu perfil. Facilítale el
[enlace del repositorio](https://github.com/cjescudero/asistente-docente) y la
[sección para administradores](#instalación-para-administradores).

En Claude, confirma que añadiste el repositorio y que estás viendo sus plugins.
Puede aparecer con el identificador `asistente-docente`. Si la organización
bloquea ese marketplace, solicita su autorización al responsable. No hace falta
buscar el plugin entre los publicados por OpenAI o Anthropic.

### Empezar con un curso

Tras instalarlo, abre una conversación nueva en ChatGPT Work o Claude Cowork.
Selecciona una carpeta para tu curso y concede al agente acceso a ella. Puede
ser una carpeta local sincronizada con OneDrive o SharePoint, con los archivos
disponibles localmente. Instalar el plugin no concede ese acceso ni configura
la sincronización.

Pide **«Inicia mi proyecto docente»**. Puedes añadir la materia y el nivel, si
los conoces. La skill ya implementada:

- Pregunta solo por el contexto, las carpetas, los tipos de material y las
  exclusiones que falten; permite dejar la selección pendiente.
- Prepara `alumnado/`, `docente/` y `archivo/`, la configuración
  `proyecto-docente.json`, una guía `LEEME.md` y las instrucciones `AGENTS.md`.
- Respeta las instrucciones previas, pregunta ante conflictos y conserva la
  preferencia de español claro. Propone una migración antes de mover originales.
- Comprueba las entradas y capacidades disponibles y explica lo pendiente.
  La puesta en marcha deja la carpeta del mapa vacía; no crea ni propone la wiki.

Comprueba que el agente ha leído `AGENTS.md`; si su aplicación no lo carga,
pídele que lo lea al comenzar. El plugin no genera `CLAUDE.md` por sistema.
Una petición sencilla con texto o adjuntos suficientes puede resolverse sin wiki
ni proyecto completo. Véanse el [contrato del curso](PROYECTO-DOCENTE.md), el
[ejemplo sintético](../examples/proyecto-docente/README.md) y la
[migración desde 0.6](MIGRACION-0.7.md).

## Instalación para administradores

### ChatGPT: incorporación al espacio de trabajo

Utiliza el recorrido de [instalación en ChatGPT del README](../README.md#instalación-en-chatgpt)
con una cuenta administradora y selecciona el espacio de trabajo correcto.
El repositorio es `https://github.com/cjescudero/asistente-docente`; el campo
**Ruta debe quedar vacío**, porque los catálogos están en la raíz del repositorio.
No introduzcas la ruta de un archivo JSON ni una URL de carpeta de GitHub.

La cuenta GitHub autorizada para importar debe poder leer el repositorio y
mantener ese acceso. Revisa el resultado de importación y establece la política
de instalación para los roles docentes: **Disponible** si cada profesor lo
instala, o **Instalado** cuando corresponda a la política de la organización.
Los valores del catálogo no sustituyen esta configuración del espacio de trabajo.
Asistente docente no incluye conectores ni exige conectar cuentas de Moodle.
[Importación y permisos oficiales](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github).

Puedes dejar vacía la referencia de rama para seguir la rama predeterminada,
o fijar una revisión aprobada. Las actualizaciones del repositorio pueden
incorporarse mediante la sincronización diaria. Para solicitarlas manualmente,
abre **Plugins → Marketplaces**, selecciona el catálogo y pulsa **Sync now**.
Revisa el informe y la versión resultante antes de anunciar la actualización.
[Gestión de marketplaces](https://learn.chatgpt.com/docs/enterprise/plugin-management).

### Claude: permisos de la organización

La vía del README añade directamente el marketplace público de este proyecto
por la interfaz de Claude. Un responsable con rol Owner o Primary Owner puede
limitar los repositorios permitidos; debe permitir esta fuente si el profesorado
va a añadirla. Las listas se gestionan en los ajustes administrados de
**Organization settings → Claude Code** y también afectan a Claude y Cowork.

No confundir esa vía con la sincronización central de un repositorio de la
organización. Según la documentación actual, **Sync from GitHub** para
marketplaces organizativos admite repositorios privados o internos, no este
repositorio público directamente. Si la institución elige esa vía, debe mantener
una copia privada o interna aprobada, conservar el catálogo y gestionar sus
actualizaciones desde el origen público.

Para esa copia, el recorrido es **Organization settings → Plugins & skills →
Marketplaces → Add plugins → Sync from GitHub**. Conecta el repositorio de la
institución y define el acceso de los miembros. Las actualizaciones de la copia
se sincronizan desde esa sección con **Update** o según su configuración
automática. Esta es una opción de administración, no un paso que deba realizar
cada profesor. [Gestión oficial de plugins en organizaciones Claude](https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization).

### Qué contiene el repositorio

| Archivo | Función |
| --- | --- |
| `.agents/plugins/marketplace.json` | Catálogo para OpenAI/Codex; apunta al plugin en la raíz. |
| `.claude-plugin/marketplace.json` | Catálogo para Claude; apunta al mismo contenido. |
| `plugin.json` | Identidad, versión y presentación comunes en Agent Plugins 1.0. |
| `.codex-plugin/plugin.json` y `.claude-plugin/plugin.json` | Adaptadores generados para sus clientes. |

Añadir estos catálogos no publica el plugin en ningún directorio público ni lo
habilita en todas las cuentas. Publicar una release en GitHub tampoco lo instala
en las aplicaciones. Los ZIP de plugin no incluyen marketplaces: para esta vía
se utiliza el repositorio completo. El ZIP `*-source.zip` sí conserva los
catálogos. Los formatos admitidos se documentan en
[OpenAI](https://learn.chatgpt.com/docs/enterprise/plugin-management) y
[Claude Code](https://code.claude.com/docs/en/plugin-marketplaces).

## Instalación avanzada

Estos procedimientos son para personas que usan terminal o prestan soporte.
No son requisitos para el recorrido gráfico del profesorado.

### Codex CLI

Alternativa para una cuenta individual sin espacio de trabajo administrado.
Necesitas Codex CLI con soporte de marketplaces y acceso a GitHub. Comprueba
que `codex plugin marketplace --help` esté disponible y registra el origen:

```sh
codex plugin marketplace add https://github.com/cjescudero/asistente-docente.git
codex plugin marketplace list
```

Esto registra el catálogo; después inicia `codex` y escribe `/plugins` dentro
de su sesión. Elige el marketplace `asistente-docente` e instala el plugin.
Abre una sesión nueva sobre la carpeta del curso para cargar sus skills.
La [gestión de fuentes de Codex](https://developers.openai.com/plugins/build/plugins)
y el [navegador de plugins de la CLI](https://learn.chatgpt.com/docs/plugins#plugin-browser-in-codex-cli)
describen ambos pasos. Si el comando no existe, actualiza Codex según su guía;
no se sustituye por una supuesta importación gráfica en cualquier cuenta web.

Para refrescar el origen configurado, usa
`codex plugin marketplace upgrade asistente-docente` y revisa la actualización
del plugin en `/plugins`. Esta instalación es para el entorno Codex: no incorpora
el marketplace a un espacio de trabajo administrado de ChatGPT.

### Claude Code

En una sesión de Claude Code, añade el marketplace e instala su plugin:

```text
/plugin marketplace add cjescudero/asistente-docente
/plugin install asistente-docente@asistente-docente
```

Inicia una sesión nueva en la carpeta del curso. Para revisar actualizaciones,
abre `/plugin`, selecciona el marketplace en **Marketplaces** y su acción de
actualización. No asumas que un marketplace externo tenga actualizaciones
automáticas activadas. [Instalación y gestión en Claude Code](https://code.claude.com/docs/en/discover-plugins).

### Código fuente y copias locales

Para desarrollar, revisar o preparar utilidades fuera del anfitrión:

```sh
git clone https://github.com/cjescudero/asistente-docente.git
cd asistente-docente
```

Conserva toda la carpeta: las skills comparten documentación, recursos y scripts.
No basta con copiar un `SKILL.md`. Mantén la instalación separada de los cursos.
Para registrar una copia local, usa `codex plugin marketplace add ./asistente-docente`
o, dentro de Claude Code, `/plugin marketplace add ./asistente-docente`, desde
la carpeta que contiene esa copia. El paso posterior de instalación sigue siendo
necesario. No edites las cachés internas de las aplicaciones.

### Dependencias Python

Crear carpetas, configuración e instrucciones puede hacerse con las herramientas
de archivos del agente, sin Python. Las utilidades que lo usan necesitan
**Python 3.10 o posterior**; su instalación es independiente de instalar el plugin.

| Capacidad | Requisito adicional |
| --- | --- |
| Bancos GIFT, feedback CSV, validación del mapa y grafo | Biblioteca estándar de Python |
| Lector de la wiki y conversión de Markdown | `requirements.txt` |
| PDF | `requirements-pdf.txt` y un navegador compatible |
| Imágenes y lectura de originales PDF o diapositivas | Herramientas disponibles en el anfitrión |

Reutiliza el entorno disponible si es suficiente. Para preparar otro, desde la
carpeta del plugin, usa `python3 scripts/setup_environment.py` en macOS/Linux o
`py -3 scripts/setup_environment.py` en Windows. El instalador muestra el
intérprete y cómo ejecutar el diagnóstico; guarda el entorno en la caché del
usuario, fuera del curso y del plugin.

Opciones: `--pdf` añade Playwright y Chromium; `--dev` prepara las dependencias de
desarrollo en `.venv`; `--venv RUTA` elige un destino externo; `--dry-run` muestra
las operaciones sin ejecutarlas. Una instalación de solo lectura requiere un
entorno externo. En Linux, consulta los
[requisitos de sistema de Playwright](https://playwright.dev/python/docs/browsers#install-system-dependencies)
si el navegador no arranca.

Con ese intérprete, `scripts/docencia.py doctor` comprueba capacidades y
`doctor --project RUTA_CURSO` añade el diagnóstico del curso. `basic_ready` y
`pdf_ready` son estados distintos; `doctor --pdf` exige las capacidades PDF.
`ASISTENTE_DOCENTE_CHROMIUM` permite indicar un navegador existente. Si falta
PDF, se conservan los archivos editables y HTML y se comunica el resultado pendiente.

## Comprobación y mantenimiento

Verifica la versión instalada y prueba primero con el
[curso sintético](../examples/proyecto-docente/README.md). Las actualizaciones del
plugin no migran automáticamente los materiales ni las instrucciones del curso.
Desinstalarlo no elimina esos archivos, que viven fuera de su instalación.

La documentación de los procedimientos se contrastó el **20 de octubre de 2026**
con las fuentes oficiales enlazadas. Esa revisión y la validación de manifiestos
no acreditan una instalación real en una cuenta de ChatGPT o Claude. Registra
por separado las pruebas de interfaz, permisos y carga de `AGENTS.md` siguiendo
[Compatibilidad](COMPATIBILIDAD.md). La carga de instrucciones depende de la
[versión y configuración de Claude Code](https://code.claude.com/docs/en/memory)
y del [recorrido de carpeta de Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork).
