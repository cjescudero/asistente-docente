# Instalación de Asistente docente

Asistente docente se distribuye desde un repositorio público. Para ChatGPT, Codex
y Claude se añade el marketplace de GitHub a la aplicación o al espacio de
trabajo y después se instala el plugin. OpenCode 2.x carga las skills desde una
copia local del proyecto. [Repositorio en GitHub](https://github.com/cjescudero/asistente-docente).

- [Instalación para profesores](#instalación-para-profesores): sin terminal.
- [Instalación para administradores](#instalación-para-administradores): permisos y actualizaciones.
- [Instalación avanzada](#instalación-avanzada): Codex CLI, Claude Code, OpenCode y Python.

Consulta las [publicaciones en GitHub](https://github.com/cjescudero/asistente-docente/releases) para conocer los cambios disponibles. Después de actualizar el marketplace, comprueba la versión instalada. Si está fijada a una revisión concreta, el administrador puede cambiarla para recibir las novedades.

## Instalación para profesores

### Elegir la vía adecuada

| Situación | Qué hacer |
| --- | --- |
| ChatGPT de tu organización | Pedir al administrador que incorpore el marketplace; después instalar el plugin desde los plugins de ese espacio de trabajo. |
| Claude con plugins disponibles | Añadir el marketplace desde Personalizar y después instalar Asistente docente. |
| Codex o Claude Code | Instala el plugin desde el marketplace del repositorio. Sigue los pasos de [Codex CLI](#codex-cli) o [Claude Code](#claude-code). |
| OpenCode 2.x | Descarga el paquete fuente y configura la ruta a `skills/`. Sigue los pasos de [OpenCode](#opencode). |
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

Tras la instalación, abre una conversación en ChatGPT Work o Claude Cowork,
o inicia Codex, Claude Code u OpenCode en la carpeta del curso.
Selecciona una carpeta para tu curso y concede al agente acceso a ella. Puede
ser una carpeta local sincronizada con OneDrive o SharePoint, con los archivos
disponibles localmente. Instalar el plugin no concede ese acceso ni configura
la sincronización.

Pide **«Inicia mi proyecto docente»**. Puedes añadir la materia y el nivel, si
los conoces. La skill ya implementada:

- Pregunta solo por el contexto, las carpetas, los tipos de material y las
  exclusiones que falten; permite dejar la selección pendiente.
- Prepara los espacios **Material de la asignatura**, **Material generado por IA** y **Entregas**. Si ya tienes carpetas, puedes asignar las tuyas y seguir trabajando con ellas.
- Conserva las instrucciones del profesor en `AGENTS.md`, consulta los conflictos y pide aprobación antes de trasladar originales.
- Comprueba las entradas y capacidades disponibles. Cuando haga falta una selección persistente o un catálogo, se crea **Gestión del proyecto**.
- Recomienda crear el mapa. Puedes encargarlo cuando hayas elegido las carpetas que le servirán de fuente.

Comprueba que el agente ha leído `AGENTS.md`; si su aplicación no lo carga,
pídele que lo lea al comenzar. El plugin no genera `CLAUDE.md` por sistema.
Una petición sencilla con texto o adjuntos suficientes puede resolverse sin wiki
ni proyecto completo. Véanse el [contrato del curso](PROYECTO-DOCENTE.md), el
[ejemplo sintético](../examples/curso-v4/README.md).

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

También puedes usar Codex como entorno habitual para trabajar en la carpeta del curso.
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

### OpenCode

1. Descarga y descomprime el ZIP `*-source.zip`, o clona el repositorio. Guarda
   la copia completa fuera de la carpeta del curso para conservar las referencias
   a la documentación, las plantillas y los scripts. [Descargas en GitHub](https://github.com/cjescudero/asistente-docente/releases).
2. Ejecuta `opencode --version` para confirmar que utilizas OpenCode 2.x. En la raíz
   del curso, crea `opencode.json` o añade la entrada al archivo `opencode.json`
   o `opencode.jsonc` que ya uses. Conserva los demás ajustes y las rutas de
   skills que ya tengas.
3. Sustituye `/ruta/asistente-docente/skills` por la ruta absoluta a la carpeta
   `skills/` de tu copia. En Windows puedes escribir la ruta con barras
   inclinadas, por ejemplo `C:/Herramientas/asistente-docente/skills`.

**OpenCode 2.x** usa una lista directamente en `skills`.

```json
{
  "skills": ["/ruta/asistente-docente/skills"]
}
```

Abre una sesión nueva de OpenCode en la carpeta del curso. Si OpenCode te pide
permiso para leer archivos externos, revisa que la ruta solicitada pertenezca
a tu copia de Asistente docente. La ruta de skills carga la colección y el
agente consulta sus archivos de apoyo a medida que los necesita.
[Configuración de skills en OpenCode 2.x](https://opencode.ai/docs/skills/).

#### Probar el primer uso en OpenCode

Copia el contenido de `originales/` del curso de ejemplo a una carpeta nueva
y configura OpenCode ahí. [Curso de ejemplo](../examples/curso-v4/README.md).

Abre una sesión en esa carpeta y pide lo siguiente.

> Inicia mi proyecto docente. Usa «Unidad 1» como material de la asignatura y
> fuente para la wiki, «Producción» para los materiales nuevos y «Trabajos
> recibidos» para las entregas. Aplica esta organización y conserva los
> originales en su sitio.

Si el agente pide más instrucciones, puedes indicarle **«Usa la skill
`proyecto-docente-inicializacion-adaptacion` y la asignación de `espacios.json`
del ejemplo `curso-v4`»**. El ejemplo incluye el comando de inicialización para
reproducir la prueba desde la terminal.

Comprueba que `AGENTS.md` recoge los espacios, que existe
`Gestión del proyecto/proyecto-docente.json` con «Unidad 1» seleccionada y que
el guion y las mediciones siguen en su carpeta. El agente puede proponer crear
el mapa como próximo paso. Encárgaselo cuando quieras iniciar ese trabajo.
[Qué prepara la inicialización](#empezar-con-un-curso).

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
[curso sintético](../examples/curso-v4/README.md). Las actualizaciones del
plugin no migran automáticamente los materiales ni las instrucciones del curso.
Desinstalarlo no elimina esos archivos, que viven fuera de su instalación.

La documentación de los procedimientos se contrastó el **20 de octubre de 2026**
con las fuentes oficiales enlazadas. Esa revisión y la validación de manifiestos
no acreditan una instalación real en una cuenta de ChatGPT o Claude. Registra
por separado las pruebas de interfaz, permisos y carga de `AGENTS.md` siguiendo
[Compatibilidad](COMPATIBILIDAD.md). La carga de instrucciones depende de la
[versión y configuración de Claude Code](https://code.claude.com/docs/en/memory)
y del [recorrido de carpeta de Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork).
