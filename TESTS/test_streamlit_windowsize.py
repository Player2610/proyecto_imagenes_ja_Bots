import streamlit as st

def campo(label, valor, altura):
    st.write(label)
    st.text_area(label, valor, height=altura, key=label)

campo("Corto", "Texto corto", 100)
campo("Largo", "Texto largo\n" * 20, 400)