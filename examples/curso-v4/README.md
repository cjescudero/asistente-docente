# Una asignatura con carpetas propias

Copia el contenido de `originales/` en una carpeta de curso nueva fuera del plugin. La unidad «Laboratorio» ya contiene su guion y un juego de datos sintéticos. Abre la carpeta y pide:

> Adapta mi curso. Conserva «Unidad 1» como material de la asignatura, usa «Producción» para el trabajo nuevo y «Trabajos recibidos» para las entregas. Usa «Unidad 1» como fuente para la wiki.

Pide **«Clasifica Laboratorio como Práctica y conserva juntos el guion y las mediciones»**. El catálogo puede heredar la clasificación para los datos sin moverlos. Después prueba **«Prepara unos apuntes sobre la variabilidad de las medidas»**. La salida pertenece a Producción. Cuando decidas incorporarla, pide «Consolida estos apuntes en Unidad 1 y actualiza las páginas del mapa que los necesiten».

Para probar un cambio manual, renombra el guion y pide que se actualice el catálogo. Compara el identificador y la versión antes y después. A continuación edita una lectura del CSV y vuelve a comprobarlos. Se conserva el identificador y aumenta la versión del contenido.

El archivo [espacios.json](espacios.json) contiene la asignación anterior. Para reproducir el inicio desde una terminal, desde el repositorio:

```sh
python scripts/docencia.py init-project "/ruta/al/curso" --spaces examples/curso-v4/espacios.json --include "Unidad 1"
python scripts/docencia.py catalog-sync "/ruta/al/curso"
python scripts/docencia.py catalog-show "/ruta/al/curso"
```

[Guion de laboratorio](originales/Unidad%201/Laboratorio/guion.md) · [Mediciones](originales/Unidad%201/Laboratorio/mediciones.csv) · [Guía de organización](../../docs/PROYECTO-DOCENTE.md).
