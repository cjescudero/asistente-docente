# Curso sintético `curso-v3`

Este ejemplo muestra la organización preparada para 0.11.0. Contiene solo
datos inventados y una fuente breve. La [guía del curso](curso/LEEME.md) explica
sus carpetas y la [configuración](curso/_datos_internos_proyecto/proyecto-docente.json)
selecciona `fuentes/teoria/`. El mapa está vacío porque su creación requiere un
encargo aparte.

El [banco GIFT](curso/materiales_generados/bancos/fuentes-medicion/banco.gift)
contiene dos preguntas principales con cuatro variantes cada una. Su
[catálogo](curso/materiales_generados/bancos/_datos_internos/catalogo.json)
enlaza el banco y los metadatos sin duplicar la fuente. El
[cuestionario](curso/materiales_generados/cuestionarios/fuentes-y-medicion/LEEME.md)
reúne cuatro modelos HTML de estudiante, solucionarios, GIFT ofuscados,
selección, manifiesto y bancos congelados. Se generó con `--html-only`; este
ejemplo no afirma que incluya PDF para imprimir.

Los archivos internos son consultables por las utilidades, pero quedan fuera de
la selección de fuentes de la wiki. El ejemplo demuestra la separación física,
no concede permisos ni simula una importación real en Moodle.
