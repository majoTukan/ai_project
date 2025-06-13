import streamlit as st
import random
from utils.questions_ai import *
st.set_page_config(page_title="Adivina el INPC", layout="centered")


MAX_INTENTOS = 6  # Limite máximo de intentos permitidos
TOLERANCIA = 0.4  # Tolerancia para considerar respuesta correcta (±0.1)

# Asegúrate de que 'preguntas' ya esté en session_state
if "data" not in st.session_state:
    st.error("No se encontraron datos en la sesión.")
    # st.stop()  # Esto evita que el resto del código corra si no hay datos
# Ahora sí inicializa solo si no existen
# if "categoria_actual" not in st.session_state or "respuesta_real" not in st.session_state:
x, y = st.session_state.data

# Usa 'preguntas' como necesites
# x, y = generar_data_adivina_inpc(data)
# st.write("X:", x)
# st.write("Y:", y)

@st.cache_data
def generar_imagen_categoria(categoria):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=f"An illustration representing propuct(s) of the category: {categoria}. Flat style.",
        size="512x512",
        quality="standard",
        n=1
    )
    return response.data[0].url
    # Selección aleatoria de una categoría
if "categoria_actual" not in st.session_state or "respuesta_real" not in st.session_state:
    st.session_state.categoria_actual = random.choice(list(y.keys()))
    st.session_state.respuesta_real = round(y[st.session_state.categoria_actual], 2)
    st.session_state.intentos = []
    st.session_state.guess = 100.00
    st.session_state.imagen_url = generar_imagen_categoria(st.session_state.categoria_actual)

categoria = st.session_state.categoria_actual
respuesta = st.session_state.respuesta_real

st.subheader("🛒 Adivina el INPC")
st.markdown(f"# **{categoria}**")
url = generar_imagen_categoria(categoria)
st.image(url, caption=categoria, use_container_width=True)

# Inicializar el valor en la sesión si no existe
if "guess" not in st.session_state:
    st.session_state.guess = 100.00  # o cualquier valor inicial que prefieras

# Mostrar un input numérico para que el usuario pueda escribir el valor
st.session_state.guess = st.number_input(
    "Ingrese el valor:", 
    value=st.session_state.guess, 
    min_value=0.0, 
    max_value=999.99, 
    step=0.01, 
    format="%.2f"
)


# Crear columnas para botones
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("➕ Unidad"):
        st.session_state.guess += 1

with col2:
    if st.button("➖ Unidad"):
        st.session_state.guess -= 1

with col4:
    if st.button("➕ Decimal"):
        st.session_state.guess += 0.01

with col5:
    if st.button("➖ Decimal"):
        st.session_state.guess -= 0.01

# Clamp (para evitar que se salga de rango)
st.session_state.guess = round(min(max(st.session_state.guess, 0), 999.99), 2)
    # Mostrar valor actual
st.markdown(
    f"<h1 style='text-align: center; color: #4CAF50;'>Tu respuesta: {st.session_state.guess:.2f}</h1>",
    unsafe_allow_html=True
)
# Usas el valor como normalmente lo harías
guess = st.session_state.guess


# Estilo del botón
st.markdown("""
    <style>
    div.stButton > button {
        width: 200px;      /* ancho del botón */
        height: 60px;      /* alto del botón */
        font-size: 24px;   /* tamaño del texto */
        display: block;
        margin: 0 auto;    /* para centrar */
    }
    </style>
    """, unsafe_allow_html=True)
if st.button("Adivinar"):
    guess = round(st.session_state.guess, 2)

    if len(st.session_state.intentos) >= MAX_INTENTOS:
        st.error(f"Has alcanzado el número máximo de intentos ({MAX_INTENTOS}). Por favor, reinicia el juego.")
    else:
        st.session_state.intentos.append(guess)

        # Comparar con tolerancia
        if abs(guess - respuesta) <= TOLERANCIA:
            st.success(f"¡Correcto! 🎉 El valor del INPC para {categoria} es {respuesta}")
            st.balloons()
        else:
            diferencia = guess - respuesta
            if diferencia < 0:
                st.warning("El valor es **más alto** 📈")
            else:
                st.warning("El valor es **más bajo** 📉")

            # Pista extra
            if abs(diferencia) <= 5:
                st.info("Estás cerca, ajusta un poco más tu respuesta.")
            elif abs(diferencia) > 10:
                st.info("Estás bastante lejos, intenta un cambio más grande.")


if len(st.session_state.intentos) >= MAX_INTENTOS:
    st.info(f"🧠 El valor correcto del INPC para **{categoria}** era **{respuesta:.2f}**.")


if len(st.session_state.intentos) >= MAX_INTENTOS or (len(st.session_state.intentos) > 0 and abs(st.session_state.intentos[-1] - respuesta) <= TOLERANCIA):
    # Mostrar botón para reiniciar solo si ganó o agotó intentos
    if st.button("Jugar otra vez"):
        for key in ["categoria_actual", "respuesta_real", "intentos", "guess", "imagen_url"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if st.session_state.intentos:
    st.markdown(f"#### Intentos ({len(st.session_state.intentos)}/{MAX_INTENTOS}):")
    for i, val in enumerate(st.session_state.intentos, 1):
        st.write(f"{i}. {val:.2f}")