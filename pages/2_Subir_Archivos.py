import streamlit as st
import os
import json
import base64
import mimetypes
import html

from modules.image_logic import (
    build_images_zip,
    convert_bytes_to_jpg,
    is_low_resolution,
    new_image_name,
    safe_zip_folder_name,
)

from modules.enhance_api import EnhanceError, enhance_quality_replicate
 

def _data_uri(file_name: str, data: bytes) -> str:
    mime, _ = mimetypes.guess_type(file_name)
    if not mime:
        mime = "application/octet-stream"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _human_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    if num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    return f"{num_bytes / (1024 * 1024 * 1024):.1f} GB"


st.set_page_config(layout="wide")
st.title("📷 Subir Imagenes")

st.markdown(
    """
<style>
  .pasarela-wrap {border: 2px solid rgba(0,0,0,0.15); border-radius: 16px; padding: 18px; background: rgba(255,255,255,0.75);} 
  .pasarela-frame {border: 2px solid rgba(0,0,0,0.25); border-radius: 16px; background: #fff; height: 58vh; display: flex; align-items: center; justify-content: center; overflow: hidden;}
  /* No scrolls: only downscale when larger than the frame */
  .pasarela-frame img {display: block; width: auto; height: auto; max-width: 100%; max-height: 100%;}
  .pasarela-meta {margin-top: 10px; font-size: 0.95rem; opacity: 0.9;}
  .pasarela-cta {margin-top: 14px;}
  .danger-btn div[data-testid="stButton"] > button {background: #c0392b; border-color: #c0392b; color: #fff;}
  .danger-btn div[data-testid="stButton"] > button:hover {background: #a93226; border-color: #a93226; color: #fff;}
</style>
""",
    unsafe_allow_html=True,
)

nombre_producto = st.text_input("Nombre del producto (nombre de carpeta/zip)")

