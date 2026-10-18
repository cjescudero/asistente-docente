---
name: skill-crear-infografias-didacticas
description: Crear imágenes didácticas con estilo de boceto a mano para explicar conceptos, procesos o relaciones de cualquier disciplina, a partir de texto o documentos. Usar para diapositivas visuales o infografías; no activar para cualquier explicación textual, gráficos de datos exactos ni maquetación genérica de documentos.
---

# Crear infografías didácticas

Transformar el contenido en una explicación visual con fondo crema, tinta negra irregular, pasteles suaves y espacio en blanco. Por defecto, crear una imagen 16:9 de apoyo a una exposición oral por unidad lógica, con texto en español. Una instrucción explícita de formato, idioma, detalle o estilo prevalece.

## Capacidad disponible

Comprobar si el anfitrión dispone de una herramienta de generación de imágenes y seguir sus instrucciones. No depender de un proveedor ni de un nombre de herramienta concreto. Se pueden usar capacidades especializadas disponibles; no exigir generación «nativa propia».

Si no hay generación de imágenes, entregar un **brief visual y un prompt reutilizable**, indicando que la imagen queda pendiente. No sustituirla por SVG, HTML, diapositivas vectoriales o una ilustración programática por defecto; esas alternativas requieren que el usuario las elija. No afirmar que se ha generado o inspeccionado una imagen cuando solo existe un prompt.

Para fórmulas, geometría, magnitudes o datos exactos, usar representación verificable con herramientas adecuadas; no confiar a una imagen generativa la exactitud matemática. Si eso cambia el formato solicitado, explicar el punto y resolver la alternativa con el usuario.

## Tipo de imagen

**Apoyo a exposición, predeterminado.** Una única idea principal, tres a cinco anclas visuales, etiquetas de una a cuatro palabras y unas 12–25 palabras visibles en total. Sirve como recordatorio del ponente y estructura para el público. No introducir narración, notas del profesor, definiciones largas ni explicaciones completas.

**Infografía autónoma, cuando se pida.** Comprensible sin narración, con unas 35–70 palabras visibles, de tres a seis bloques y contexto suficiente. Dividir en varias imágenes si el contenido obliga a reducir demasiado la letra. Estos rangos orientan; el texto literal obligatorio puede exigir otra solución.

## Flujo

1. Leer fuentes y extraer estructura. En presentaciones, tratar cada diapositiva como unidad inicial; en documentos, usar secciones y relaciones; en tablas, identificar la comparación y las unidades, sin copiar celdas indiscriminadamente.
2. Decidir audiencia, alcance, tipo e idioma. Mantener términos, acrónimos, unidades, nombres y cifras. Reproducir literalmente cualquier texto que el usuario exija, sin corregirlo o traducirlo silenciosamente.
3. Dividir contenido por idea principal. Construir el brief con título, propósito, etiquetas, relaciones, composición y datos que deben conservarse. Aplicar la [guía de composición](references/composicion.md).
4. Elegir un patrón que explique la relación: proceso, comparación, evolución, capas, ciclo, mapa conceptual o jerarquía. No convertir toda explicación en tarjetas independientes.
5. Preparar el prompt en inglés, manteniendo el texto visible en español o en el idioma pedido. Incluir siempre estilo obligatorio, elementos que evitar y texto literal. Usar la [plantilla de prompt](references/prompt.md).
6. Generar mediante la capacidad disponible. Si el usuario aporta referencias visuales utilizables, extraer estética y densidad; no copiar su contenido. El plugin no incluye las imágenes de referencia originales de procedencia no documentada.
7. Ver la imagen y revisarla con la [lista de calidad](references/calidad.md): contenido, ortografía, legibilidad, densidad y estilo. Corregir o regenerar cuando aparezcan errores. Si el entorno no permite inspeccionarla, declarar esa revisión pendiente.
8. Entregar una imagen por unidad lógica y mantener una familia visual coherente. Añadir una descripción textual accesible cuando ayude. Si se pide PDF o presentación, generar primero las imágenes y después componer y verificar ese archivo con las capacidades disponibles.

## Estilo obligatorio por defecto

Fondo crema o marfil, contornos negros con irregularidad natural y rellenos muy suaves: amarillo claro, lavanda, azul cielo tenue, menta, melocotón y gris cálido. Letras grandes de aspecto manuscrito; cajas redondeadas cuando sean útiles, flechas dibujadas y pequeños iconos explicativos. Dejar suficiente espacio para que la estructura se perciba de un vistazo.

Evitar aspecto de folleto institucional, cartel corporativo, panel de indicadores, azul dominante, colores saturados, degradados, sombras brillantes, iconos de catálogo, realismo o 3D. Evitar párrafos, microtexto, tablas densas y exceso de recuadros. El tema médico, académico o jurídico no impone por sí solo una estética institucional.

Para elegir entre texto, diagrama, interacción o vídeo antes de decidir una infografía, consultar [español claro](../skill-redactar-espanol-claro/SKILL.md).
