# Curso inicializado de ejemplo: fuentes y creaciones separadas

[curso/LEEME.md](curso/LEEME.md) explica la organización. Contiene materiales
sintéticos sobre interpretación de datos y fuentes, adaptables a humanidades
y ciencias. No contiene datos de estudiantes ni afirma una lectura por el agente.

Para probarlo, pide al agente que copie **solo la carpeta `curso`** a una
ubicación de trabajo fuera del plugin, la abra y ejecute «Inicia mi proyecto
docente». La copia es un ejemplo reutilizable, no una exportación de materiales
del profesor. Git y los ZIP no conservan carpetas vacías: la iniciación completa
`mapa-docente/` vacía cuando falte, sin crear wiki, índice, lector ni grafo.

La configuración `curso-v3` selecciona `fuentes/teoria/` y
`fuentes/evaluaciones/cuestionarios/`. Excluye
`fuentes/evaluaciones/cuestionarios/cuestionario-retirado.md`.
El cuestionario vigente es una fuente reservada, no un documento para el alumnado.
La actividad aportada en `fuentes/actividades/` tampoco forma parte de esta
selección.

`materiales_generados/actividades/actividad-pendiente/` reúne un enunciado y una rúbrica en
preparación, separados por destinatario. Su registro `_datos_internos/material-docente.json`
indica `borrador`; no se puede incorporar al mapa. El material de dudas
frecuentes en `materiales_generados/materiales/` está `revisado`, pero tampoco se utiliza
en la wiki hasta que se seleccione expresamente. Ambos muestran su estado en
`LEEME.md`; cambiarlo no implica mover los archivos.

Resultados y mapa quedan siempre fuera del corpus. El archivo requiere
selección explícita. Los nombres de carpetas no configuran permisos.

Peticiones para comprobar el recorrido:

1. «Comprueba qué fuentes están seleccionadas y qué falta por preparar».
2. «Revisa la redacción de interpretar-datos.md». Debe poder hacerse sin wiki.
3. En un encargo separado: «Crea el mapa docente con esta selección». Debe
   mantener el cuestionario vigente reservado y omitir el retirado.
4. «Propón una actividad a partir de las fuentes elegidas». Su destino será
   `materiales_generados/actividades/<identificador>/`, con estado borrador y documentos
   del alumnado y del docente separados. Al terminar, la sugerencia de evaluar
   debe explicar que antes hacen falta entregas identificadas y criterios.
5. «Crea un banco para evaluar estos conocimientos». Después se podrán preparar
   modelos impresos; el feedback requerirá sus resultados por pregunta.
6. «Excluye el cuestionario vigente y comprueba qué páginas requieren revisión».
   Si ya se usó en la wiki, debe señalar sus dependencias antes de reutilizarlas.

También puedes pedir apuntes o diapositivas visuales individuales. Las sugerencias
deben reconocer los resultados ya comprobados y no iniciar el siguiente paso
automáticamente. El idioma predeterminado es español claro.

La [guía del proyecto](../../docs/PROYECTO-DOCENTE.md) cubre la organización y
la organización de carpetas que ya contienen materiales.
El [registro de comprobaciones](../../docs/VALIDACION.md) distingue pruebas
automatizadas, evaluación del procedimiento e instalaciones reales.
