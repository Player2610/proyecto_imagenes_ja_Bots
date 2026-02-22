import streamlit as st
import os
st.set_page_config(layout="wide")
st.title("📂 Subir Imágenes y PDF")

nombre_producto = st.text_input("Nombre del producto")

if nombre_producto:

    ficha = st.session_state.ficha
    titulo_ficha = ficha.get("titulo", nombre_producto)
    ruta_producto = os.path.join("C:\\Users\\npc201.DESKTOP-G23MOJL\\Documents\\JOB_Projects\\PRODUCTOS", titulo_ficha)

    if not os.path.exists(ruta_producto):
        st.error("⚠️ Ese producto no tiene carpeta aún")
        st.stop()

    st.success(f"Carpeta encontrada: {ruta_producto}")

    # ✅ Revisión de imágenes en carpeta
    from PIL import Image
    imagenes_en_carpeta = [f for f in os.listdir(ruta_producto) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    st.subheader(f"Imágenes encontradas: {len(imagenes_en_carpeta)}")
    for img_name in imagenes_en_carpeta:
        img_path = os.path.join(ruta_producto, img_name)
        try:
            with Image.open(img_path) as im:
                ancho, alto = im.size
                formato = im.format
        except Exception as e:
            ancho, alto, formato = "-", "-", "Error"
        st.write(f"• {img_name} — {ancho}x{alto} px — {formato}")

    # ✅ Subir PDF
    pdf = st.file_uploader(
        "Subir hoja de datos (PDF)",
        type=["pdf"]
    )

    if st.button("Guardar archivos"):


        if pdf:
            ruta_pdf = os.path.join(ruta_producto, pdf.name)
            with open(ruta_pdf, "wb") as f:
                f.write(pdf.getbuffer())

        st.success("✅ Archivos guardados correctamente")