# Procedencia y distribución

El contenido propio de Asistente docente se distribuye bajo la [licencia MIT](LICENSE),
Copyright (c) 2026 Carlos J. Escudero. La licencia fue elegida por el propietario
el 18 de octubre de 2026. Los componentes de terceros conservan sus licencias.

Las skills de origen se adaptan dentro de este proyecto sin modificarlas.
Consulta [el registro de procedencia](docs/PROCEDENCIA.md). Los procedimientos de
TI aportan referencias de diseño; no se incorporan entregas, notas, excepciones
personales ni recursos de aquel curso.

## Dependencias distribuidas

MathJax 3.2.2, Apache License 2.0. Se incluyen el bundle `tex-svg.js`, su
`LICENSE`, metadatos npm y hashes en `assets/vendor/mathjax/`. Fuente:
https://registry.npmjs.org/mathjax/-/mathjax-3.2.2.tgz.
No se ha modificado el bundle. MathJax es una dependencia de renderizado, no un
proveedor ni una certificación del plugin.

El esquema Agent Plugins 1.0.0 se obtiene de
https://agent-plugins.org/schemas/1.0.0/plugin.schema.json para validar el
manifiesto localmente. No se requiere descargarlo durante el uso del plugin. Los esquemas son material
software bajo Apache-2.0 según el [aviso upstream](https://github.com/agentplugins/agent-plugins-spec/blob/ff8ab5e392cc87bd88d87c060815a87490e51003/LICENSE.md).
Se incluyen [su licencia](schemas/AGENT-PLUGINS-LICENSE.txt) y
[procedencia, revisión y huella](schemas/provenance.json). La copia coincide
semánticamente con la revisión indicada; no se han cambiado sus reglas.

Playwright y markdown-it-py se instalan como dependencias; no se distribuyen
entornos virtuales ni binarios de navegador. Las referencias visuales JPG/PNG
de la skill original no están incluidas: no tienen procedencia documentada en
esa fuente.

El estilo de redacción está inspirado en ASD-STE100, con adaptación editorial
propia al español. No se reproduce el estándar ni se declara certificación.
