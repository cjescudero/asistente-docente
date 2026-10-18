# Compatibilidad e instalación

## Formatos

La fuente canónica usa Agent Plugins 1.0.0: `plugin.json` en la raíz y skills
como hijos directos de `skills/`. OpenAI utiliza `extensions.com.openai` para
la presentación. Los adaptadores se generan con `scripts/sync_manifests.py`. El ZIP Claude añade su manifiesto en
`.claude-plugin/plugin.json` y omite el manifiesto portable. La identidad y
versión de ambos salen del mismo archivo fuente.

Referencias oficiales:

- [Agent Plugins 1.0.0](https://agent-plugins.org/specification).
- [Empaquetado OpenAI](https://developers.openai.com/plugins/build/plugins).
- [Plugins de Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).
- [Requisitos de subida Claude](https://platform.claude.com/docs/en/manage-claude/plugins-api#upload-requirements).

La fuente conserva también `.codex-plugin/plugin.json`, generado para clientes
Codex que lo admitan. Los catálogos `.agents/plugins/marketplace.json` y
`.claude-plugin/marketplace.json` permiten distribuir desde un repositorio GitHub.
Los catálogos se incluyen en la fuente, no en los ZIP de un plugin individual.
La [guía de instalación](INSTALACION.md) separa esos flujos y sus requisitos.
No se necesitan MCP, hooks ni variables exclusivas de un anfitrión.

La versión 0.6.0 distribuye doce skills en ambos paquetes:
`asistente-docente-0.6.0-agent-plugins.zip` y
`asistente-docente-0.6.0-claude.zip`. El Mapa docente usa páginas Markdown con
enlaces relativos estándar e inventario JSON; no requiere Notion, Obsidian ni
frontmatter. Su grafo se genera con Python estándar y funciona como HTML autónomo
sin acceso a la red. La lectura del corpus y la revisión visual requieren las
capacidades correspondientes del anfitrión.
El lector navegable `index.html` requiere `markdown-it-py` al generarse;
su consulta posterior es local y no necesita Python, servidor ni conexión.

Cada carpeta fuente debe haber sido elegida por el usuario. El registro versión 2
admite varias raíces relativas y clasifica por separado las páginas, sus fuentes
y sus accesos. Si no hay una ruta relativa posible, como entre distintas unidades
de Windows, se debe comunicar la limitación. El plugin no mueve ni copia los
originales para resolverla sin una petición que lo autorice.

## Prueba en cada anfitrión

1. Construir los paquetes y comprobar los hashes de `release/SHA256SUMS`.
2. Instalar desde el catálogo del repositorio siguiendo la guía. Usar el ZIP
   solo si el anfitrión ofrece esa opción. Registrar cualquier limitación de acceso.
3. Confirmar nombre, versión 0.6.0 y doce skills; comprobar que los recursos del
   paquete son accesibles desde las skills.
4. Pedir una actividad breve con fuentes sintéticas. Revisar rigor, nivel,
   separación entre enunciado y solución y generación real de Markdown/PDF.
5. Ejecutar el circuito del README con los ejemplos. Comprobar que HTML, PDF,
   GIFT, snapshot y manifiesto se guardan en la carpeta elegida para el curso.
6. En el caso visual, comprobar imagen real cuando haya generador; si no lo
   hay, comprobar que se entrega diseño y prompt sin declarar imagen generada.
7. Preparar fuera del plugin una copia del ejemplo sintético del Mapa docente,
   eligiendo explícitamente sus dos carpetas fuente. Consultar contenidos vigentes
   y el examen histórico: comprobar citas, lectura parcial y que no se escriben
   páginas, log ni grafo durante la consulta.
8. Añadir una fuente sintética y pedir actualizar el mapa. Comprobar páginas
   afectadas y regeneración del lector y del grafo. Modificar después una fuente ya registrada:
   la huella distinta debe provocar revisión, no continuidad silenciosa de la síntesis.
9. Abrir los HTML sin red y probar arrastre, zoom, búsqueda, filtros y panel.
   Tras filtrar, «Reorganizar» distribuye los nodos visibles y conserva selección
   y filtros; «Ajustar» solo encuadra. Desde un nodo abrir documentos de la wiki
   renderizados y sus Markdown. Recorrer índice, enlaces, anclas y volver en el
   lector. Comprobar originales, sección reservada y evaluaciones ocultas al inicio.
10. Generar la vista estudiantil. Inspeccionar los datos del HTML: excluir fuentes
    no autorizadas, páginas que dependan de ellas directa o indirectamente y
    enlaces salientes a archivos. El filtro docente no basta para esta prueba.
11. En un proyecto de prueba externo al plugin, invocar la puesta en marcha.
    Comprobar que crea o integra instrucciones generales en `AGENTS.md`, conserva
    las reglas y pregunta ante conflictos. Verificar español claro por defecto
    y la pregunta por ubicación y tipos de materiales solo si faltan. No debe
    proponer ni invocar la creación del mapa.
    Después pedir crear el mapa de carpetas elegidas: debe integrar su bloque en
    `AGENTS.md` con rutas válidas desde él. Probar también sin puesta en marcha
    previa y con un bloque de la versión 0.5.0. Repetir sin duplicar reglas.
    Consultar desde el índice hasta un original enlazado, evitando ciclos y la
    lectura completa del corpus y sin modificarlo durante la consulta.
12. Registrar fecha, versión del anfitrión, pasos, resultados y limitaciones.

Una cuenta puede permitir skills pero restringir ejecución, dependencias o
generación de archivos. El paquete no instala automáticamente un runtime en el
anfitrión. No sustituir silenciosamente un PDF pedido por HTML. El Mapa docente
requiere acceso a los archivos del curso; instalar el plugin no comparte esos
archivos entre anfitriones. Si no existe un lector para un formato, registrar
la fuente pendiente o no legible, sin inventar su contenido.

La puesta en marcha genera instrucciones generales en `AGENTS.md`; la creación
o actualización del mapa incorpora en ese archivo el bloque que lo establece
como punto de partida del proyecto. Su carga automática depende del anfitrión.
Comprobar que las incorpora a la tarea; si no lo hace, adjuntar el archivo o pedir
su lectura explícita. Ninguna de estas skills crea `CLAUDE.md` ni modifica
instrucciones globales como efecto secundario.

Sin Python, el agente puede mantener el Markdown mediante las capacidades de
archivos disponibles, pero debe declarar la validación automática y el grafo
pendientes. Generar HTML no demuestra que se hayan probado sus controles. Una
vista docente contiene información aunque sus nodos estén ocultos; ni Markdown
ni HTML aplican permisos. La vista estudiantil no distribuye los originales.

El validador admite registros de versión 1; el grafo requiere versión 2. Si se
solicita actualizar un mapa anterior, migrarlo en una copia sin alterar el mapa
anterior ni los originales. Véase [Mapa docente](MAPA-DOCENTE.md).

## Distribución en GitHub

Licencia MIT y repositorio elegidos por el propietario. Los paquetes incluyen
los avisos de terceros. Seguir [la guía de publicación](PUBLICACION-GITHUB.md)
para revisar la fuente, construir artefactos y comprobar las instalaciones
reales. La preparación local no publica repositorios, marketplaces ni plugins.
