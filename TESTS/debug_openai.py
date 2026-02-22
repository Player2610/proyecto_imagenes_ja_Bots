import sys
import os
import json

# Añade JOB_Projects al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from openai_client import generar_ficha_producto

producto = "Diodo TVS 33V SMD SMBJ33A"

texto = generar_ficha_producto(producto)
data = json.loads(texto)

print("\n===== RESPUESTA CRUDA =====\n")
print(texto)

print("\n===== TIPO DE DATO =====\n")
print(type(texto))
print("\n===== TIPO DESPUÉS DE JSON.LOADS =====\n")
print(type(data))