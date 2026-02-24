import os
from openai import OpenAI


MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY")
    return OpenAI(api_key=api_key)
