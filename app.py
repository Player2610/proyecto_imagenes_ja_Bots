
import streamlit as st
from modules.generar_ficha import vista_generar_ficha
from modules.subir_archivos import vista_subir_archivos


st.set_page_config(page_title="Generador SEO", layout="wide")

# ---------------- ESTADO ----------------
if "paso" not in st.session_state:
    st.session_state.paso = 1

if "ficha" not in st.session_state:
    st.session_state.ficha = None

if "producto" not in st.session_state:
    st.session_state.producto = ""

# ---------------- TITULO ----------------
st.title("🛠 Generador de Productos")


# =====================================================
# PASO 1 — GENERAR FICHA
# =====================================================
if st.session_state.paso == 1:
    vista_generar_ficha()

# =====================================================
# PASO 2 — SUBIR ARCHIVOS
# =====================================================
elif st.session_state.paso == 2:
    vista_subir_archivos()