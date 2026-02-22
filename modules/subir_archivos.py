import os
import io
import zipfile
from datetime import datetime
import streamlit as st

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def _human_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    if num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    return f"{num_bytes / (1024 * 1024 * 1024):.1f} GB"


def _zip_folder_bytes(folder_path: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(os.listdir(folder_path)):
            full = os.path.join(folder_path, name)
            if os.path.isfile(full):
                zf.write(full, arcname=name)
    return buf.getvalue()

def vista_subir_archivos():
    if st.button("🔄 Actualizar imágenes"):
        st.rerun()
    st.header("Paso 2️⃣ — Subir Imágenes / PDF")
    nombre_producto = st.session_state.producto
    ficha = st.session_state.ficha
    titulo_ficha = ficha.get("titulo", nombre_producto)
    # Link a Google Images
    st.markdown(f"[🔎 Buscar imágenes en Google](https://www.google.com/search?tbm=isch&q={titulo_ficha.replace(' ', '+')})", unsafe_allow_html=True)
    ruta = os.path.join("PRODUCTOS", titulo_ficha)
    if not os.path.exists(ruta):
        st.error("⚠️ Carpeta no encontrada")
        st.stop()
    st.success(f"📂 Carpeta activa: {ruta}")

    with st.expander("Ver carpeta", expanded=True):
        try:
            files = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]
        except Exception as e:
            files = []
            st.error(f"No se pudo leer la carpeta: {e}")

        st.write(f"Archivos: {len(files)}")

        if files:
            zip_bytes = _zip_folder_bytes(ruta)
            st.download_button(
                "⬇ Descargar carpeta (zip)",
                data=zip_bytes,
                file_name=f"{titulo_ficha}.zip",
                mime="application/zip",
            )

        for name in sorted(files):
            full = os.path.join(ruta, name)
            try:
                stat = os.stat(full)
                size = _human_size(int(stat.st_size))
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            except Exception:
                size = "-"
                mtime = "-"

            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{name}  ({size}, {mtime})")
            with col_b:
                try:
                    with open(full, "rb") as fh:
                        data = fh.read()
                    st.download_button(
                        "Descargar",
                        data=data,
                        file_name=name,
                        key=f"dl::{name}",
                    )
                except Exception:
                    st.write("-")

    st.subheader("Subidas")
    imagenes = st.file_uploader(
        "Subir imágenes (se guardan en la carpeta del servidor)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
    imagenes_en_carpeta = [f for f in os.listdir(ruta) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

    pdf = st.file_uploader(
        "Subir hoja de datos (PDF)",
        type=["pdf"],
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Atrás"):
            st.session_state.paso = 1
            st.rerun()
    with col2:
        if st.button("💾 Guardar archivos"):
            nombre_imagen_json = st.session_state.ficha.get("nombre_imagen", "imagen-producto.jpg")
            base, ext = os.path.splitext(nombre_imagen_json)
            ext = ext.lower() or ".jpg"

            # Guardar imágenes con nombres SEO (y convertir a JPEG si corresponde)
            if imagenes:
                for idx, up in enumerate(imagenes, 1):
                    if idx == 1:
                        out_name = f"{base}{ext}" if nombre_imagen_json else f"imagen-producto{ext}"
                    else:
                        out_name = f"{base}-{idx}{ext}" if base else f"imagen-producto-{idx}{ext}"

                    out_path = os.path.join(ruta, out_name)

                    # Si PIL no esta disponible, guardamos tal cual
                    if Image is None:
                        with open(out_path, "wb") as f:
                            f.write(up.getbuffer())
                        continue

                    assert Image is not None

                    try:
                        up.seek(0)
                        im = Image.open(up)
                        im.load()

                        if ext in (".jpg", ".jpeg"):
                            if im.mode in ("RGBA", "LA"):
                                bg = Image.new("RGB", im.size, (255, 255, 255))
                                alpha = im.split()[-1]
                                bg.paste(im.convert("RGB"), mask=alpha)
                                im = bg
                            else:
                                im = im.convert("RGB")
                            im.save(out_path, format="JPEG", quality=90, optimize=True)
                        else:
                            # Guardar en el formato indicado por la extension
                            im.save(out_path)
                    except Exception:
                        # Fallback: guardar bytes originales
                        up.seek(0)
                        with open(out_path, "wb") as f:
                            f.write(up.getbuffer())

            if pdf:
                with open(os.path.join(ruta, pdf.name), "wb") as f:
                    f.write(pdf.getbuffer())

            st.success("✅ Archivos guardados correctamente")

    # Revisión de imágenes en carpeta
    imagenes_en_carpeta = [f for f in os.listdir(ruta) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    st.subheader(f"Imágenes encontradas: {len(imagenes_en_carpeta)}")
    nombre_imagen_json = st.session_state.ficha.get("nombre_imagen", "imagen-producto.jpg")
    base, ext = os.path.splitext(nombre_imagen_json)
    cols = st.columns(len(imagenes_en_carpeta) if imagenes_en_carpeta else 1)
    for idx, img_name in enumerate(imagenes_en_carpeta, 1):
        if idx == 1:
            nuevo_nombre = nombre_imagen_json
        else:
            nuevo_nombre = f"{base}-{idx}{ext}"
        img_path = os.path.join(ruta, img_name)
        try:
            if Image is None:
                raise RuntimeError("PIL no disponible")

            assert Image is not None

            with Image.open(img_path) as im:
                ancho, alto = im.size
                formato = im.format
            # Renombrar solo si la imagen se puede abrir
            final_nombre = nuevo_nombre
            if img_name != nuevo_nombre:
                nuevo_path = os.path.join(ruta, nuevo_nombre)
                try:
                    os.rename(img_path, nuevo_path)
                    img_path = nuevo_path
                    final_nombre = nuevo_nombre
                except Exception as rename_err:
                    st.warning(f"No se pudo renombrar {img_name}: {rename_err}")
                    final_nombre = img_name
            with Image.open(img_path) as im:
                with cols[idx-1]:
                    st.image(im, caption=f"{final_nombre} ({ancho}x{alto} px, {formato})", width=300)
                    if ancho < 500 or alto < 500:
                        st.markdown(f"<span style='color:red; font-weight:bold;'>⚠️ Imagen menor a 500x500 px</span>", unsafe_allow_html=True)
        except Exception as e:
            ancho, alto, formato = "-", "-", "Error"
            with cols[idx-1]:
                st.write(f"• {nuevo_nombre} — {ancho}x{alto} px — {formato} (Error: {e})")
