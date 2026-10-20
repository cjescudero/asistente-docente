# Curso inicializado de ejemplo

[curso/LEEME.md](curso/LEEME.md) explica la organización. Contiene materiales
sintéticos sobre interpretación de datos y fuentes, adaptables a humanidades
y ciencias. No contiene datos de estudiantes ni afirma una lectura por el agente.

Para probarlo, pide al agente que copie **solo la carpeta `curso`** a una
ubicación de trabajo fuera del plugin, la abra y ejecute «Inicia mi proyecto
docente». La copia es un ejemplo reutilizable, no una exportación de materiales
del profesor. Git y los ZIP no conservan carpetas vacías: la iniciación completa
`docente/mapa-docente/` vacía cuando falte, sin crear wiki, índice, lector ni grafo.

La configuración selecciona `alumnado/materiales/`, `docente/fuentes/` y
`docente/evaluaciones/`. Excluye `docente/evaluaciones/examen-retirado.md`.
El examen vigente es una fuente reservada, no un documento para el alumnado.
Actividades, conocimientos, soluciones, rúbricas y archivo no forman parte de
esta selección; resultados, borradores y mapa están excluidos por diseño.

Peticiones para comprobar el recorrido:

1. «Comprueba qué fuentes están seleccionadas y qué falta por preparar».
2. «Revisa la redacción de interpretar-datos.md». Debe poder hacerse sin wiki.
3. «Propón una actividad a partir de las fuentes elegidas». Su destino inicial
   será `docente/borradores/`, sin entregar soluciones al alumnado.
4. En un encargo separado: «Crea el mapa docente con esta selección». Debe
   mantener el examen vigente reservado y omitir el retirado.
5. «Excluye el examen vigente y comprueba qué páginas requieren revisión».
   Si ya se usó en la wiki, debe señalar sus dependencias antes de reutilizarlas.

La [guía de migración](../../docs/MIGRACION-0.7.md) cubre cursos existentes.
El [registro de comprobaciones](../../docs/VALIDACION.md) distingue pruebas
automatizadas, evaluación del procedimiento e instalaciones reales.
