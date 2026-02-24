from prompts import PROMPT_FICHA
from config import MODEL, get_openai_client

def generar_ficha_producto(nombre_producto):

    if not nombre_producto:
        raise ValueError("El nombre del producto está vacío")

    client = get_openai_client()

    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": f"""
{PROMPT_FICHA}

Devuelve EXCLUSIVAMENTE JSON válido.

Producto: {nombre_producto}
"""
            }
        ]
    )

    return response.choices[0].message.content  # así se obtiene el texto
