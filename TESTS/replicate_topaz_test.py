import requests
import time
import os

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

headers = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}

# 1. Crear la predicción
response = requests.post(
    "https://api.replicate.com/v1/predictions",
    headers=headers,
    json={
        "version": "f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
        "input": {
            "image": "https://url-de-tu-imagen.jpg",
            "scale": 4
        }
    }
)

# DEBUG
print("Status code:", response.status_code)
print("Respuesta completa:", response.json())

prediction = response.json()

if "id" not in prediction:
    print("❌ Error al crear predicción:", prediction)
    exit()

prediction_id = prediction["id"]
print("✅ Predicción creada, ID:", prediction_id)

# 2. Esperar resultado
while True:
    result = requests.get(
        f"https://api.replicate.com/v1/predictions/{prediction_id}",
        headers=headers
    ).json()

    print("Estado actual:", result.get("status"))

    if result["status"] == "succeeded":
        print("✅ Imagen mejorada:", result["output"])
        break
    elif result["status"] == "failed":
        print("❌ Error:", result.get("error"))
        break

    time.sleep(2)