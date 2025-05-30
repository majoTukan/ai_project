import streamlit as st
from utils.questions import *
from utils.questions_ai import (
    load_turism_data,
    load_vehicles_data,
    generar_preguntas_turismo,
    generar_preguntas_vehiculos
)

st.set_page_config(page_title="Trivia Tukan", layout="centered")

# ---------------- Funciones auxiliares ----------------
@st.cache_data
def cargar_datos():
    """Carga y devuelve los dataframes que se usan en las trivias."""
    df_turism = load_turism_data()
    df_vehicles = load_vehicles_data()
    return df_turism, df_vehicles

def resetear_sesion_trivia():
    """Elimina todos los elementos de sesión relacionados con una trivia anterior."""
    for key in list(st.session_state.keys()):
        if key.startswith(("respuesta_", "verificada_")):
            del st.session_state[key]

    st.session_state.pregunta_actual = 0
    st.session_state.aciertos = 0
    st.session_state.resultados = []
# ------------------------------------------------------

# Carga inicial de datos
df_turism, df_vehicles = cargar_datos()

# ---------------- UI principal ----------------
st.title("🧠 Bienvenido a la Trivia Tukan")
st.subheader("Selecciona una categoría")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎒 Iniciar trivia de Turismo"):
        resetear_sesion_trivia()
        st.session_state.preguntas = generar_preguntas_turismo(df_turism, n=10)
        st.switch_page("pages/turism.py")   # asegúrate que existe

with col2:
    if st.button("🚗 Iniciar trivia de ventas de vehículos"):
        resetear_sesion_trivia()
        st.session_state.preguntas = generar_preguntas_vehiculos(df_vehicles, n=10)
        st.switch_page("pages/vehicles.py") # asegúrate que existe

# ---------------- Pie de página ----------------
st.markdown("---")
st.markdown("ℹ️ Próximamente más categorías y preguntas…")
