import streamlit as st
from utils.questions import *
from utils.questions_ai import (
    load_turism_data,
    load_vehicles_data,
    load_inpc_data,
    generar_preguntas_turismo,
    generar_preguntas_vehiculos,
    generar_preguntas_inpc,
    generar_data_adivina_inpc,
)
from utils.google_sheets import guardar_usuario_en_sheets

st.set_page_config(page_title="Trivia Tukan", layout="centered")
hide_pages_nav = """
    <style>
        section[data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_pages_nav, unsafe_allow_html=True)
# ---------------- Funciones auxiliares ----------------
@st.cache_data
def cargar_datos():
    """Carga y devuelve los dataframes que se usan en las trivias."""
    df_turism = load_turism_data()
    df_vehicles = load_vehicles_data()
    df_inpc = load_inpc_data()
  # Carga datos para adivinar INPC
    return df_turism, df_vehicles, df_inpc

def resetear_sesion_trivia():
    """Elimina todos los elementos de sesión relacionados con una trivia anterior."""
    for key in list(st.session_state.keys()):
        if key.startswith(("respuesta_", "verificada_")):
            del st.session_state[key]

    st.session_state.pregunta_actual = 0
    st.session_state.aciertos = 0
    st.session_state.resultados = []
# ------------------------------------------------------

if "user_name" not in st.session_state:
    st.session_state.user_name = None
# Mostrar siempre el título
st.title("🧠 Bienvenido a la Trivia Tukan")

if st.session_state.user_name is None:
    with st.form("form_user_name", clear_on_submit=False):
        user_name_input = st.text_input("Por favor, ingresa tu nombre para comenzar:")
        submitted = st.form_submit_button("Confirmar nombre")

        if submitted and user_name_input:
            st.session_state.user_name = user_name_input
            guardar_usuario_en_sheets(st.session_state.user_name)
        # st.experimental_rerun()

else:
    # Carga inicial de datos
    df_turism, df_vehicles, df_inpc = cargar_datos()

    # ---------------- UI principal ----------------
    st.subheader(f"Selecciona una trivia, {st.session_state.user_name}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎒 Trivia de Turismo"):
            resetear_sesion_trivia()
            st.session_state.preguntas = generar_preguntas_turismo(df_turism, n=10)
            st.switch_page("pages/turism.py")   # asegúrate que existe

    with col2:
        if st.button("🚗 Trivia de ventas de vehículos"):
            resetear_sesion_trivia()
            st.session_state.preguntas = generar_preguntas_vehiculos(df_vehicles, n=10)
            st.switch_page("pages/vehicles.py") # asegúrate que existe

    with col3:
        if st.button("🛒📈 Trivia de INPC"):
            resetear_sesion_trivia()
            st.session_state.preguntas = generar_preguntas_inpc(df_inpc, n=10)
            st.switch_page("pages/inpc.py") # asegúrate que existe

    with col1:
        if st.button("🛒 Adivina el INPC"):
            resetear_sesion_trivia()
            st.session_state.data = generar_data_adivina_inpc(df_inpc)
            st.switch_page("pages/guess_inpc.py")   # asegúrate que existe
    # ---------------- Pie de página ----------------
    st.markdown("---")
    # st.markdown("Ver ranking de puntajes")
    if st.button("🏆 Ver ranking de puntajes"):
            st.switch_page("pages/ranking.py") # 
    # ---------------- Pie de página ----------------
    st.markdown("---")
    st.markdown("ℹ️ Próximamente más categorías y preguntas…")
