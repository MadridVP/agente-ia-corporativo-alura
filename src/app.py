"""
Paso 6 del pipeline RAG: interfaz de chat simple y funcional en Streamlit.
"""

import streamlit as st
from generate import responder

st.set_page_config(page_title="BimBam Buy - Asistente Virtual", page_icon="🛍️")

st.title("🛍️ BimBam Buy - Asistente Virtual")
st.caption(
    "⚠️ Estás conversando con un agente de IA, no con una persona. "
    "Responde solo con base en los documentos internos de la empresa."
)

if "historial" not in st.session_state:
    st.session_state.historial = []

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])
        if mensaje.get("fuentes"):
            fuentes_texto = ", ".join(
                f"{f['archivo']} (pág. {f['pagina']})" for f in mensaje["fuentes"]
            )
            st.caption(f"📄 Fuentes: {fuentes_texto}")

pregunta = st.chat_input("Escribe tu pregunta sobre políticas, envíos, devoluciones...")

if pregunta:
    st.session_state.historial.append({"rol": "user", "contenido": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            resultado = responder(pregunta)
        st.markdown(resultado["respuesta"])

        if resultado["fuentes"]:
            fuentes_texto = ", ".join(
                f"{f['archivo']} (pág. {f['pagina']})" for f in resultado["fuentes"]
            )
            st.caption(f"📄 Fuentes: {fuentes_texto}")

        col1, col2 = st.columns([1, 10])
        with col1:
            st.button("👍", key=f"up_{len(st.session_state.historial)}")
        with col2:
            st.button("👎", key=f"down_{len(st.session_state.historial)}")

    st.session_state.historial.append(
        {
            "rol": "assistant",
            "contenido": resultado["respuesta"],
            "fuentes": resultado["fuentes"],
        }
    )