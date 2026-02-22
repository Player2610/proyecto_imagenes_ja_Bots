from openai import OpenAI
from prompts import PROMPT_FICHA

client = OpenAI()

def generar_ficha_producto(nombre_producto):

    if not nombre_producto:
        raise ValueError("El nombre del producto está vacío")

    response = client.chat.completions.create(
        model="gpt-5.2",  # gpt-5.2 no existe
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