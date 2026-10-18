# Validación local

Fecha: 18 de octubre de 2026. Versión actual: **0.6.0**.

## Preparación pública y generalidad (0.6.0)

**205 pruebas aprobadas, incluidas las dos PDF, sin omisiones** en macOS,
Python 3.12.9 y Chrome local mediante un perfil temporal. No se ha cambiado el
renderizador; se comprueban además las nuevas funciones de distribución e
instalación. El código común de ambos paquetes es idéntico, las construcciones
son reproducibles y la fuente extraída reconstruye los mismos ZIP desde otra
carpeta. Los paquetes extraídos funcionan con la instalación de solo lectura.

Se verifican exclusión de archivos de entorno y cachés, licencia y avisos,
catálogos y adaptadores sincronizados, recursos compartidos y enlaces locales.
Se detectan un adaptador desactualizado y la ausencia de licencia. La suite
comprueba los comandos de instalación por plataforma, el rechazo de un destino
que no sea un entorno, el modo sin cambios y la parada ante fallos de instalación.

Instalación básica real en un entorno virtual temporal nuevo: descarga de
markdown-it-py y mdurl, diagnóstico `basic_ready: true`, `pdf_ready: false`, y
lector de trece documentos generado desde otra carpeta, sin Playwright ni
navegador en ese entorno. Esta prueba no sustituye una instalación de las skills
en un anfitrión. No se han modificado configuraciones globales.

