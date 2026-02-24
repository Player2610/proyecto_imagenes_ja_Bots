import json
import os
from openai_client import generar_ficha_producto
import streamlit as st

def vista_generar_ficha():
    st.header("Paso 1️⃣ — Generar ficha SEO")

    nombre_producto = st.text_input(
        "Nombre del producto",
        value=st.session_state.producto
    )

    if st.button("🚀 Generar ficha"):
        if nombre_producto:
            with st.spinner("Generando contenido..."):
                try:
                    texto = generar_ficha_producto(nombre_producto)
                except Exception as e:
                    st.error(str(e))
                    st.stop()
            try:
                ficha = json.loads(texto)
            except json.JSONDecodeError:
                st.error("La IA no devolvió JSON válido 😢")
                st.text(texto)
                st.stop()
            st.session_state.ficha = ficha
            st.session_state.producto = nombre_producto
            # Usar el título de la ficha como nombre de la carpeta
            titulo_ficha = ficha.get("titulo", nombre_producto)
            ruta = os.path.join("PRODUCTOS", titulo_ficha)
            os.makedirs(ruta, exist_ok=True)
            st.success("✅ Ficha generada + carpeta creada")

    if st.session_state.ficha:
        ficha = st.session_state.ficha
        st.subheader("Vista previa")

        def boton_copiar(texto):
            texto_json = json.dumps(texto)
            st.markdown(
                f"""
                <button onclick='navigator.clipboard.writeText({json.dumps(texto_json)})'>
                    📋 Copiar
                </button>
                """,
                unsafe_allow_html=True
            )

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

        campo("Título", ficha["titulo"])
        campo("Frase clave", ficha["frase_clave"])
        campo("Título SEO", ficha["titulo_seo"])
        campo("Meta descripción", ficha["meta_descripcion"])
        campo("Descripción corta", ficha["descripcion_corta"])
        campo("Descripción larga", ficha["descripcion_larga"], 500)
        campo("Etiquetas", ", ".join(ficha["etiquetas"]))
        campo("Categorías", ", ".join(ficha["categorias"]))

        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button("➡ Siguiente"):
                st.session_state.paso = 2
                st.rerun()
