import os

from pyngrok import ngrok


def main() -> None:
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    if authtoken:
        ngrok.set_auth_token(authtoken)

    addr = os.getenv("STREAMLIT_PORT", "8502")
    url = ngrok.connect(addr)
    print(f"URL publica: {url}")
    input("Enter para cerrar...")


if __name__ == "__main__":
    main()