if nombre_producto:
    st.subheader("Subir imagenes")
    images = st.file_uploader(
        "Subir imágenes (varias)",
        type=["png", "jpg", "jpeg", "webp", "avif"],
        accept_multiple_files=True,
        key="up_images",
    )

    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 1
    if "last_action" not in st.session_state:
        st.session_state.last_action = ""
    if "enhanced" not in st.session_state:
        st.session_state.enhanced = {}

    # Reset index if the set of images changes
    image_sig = []
    if images:
        for up in images:
            image_sig.append((getattr(up, "name", ""), int(getattr(up, "size", 0))))
    image_sig = tuple(image_sig)
    image_count = len(images) if images else 0
    if st.session_state.get("_last_image_sig") != image_sig:
        st.session_state._last_image_sig = image_sig
        st.session_state.carousel_idx = 1

    st.subheader("Pasarela de imagenes")
    if not images:
        st.info("Sube al menos una imagen para ver la pasarela.")
    else:
        idx = int(st.session_state.carousel_idx)
        up = images[idx - 1]

        up.seek(0)
        img_bytes = up.getbuffer().tobytes()
        img_name = getattr(up, "name", "imagen")
        img_name_html = html.escape(img_name, quote=True)
        img_size = _human_size(int(getattr(up, "size", len(img_bytes))))

        new_name = new_image_name(nombre_producto, idx, ext=".jpg")
        new_name_html = html.escape(new_name, quote=True)

        converted_err = ""
        try:
            jpg_bytes, w_i, h_i = convert_bytes_to_jpg(img_bytes)
            original_jpg_bytes = jpg_bytes
            display_bytes = st.session_state.enhanced.get(idx, original_jpg_bytes)
            w, h, fmt = str(w_i), str(h_i), "JPG"
        except Exception as e:
            converted_err = str(e)
            original_jpg_bytes = b""
            display_bytes = img_bytes
            w, h, fmt = "-", "-", "Error"

        low_res = False
        try:
            low_res = is_low_resolution(int(w), int(h), min_px=500)
        except Exception:
            low_res = False

        st.markdown('<div class="pasarela-wrap">', unsafe_allow_html=True)

        # Image frame (no scroll; downscale only if larger)
        uri = _data_uri(new_name, display_bytes)
        st.markdown(
            f"""
<div class="pasarela-frame">
  <img src="{uri}" alt="{new_name_html}" />
</div>
<div class="pasarela-meta">
  <div><b>{new_name_html}</b></div>
  <div>Original: {img_name_html}</div>
  <div>Autoajuste: solo reduce si excede el recuadro | #{idx}/{image_count} | {w}x{h} | {fmt} | {img_size}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if converted_err:
            st.error(f"No pude convertir esta imagen a JPG: {converted_err}")

        st.markdown('<div class="pasarela-cta">', unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("Corregir miniatura", use_container_width=True):
                st.session_state.last_action = "Corregir miniatura"
        with b2:
            if low_res:
                st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
            if st.button("Corregir escalado", use_container_width=True):
                st.session_state.last_action = "Corregir escalado"
            if low_res:
                st.markdown("</div>", unsafe_allow_html=True)
        with b3:
            if low_res:
                st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
            if st.button("Mejorar calidad (IA)", use_container_width=True, disabled=bool(converted_err)):
                api_token = os.getenv("REPLICATE_API_TOKEN", "").strip()
                model_version = os.getenv("REPLICATE_MODEL_VERSION", "").strip()
                model = os.getenv("REPLICATE_MODEL", "").strip()
                image_key = os.getenv("REPLICATE_IMAGE_KEY", "").strip() or None
                scale_key = os.getenv("REPLICATE_SCALE_KEY", "").strip() or None
                scale_value_raw = os.getenv("REPLICATE_SCALE_VALUE", "").strip()
                extra_json = os.getenv("REPLICATE_EXTRA_INPUT_JSON", "").strip()
                extra_input = None
                if extra_json:
                    try:
                        extra_input = json.loads(extra_json)
                        if not isinstance(extra_input, dict):
                            st.error("REPLICATE_EXTRA_INPUT_JSON debe ser un JSON objeto")
                            extra_input = None
                    except Exception as e:
                        st.error(f"REPLICATE_EXTRA_INPUT_JSON invalido: {e}")
                        extra_input = None

                # Backwards compatibility: allow owner/name in REPLICATE_MODEL_VERSION
                if (not model) and ("/" in model_version) and (":" not in model_version):
                    model = model_version
                    model_version = ""

                with st.expander("Config Replicate", expanded=False):
                    masked = (api_token[:6] + "..." + api_token[-4:]) if api_token else ""
                    st.write(f"REPLICATE_API_TOKEN: {masked}")
                    st.write(f"REPLICATE_MODEL: {model}")
                    st.write(f"REPLICATE_MODEL_VERSION: {model_version}")
                    st.write(f"REPLICATE_IMAGE_KEY: {image_key or ''}")
                    st.write(f"REPLICATE_SCALE_KEY: {scale_key or ''}")
                    st.write(f"REPLICATE_SCALE_VALUE: {scale_value_raw}")
                    st.write(f"REPLICATE_EXTRA_INPUT_JSON: {extra_json}")

                if not api_token or (not model_version and not model):
                    st.error("Faltan variables: REPLICATE_API_TOKEN y (REPLICATE_MODEL_VERSION o REPLICATE_MODEL)")
                else:
                    scale_value = 2
                    if scale_value_raw:
                        try:
                            scale_value = json.loads(scale_value_raw)
                        except Exception:
                            scale_value = scale_value_raw

                    with st.spinner("Mejorando calidad (IA)..."):
                        try:
                            enhanced_bytes = enhance_quality_replicate(
                                jpg_bytes=original_jpg_bytes,
                                api_token=api_token,
                                model_version=model_version or None,
                                model=model or None,
                                scale=scale_value,
                                timeout_s=180,
                                image_key=image_key,
                                scale_key=scale_key,
                                extra_input=extra_input,
                            )
                            st.session_state.enhanced[idx] = enhanced_bytes
                            st.session_state.last_action = "Mejorar calidad (IA)"
                            st.rerun()
                        except EnhanceError as e:
                            st.error(str(e))
                        except Exception as e:
                            st.error(f"Error inesperado: {e}")
            if low_res:
                st.markdown("</div>", unsafe_allow_html=True)
        with b4:
            if st.button("Quitar marca de agua", use_container_width=True):
                st.session_state.last_action = "Quitar marca de agua"

        nav_prev, nav_mid, nav_next = st.columns([1, 2, 1])
        with nav_prev:
            if st.button("⬅ Anterior", use_container_width=True, disabled=idx <= 1):
                st.session_state.carousel_idx -= 1
                st.rerun()
        with nav_mid:
            st.write(f"{idx}/{image_count}")
        with nav_next:
            if st.button("Siguiente ➡", use_container_width=True, disabled=idx >= image_count):
                st.session_state.carousel_idx += 1
                st.rerun()

        if st.session_state.last_action:
            st.info(f"Accion seleccionada: {st.session_state.last_action} (pendiente de implementar)")

        if low_res:
            st.warning("Resolucion menor a 500x500 px: recomienda corregir escalado o mejorar calidad.")

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.subheader("Descarga")
    zip_name = safe_zip_folder_name(nombre_producto)
    if not images:
        st.info("Sube imagenes para habilitar el zip.")
    else:
        try:
            payload = []
            for up in images:
                up.seek(0)
                payload.append((getattr(up, "name", ""), up.getbuffer().tobytes()))

            # If there are enhanced images, replace by index.
            if st.session_state.enhanced:
                new_payload = []
                for i, (orig_name, raw) in enumerate(payload, 1):
                    if i in st.session_state.enhanced:
                        new_payload.append((orig_name, st.session_state.enhanced[i]))
                    else:
                        new_payload.append((orig_name, raw))
                payload = new_payload

            zip_bytes = build_images_zip(product_name=nombre_producto, images=payload)
            st.download_button(
                "⬇ Descargar carpeta (zip)",
                data=zip_bytes,
                file_name=f"{zip_name}.zip",
                mime="application/zip",
            )
        except Exception as e:
            st.error(f"No pude generar el zip: {e}")
