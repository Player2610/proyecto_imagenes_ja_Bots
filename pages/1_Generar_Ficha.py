import streamlit as st
import json
from openai_client import generar_ficha_producto
st.set_page_config(page_title="Generador SEO", layout="wide")

st.write("APP INICIADA")

st.title("🚀 Generador de Fichas SEO")

nombre_producto = st.text_input("Nombre del producto")

# 👉 SOLO ejecutar cuando se presiona el botón
if st.button("Generar ficha"):

    if nombre_producto:

        with st.spinner("Generando contenido..."):
            texto = generar_ficha_producto(nombre_producto)

        try:
            ficha = json.loads(texto)
        except json.JSONDecodeError:
            st.error("La IA no devolvió JSON válido 😢")
            st.text(texto)
            st.stop()

        st.success("✅ Ficha generada")

        def campo(label, valor, altura=120):
            st.write(f"**{label}**")
            st.text_area(
                label,
                valor,
                height=altura,
                key=label
            )
            boton_copiar(valor)
            st.write("---")

        def boton_copiar(texto):
            texto_json = json.dumps(texto)

            st.markdown(
                f"""
                <button onclick='navigator.clipboard.writeText({texto_json})'>
                    📋 Copiar
                </button>
                """,
                unsafe_allow_html=True
            )

        campo("Título", ficha["titulo"])
        campo("Frase clave", ficha["frase_clave"])
        campo("Título SEO", ficha["titulo_seo"])
        campo("Meta descripción", ficha["meta_descripcion"])
        campo("Descripción corta", ficha["descripcion_corta"])
        campo("Descripción larga", ficha["descripcion_larga"], 500)

        campo("Etiquetas", ", ".join(ficha["etiquetas"]))
        campo("Categorías", ", ".join(ficha["categorias"]))

    else:
        st.warning("⚠️ Ingresa un nombre de producto")