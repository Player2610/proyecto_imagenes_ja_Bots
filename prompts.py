PROMPT_FICHA = """
Necesito que redactes una ficha de producto optimizada para SEO siguiendo este formato exacto:
Devuelve la respuesta EXCLUSIVAMENTE en JSON válido.
Devuelve la respuesta EXCLUSIVAMENTE en formato JSON válido.

Usa EXACTAMENTE estas claves (sin tildes ni espacios):

{
  "titulo": "",
  "frase_clave": "",
  "titulo_seo": "",
  "meta_descripcion": "",
  "descripcion_corta": "",
  "descripcion_larga": "",
  "nombre_imagen": "",
  "etiquetas": [],
  "categorias": []
}
No incluyas texto adicional.
No uses Markdown.

Formato requerido:

Título: nombre del producto, modificado para que sea conciso, técnico, llamativo y no demasiado largo. No añadir aclaraciones tipo “para electrónica” o “para robótica”

Frase clave objetivo: palabra o frase clave principal del producto (ej. “Amplificador Operacional INA128P”).

Título SEO | utilidad del producto: máximo 65 caracteres, incluir la frase clave objetivo, exactamente con el formato “|” entre ambos elementos.

Meta descripción: 150–160 caracteres, incluir la frase clave objetivo, no usar palabras como “compra” o “mira”.

Descripción corta: máximo 3 líneas, clara y persuasiva, incluir la frase clave objetivo.

Descripción larga: explicación completa del producto, sus ventajas y usos, mínimo 300 palabras, incluir la frase clave objetivo al menos 2 veces. Debe tener tono técnico, profesional y enfocado a proyectos de electrónica, robótica o ingeniería.

Nombre de imagen: el nombre del archivo de imagen principal del producto, optimazado para seo (ej. amplificador-operacional-ina128p.jpg), sin espacios, con guiones, sin mayúsculas, y con extensión .jpg.
Instrucciones adicionales:

• Funciones destacadas del “frase clave objetivo”: lista en viñetas con funciones y beneficios técnicos.

• Aplicaciones comunes: lista en viñetas con usos típicos del producto.

• Características técnicas: lista en viñetas con especificaciones técnicas exactas del producto.

• Hoja de datos: indicar “Hoja de datos disponible” o “—-No aplica—-” según corresponda.

• Para más (categoría del producto), consulte la sección (poner la categoría adecuada en negrilla (ej. Optoacopladores y Aisladores Electrónicos)).

• Usar bastantes palabras de transición

• Usa voz activa todo el tiempo

• Cada sección debe estar claramente diferenciada con títulos en negrita.

• Usar tono técnico, claro, profesional y persuasivo, apto para ecommerce.

• Optimizar para SEO incluyendo la frase clave objetivo en las secciones relevantes.

• Mantener coherencia y profesionalismo en la redacción.

• Redactaras: DATASHEET: {nombre del producto}

• El título no tiene que llevar nombre de fabricante, solo datos técnicos útiles, pero no tan largo

• En caso de que el producto sea un paquete, el título debe especificarlo al final con "Paquete X10, X5, etc"

REGLAS OBLIGATORIAS:

0. Si consideras que la informacion o el titulo estan mal, incoherentes o no tienen sentido, corrige el error y redacta un titulo o especificaciones coherentes con el producto, pero sin inventar datos técnicos.
1. NO inventes características técnicas.
2. NO completes especificaciones desconocidas.
3. Si un dato técnico no es seguro o verificable → OMITIRLO.
4. NO uses "No aplica", "N/A", "---", ni placeholders.
5. SOLO incluir especificaciones que correspondan al tipo de producto.

6. Detectar automáticamente el tipo de producto:

- Si es un diodo / TVS / LED / transistor / pasivo:
  → Incluir únicamente parámetros eléctricos relevantes
  (voltaje, potencia, encapsulado, tipo, tolerancia si aplica)

- Si es módulo o placa:
  → Incluir pines, interfaces, alimentación, etc.

7. NO incluir secciones absurdas o incompatibles.
   Ejemplo: microcontrolador en un diodo TVS → PROHIBIDO.

8. La sección "Características técnicas" debe contener SOLO datos reales y coherentes con el componente.

9. Si hay pocos datos técnicos confiables:
   → Mostrar solo los esenciales.
10. Busca por internet para verificar datos técnicos si es necesario, pero SOLO si puedes confirmar su veracidad.
"""