# Generador de Productos (Streamlit)

App en Streamlit para generar fichas SEO (JSON) y gestionar imagenes/PDF por producto.

## Requisitos

- Python 3.10+

## Instalacion

```bash
python -m venv .venv
```

Activar el entorno:

- Windows (PowerShell):
  ```powershell
  .\\.venv\\Scripts\\Activate.ps1
  ```
- Windows (cmd):
  ```bat
  .\\.venv\\Scripts\\activate.bat
  ```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Variables de entorno

- `OPENAI_API_KEY`: API key para OpenAI
- `NGROK_AUTHTOKEN`: token de ngrok (solo si vas a exponer la app)

Ejemplo (PowerShell):

```powershell
$env:OPENAI_API_KEY = "..."
$env:NGROK_AUTHTOKEN = "..."
```

## Ejecutar

```bash
streamlit run app.py
```

La app usa el puerto configurado en `.streamlit/config.toml`.

## Exponer con ngrok

En otra terminal:

```bash
python ngrok_deply.py
```

Esto imprime la URL publica. Cualquier archivo subido desde el navegador se guarda en el filesystem donde corre Streamlit.
