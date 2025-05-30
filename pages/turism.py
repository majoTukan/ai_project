# Importamos las bibliotecas necesarias
import streamlit as st
from utils.questions import *
from utils.questions_ai import *

# Configura la página
st.set_page_config(page_title="Trivia de Turismo", layout="centered")

# Verifica que se hayan cargado las preguntas correctamente desde app.py
if "preguntas" not in st.session_state or "pregunta_actual" not in st.session_state:
    st.error("⚠️ Primero inicia la trivia desde el menú de inicio.")
    st.stop()

# Inicializamos resultados si no existen aún
if "resultados" not in st.session_state:
    st.session_state.resultados = []

# Cargamos preguntas e índice actual
preguntas = st.session_state.preguntas
idx = st.session_state.pregunta_actual
actual = preguntas[idx]

# Asegura que tenga tipo definido (por compatibilidad con preguntas viejas)
tipo = actual.get("tipo", "opcion_multiple")

# Título de pregunta
st.subheader(f"Pregunta {idx + 1} de {len(preguntas)}")
st.markdown(f"**{actual['pregunta']}**")


# Mostrar opciones según el tipo
if tipo == "opcion_multiple":
    opciones = actual["opciones"]
elif tipo == "verdadero_falso":
    opciones = ["Verdadero", "Falso"]
else:
    st.error("Tipo de pregunta no soportado.")
    st.stop()

respuesta = st.radio("Selecciona tu respuesta:", opciones, key=f"radio_{idx}")
# Verificación controlada por estado
if f"verificada_{idx}" not in st.session_state:
    st.session_state[f"verificada_{idx}"] = False

# Botón verificar respuesta
if st.button("Verificar", key=f"verificar_{idx}") and not st.session_state[f"verificada_{idx}"]:
    correcta = actual.get("correcta") or actual.get("respuesta_correcta")
    correcto = respuesta == correcta

    st.session_state.resultados.append({
        "pregunta": actual["pregunta"],
        "respuesta": respuesta,
        "correcta": correcta,
        "es_correcta": correcto,
        "explicacion": actual["explicacion"]
    })

    st.session_state[f"verificada_{idx}"] = True

    if correcto:
        st.success("✅ ¡Correcto!")
    else:
        st.error(f"❌ Incorrecto. La respuesta correcta es: {correcta}")

    st.markdown(f"📘 **Explicación:** {actual['explicacion']}")

# Mostrar botón para avanzar si ya se verificó
if st.session_state[f"verificada_{idx}"]:
    if idx < len(preguntas) - 1:
        if st.button("Siguiente pregunta", key=f"siguiente_{idx}"):
            st.session_state.pregunta_actual += 1
            st.rerun()
    else:
        st.success("🎉 ¡Has completado la trivia!")
        if st.button("Volver al menú principal"):
            st.switch_page("app.py")