Claude Code 2.1.50 valida sin errores ni avisos el manifiesto y el catálogo de
Claude. No se ha instalado el plugin en Claude Cowork ni ChatGPT Work. El
comando Codex disponible en esta máquina no permite comprobar la instalación
porque su ejecutable interno no está disponible; los archivos se validan con
las reglas locales y las referencias oficiales. Esta validación local no incluye
GitHub Actions ni importaciones nuevas en Moodle. Las ejecuciones remotas se
consultan por separado en [GitHub Actions](https://github.com/cjescudero/asistente-docente/actions).

Las doce skills y sus plantillas se revisaron para separar ejemplos de reglas
obligatorias; véase [generalidad](GENERALIDAD.md). Las pruebas no acreditan un
resultado pedagógico en toda disciplina. No se repitió la revisión visual de
la wiki o el grafo, cuyos generadores y presentación no cambian en esta versión.

## Respeto de instrucciones, redacción y orígenes (0.5.2)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF opcionales omitidas.** Sin
errores en el validador del plugin ni en los validadores de las skills de inicio
y redacción. La suite incluye extracción, equivalencia y portabilidad de ambos
paquetes. Se revisaron las instrucciones y los casos del catálogo para conservar
AGENTS.md, preguntar ante conflictos, registrar español claro por defecto y
solicitar solo ubicación o tipos de contenidos desconocidos, sin iniciar el mapa.

No se realizó una nueva simulación de conversación para esos casos ni pruebas
en cuentas externas. Las pruebas Python no verifican por sí solas que un agente
respete el procedimiento de preguntas. No se repiten PDF ni revisión visual,
porque esta versión modifica instrucciones y documentación, no renderizadores.

## Responsabilidades de inicio y creación del mapa (0.5.1)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF opcionales omitidas.** El
validador del plugin y los validadores de las dos skills modificadas no presentan
errores. La prueba de empaquetado comprueba la plantilla en la skill de creación
del mapa y su ausencia en la de inicio, además de equivalencia funcional y
ejecución de ambos paquetes extraídos fuera de la carpeta fuente.

Evaluación manual por un agente en dos proyectos temporales: la inicialización
de Historia creó solo instrucciones generales, sin preguntar por fuentes ni
continuar con el mapa. En una copia del mapa de ejemplo, el cierre de creación
integró el bloque en el `AGENTS.md` del proyecto y conservó una regla previa
del profesor. Comprobadas la entrada real y ambas raíces desde ese archivo.
La segunda aplicación mantuvo el resultado idéntico, sin duplicados; los otros
26 archivos de la copia conservaron sus huellas. El mapa de siete fuentes pasó
su validador. Esta evaluación se limita al reparto de instrucciones y al cierre
del flujo: no incluye una nueva síntesis del corpus ni renderizado.

No se repiten PDF ni revisión visual: no cambia el renderizado. Tampoco se ha
instalado esta versión en ChatGPT Work o Claude Cowork. La evaluación de 0.5.0
descrita debajo se conserva como historial y no representa el reparto actual
de responsabilidades.

## Puesta en marcha y consulta recursiva (0.5.0)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF opcionales omitidas.** El
validador del plugin y los validadores de las skills de puesta en marcha y
consulta no presentan errores. Las pruebas de empaquetado comprueban doce skills,
la nueva plantilla de `AGENTS.md`, contenido común idéntico, construcción
reproducible y ejecución desde los dos paquetes extraídos en otra carpeta, con
la instalación marcada de solo lectura.

Una evaluación manual por un agente, en un proyecto temporal con instrucciones
previas, aplicó la skill dos veces: conservó esas reglas, produjo una sola
sección sin campos pendientes y dejó el segundo resultado idéntico al primero.
Sin carpetas elegidas, no creó una wiki ni otras configuraciones; preparó la
pregunta de creación y selección de orígenes.

En un corpus sintético se siguió índice → concepto → ficha → original. El
original indicaba 40 ms y la síntesis 50 ms: la respuesta usó el original y
señaló la discrepancia. Se evitó un enlace cíclico al índice y no se aplicó como
vigente una rúbrica de 2023. La consulta conservó archivos, huellas SHA-256 y
fechas de modificación. Esta evaluación de instrucciones declarativas no es
una prueba de selección automática de la skill ni garantiza el comportamiento
de otros modelos o anfitriones.

No se han repetido la revisión visual de navegador ni las pruebas PDF: esta
versión cambia instrucciones, documentación y catálogo, sin modificar los
renderizadores. Las instalaciones reales en ChatGPT Work y Claude Cowork siguen
pendientes; la presencia de `AGENTS.md` no demuestra que un anfitrión lo cargue.

## Wiki navegable y reorganización (0.4.0)

**197 pruebas ejecutadas: 195 aprobadas y dos PDF omitidas.** Incluyen generación
conjunta del lector y el grafo, documentos asociados sin inventar aristas,
rutas relativas desde otras carpetas, originales protegidos, reproducibilidad,
HTML incrustado inerte, enlaces y anclas Unicode, autorreferencias y bloqueo del
lector docente en una exportación estudiantil. Ambos paquetes se extraen y
generan HTML desde otra carpeta con la instalación marcada de solo lectura.

El ejemplo conserva 16 nodos y 29 relaciones docentes, y 12 nodos y 21 relaciones
estudiantiles. El lector incluye 13 documentos (nueve páginas y cuatro de guía y
registro). No cambia fuentes, estados de lectura ni relaciones académicas.

Comprobación en Chrome local con perfil temporal, Playwright y solicitudes
HTTP/HTTPS bloqueadas: escritorio 1440 × 960 y móvil 390 × 844. Verificados
Reorganizar sobre el conjunto visible, conservación de búsqueda/filtros/selección,
Ajustar sin mover nodos, arrastre, teclado, zoom y navegación de documentos
HTML/Markdown. Casos sintéticos de 48 nodos sin solapamientos de cajas, 320
conectados y 600 nodos con encuadre completo. Los mapas grandes requieren zoom
o filtrado para leer todas las etiquetas; encuadrarlos no hace legible todo a la vez.

En el lector se han probado índice → página → otra página, anclas, volver/avanzar,
recarga de enlaces profundos, búsqueda, tipos, área reservada, salto accesible y
menú móvil. También el recorrido real del ejemplo grafo → documento → índice →
concepto → volver → grafo. Sin errores JavaScript, ejecución de contenido hostil
ni solicitudes remotas en estos casos. Revisadas capturas de ambas vistas.

Comprobaciones opcionales de navegador (requieren navegador local):

```sh
python tests/check_graph_browser.py --html examples/mapa-docente/mapa-docente/grafo-docente.html
python tests/check_graph_layout.py
python tests/check_wiki_browser.py --html examples/mapa-docente/mapa-docente/index.html
```

Las capturas se guardan fuera del paquete. No se han repetido los PDF ni las
instalaciones/importaciones reales en ChatGPT Work, Claude Cowork o Moodle.


## Mapa docente y grafo (0.3.0)

**176 pruebas ejecutadas: 174 aprobadas y dos pruebas PDF omitidas**. Se mantienen
los casos anteriores y se incorporan pruebas de varias raíces seleccionadas,
páginas clasificadas y grafo derivado. Se comprueban compatibilidad del registro
anterior, raíces inválidas, conservación de originales, enlaces relativos desde
otra carpeta, generación reproducible y sobrescritura limitada al derivado propio.

El HTML estudiantil se valida por contenido: excluye fuentes y páginas privadas,
referencias sin clasificar y dependencias transitivas, incluidos ciclos y fuentes
con rutas alias. Los títulos se serializan como datos; una cadena con cierre de
script no se ejecuta. Se comprueba que no contiene enlaces salientes a archivos.

El ejemplo actualizado usa dos carpetas de materiales elegidas para la
demostración, siete fuentes y nueve páginas. Produce 16 nodos y 29 enlaces para
docencia; 12 nodos y 21 enlaces para estudiantes. Los originales son documentos
Markdown sintéticos. El contenido reservado no aparece en los datos del HTML
estudiantil; en el docente, ocultar evaluaciones es solo un filtro visual.

Comprobación real con Playwright 1.60 y Chrome local, usando perfil temporal:
búsqueda con y sin tildes, filtros por tipo y acceso, selección por teclado,
panel de relaciones, arrastre, desplazamiento, rueda, botones de zoom y
restablecimiento, vista móvil y modo estudiante. Sin solicitudes HTTP/HTTPS,
errores JavaScript ni ejecución de títulos hostiles en los casos comprobados.
Se ha revisado visualmente el ejemplo en escritorio y móvil. El navegador
necesitó ejecutarse fuera del sandbox que impedía su arranque; no utilizó la
sesión de navegación del usuario.

La comprobación de navegador es optativa y se ejecuta aparte:

```sh
python tests/check_graph_browser.py --html examples/mapa-docente/mapa-docente/grafo-docente.html
```

`ASISTENTE_DOCENTE_CHROMIUM` permite indicar el ejecutable existente;
`--screenshots` acepta una carpeta externa al paquete. El grafo no necesita
Playwright para generarse o consultarse: se usa únicamente en esta prueba.

Los paquetes incluyen once skills. La suite extrae ambos ZIP y ejecuta
validación y generación desde otra carpeta; compara el contenido funcional
común y la construcción reproducible. Los dos PDF no se regeneran en esta
ampliación: su renderer y sus flujos no cambian. Las pruebas en las cuentas de
ChatGPT Work, Claude Cowork y una instancia Moodle siguen pendientes.

## Validación previa de biblioteca docente (0.2.0)

Suite local: **140 pruebas ejecutadas, 138 aprobadas y dos pruebas PDF omitidas**.
Se incorporan 32 pruebas de inventario, lectura parcial, rutas, enlaces, huellas,
datos malformados y funcionamiento de solo lectura. Se comprueba detección de
fuentes cambiadas, ausentes, duplicados de ID y rutas que salen del corpus.

El ejemplo sintético contiene seis fuentes: cuatro lecturas completas, una
parcial y una pendiente, con dos mapas temáticos. Su validación de estructura y
huellas no presenta errores. También se comprueba desde ambos paquetes
extraídos en otra carpeta. Los paquetes contienen diez skills y recursos
funcionales idénticos; la construcción es reproducible. Los ZIP finales se
extraen y el validador de biblioteca funciona desde otra carpeta con la
instalación marcada de solo lectura. Se comprueban sus SHA-256.

La comprobación semántica del ejemplo contrasta síntesis, localizadores y
restricciones con sus originales Markdown. No acredita lectura de archivos
PDF/PowerPoint reales ni lectura de un corpus del profesor. El validador no
comprueba anclas, precisión pedagógica ni cobertura declarada por el agente.

Una consulta representativa local, siguiendo la nueva skill, identificó la
ausencia de rúbrica vigente, conservó el 8/2 como criterio histórico, delimitó
el contenido de las diapositivas y consultó el apéndice en el original antes
de responder sobre él. La consulta no modificó fichas ni estados. Es una prueba
de seguimiento de instrucciones en este entorno, no de selección automática
o instalación de la skill en ChatGPT Work o Claude Cowork.

Las dos pruebas PDF no se repiten en esta ampliación: el renderer, las fórmulas,
los exámenes y el feedback no cambian. Se conserva abajo la evidencia de 0.1.0;
no se presenta como una nueva ejecución de PDF en 0.2.0.

## Validación previa (0.1.0)

**108 pruebas aprobadas**, incluidas las dos pruebas PDF, sin pruebas omitidas
en aquella ejecución completa. Ambos paquetes de esa versión superaron la
validación.

## Evidencias

- Parser GIFT: pruebas con los cinco tipos de banco, escapes, feedback, pesos,
  tolerancias, Unicode y entradas rechazadas explícitamente.
- Exámenes: pruebas de semilla, cuotas, reutilización de preguntas, snapshot,
  orden de opciones, verdadero/falso con B correcta y precisión numérica.
- Feedback: pruebas de notas y dialectos preservados, blancos explícitos,
  duplicados, datos ausentes, correspondencias, detalle opcional y consolidado.
- Renderizado: generación real de PDF con fórmulas, detección de macros no
  soportadas y conservación del HTML cuando no se completa un PDF.
- Nueve PDF de demostración generados: cuatro de humanidades, cuatro de ciencias
  y unos apuntes. Las nueve páginas se renderizaron y revisaron visualmente:
  sin texto cortado, soluciones en hojas del estudiante ni fórmulas pendientes.
- Circuito de feedback con tres identidades sintéticas: dos comentarios
  individuales y un no presentado sin comentario, conservando las notas.
- Empaquetado: estructura validada, contenido común idéntico, hashes, construcción
  reproducible y ejecución desde ambos ZIP extraídos en otra carpeta.

## Entorno y repetición

Python 3.12, Playwright 1.60.0 y Chrome local en macOS. El navegador se ejecutó
fuera del sandbox del agente, que impedía su arranque. Se usó un perfil temporal
de Playwright, sin la sesión de navegación del usuario. Las solicitudes de red
del documento se bloquearon; MathJax se cargó desde el recurso incluido.

```sh
python -m unittest discover -s tests -v
python scripts/validate_plugin.py
python scripts/validate_library.py examples/mapa-docente/mapa-docente
python scripts/build_release.py
```

Para incluir las dos pruebas PDF, establecer `RUN_PDF_TESTS=1` con Chromium
disponible. `ASISTENTE_DOCENTE_CHROMIUM` permite seleccionar un ejecutable local.
Sin esa variable se utiliza el Chromium instalado por Playwright. El resto de
las pruebas no necesita navegador ni conexión a Moodle.

## Límites de lo comprobado

No se han instalado los ZIP en cuentas de ChatGPT Work o Claude Cowork ni se han
importado preguntas o comentarios en una instancia real de Moodle. La
compatibilidad de empaquetado no sustituye esas pruebas. Están descritas en
[compatibilidad](COMPATIBILIDAD.md) y [Moodle](MOODLE.md).

El pipeline de GitHub está preparado para Linux, macOS y Windows, pero no se ha
ejecutado en GitHub. No se ha publicado el proyecto ni se ha asignado una licencia
pública a su contenido propio. Los casos del [catálogo](CATALOGO.md) permiten
evaluar cada skill en los anfitriones; la suite Python comprueba las utilidades,
no todas las decisiones pedagógicas del agente.
