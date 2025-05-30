import streamlit as st
from utils.questions import *
from utils.questions_ai import *


st.set_page_config(page_title="Trivia Tukan", layout="centered")

# Título de la app
st.title("🧠 Bienvenido a la Trivia Tukan")

# Menú principal con opciones (solo una por ahora)
st.subheader("Selecciona una categoría")
# Menú principal
# menu = st.sidebar.selectbox("Menú", ["Inicio", "Trivia de Turismo"])
@st.cache_data
def cargar_datos():
    return load_data()

# Cargamos los datos turísticos
df = cargar_datos()
# Cuando el usuario da clic en el botón, iniciamos la trivia
if st.button("🎒 Iniciar Trivia de Turismo"):
    # Generamos las preguntas AI y las almacenamos en la sesión
    preguntas = generar_preguntas(df, n=10)

    # Inicializamos los estados que necesitaremos
    st.session_state.preguntas = preguntas  # Lista de preguntas
    st.session_state.pregunta_actual = 0    # Índice de la pregunta actual
    st.session_state.resultados = []        # Para almacenar respuestas del usuario

    # Redirigimos a la página de preguntas
    st.switch_page("pages/turism.py")  # Asegúrate de que este archivo esté en /pages

# Pie de página o mensaje adicional
st.markdown("---")
st.markdown("ℹ️ Próximamente más categorías y preguntas...")

