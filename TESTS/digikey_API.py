import requests
import os
import json

CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID")
CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET")

# Obtener token
token_resp = requests.post(
    "https://api.digikey.com/v1/oauth2/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
)
access_token = token_resp.json()["access_token"]

# Buscar Arduino - POST con body JSON
resp = requests.post(
    "https://api.digikey.com/products/v4/search/keyword",
    headers={
        "Authorization": f"Bearer {access_token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "X-DIGIKEY-Locale-Site": "US",
        "X-DIGIKEY-Locale-Language": "en",
        "X-DIGIKEY-Locale-Currency": "USD",
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    data=json.dumps({
        "Keywords": "mpu6050",
        "Limit": 5
    })
)

data = resp.json()

print(f"Total productos encontrados: {data['ProductsCount']}\n")

for product in data['Products']:
    print(f"Nombre:        {product['Description']['ProductDescription']}")
    print(f"Fabricante:    {product['Manufacturer']['Name']}")
    print(f"Part Number:   {product['ManufacturerProductNumber']}")
    print(f"DigiKey PN:    {product['ProductVariations'][0]['DigiKeyProductNumber']}")
    print(f"Precio:        {product['ProductVariations'][0]['StandardPricing'][0]['UnitPrice']} USD")
    print(f"Stock:         {product['QuantityAvailable']}")
    print(f"URL:           {product['ProductUrl']}")
    print("-" * 60)