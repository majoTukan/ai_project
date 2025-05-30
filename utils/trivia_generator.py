import streamlit as st
from utils.questions import *
from utils.questions_ai import *
from utils.leaderboard import record_score, get_leaderboard
from utils.google_sheets import guardar_score_en_sheets
from utils.ui_helpers import mostrar_usuario_en_esquina

def trivia_generator(trivia_id):
    # mostrar_usuario_en_esquina()
    st.write("user:", st.session_state.get("user_name"))

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

    # ---------- PUNTAJE DINÁMICO ----------
    st.markdown(
        f"### 🏆 Puntaje: **{st.session_state.aciertos}/{len(preguntas)}** preguntas correctas"
    )
    # --------------------------------------

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

    # ---------- control de estado ----------
    if f"verificada_{idx}" not in st.session_state:
        st.session_state[f"verificada_{idx}"] = False
    if f"respuesta_{idx}" not in st.session_state:
        st.session_state[f"respuesta_{idx}"] = None
    # Inicializa contador de aciertos si no existe aún
    if "aciertos" not in st.session_state:
        st.session_state.aciertos = 0

    # ---------------------------------------


    # Radio button siempre visible pero deshabilitado si ya fue verificada
    respuesta = st.radio(
        "Selecciona tu respuesta:",
        opciones,
        key=f"radio_{idx}",
        index=opciones.index(st.session_state[f"respuesta_{idx}"]) if st.session_state[f"respuesta_{idx}"] in opciones else 0,
        disabled=st.session_state[f"verificada_{idx}"]
    )
    # st.session_state[f"respuesta_{idx}"] = respuesta

    # Botón Verificar (solo si no se ha verificado ya)
    if not st.session_state[f"verificada_{idx}"]:
        if st.button("Verificar", key=f"verificar_{idx}"):
            correcta = actual.get("correcta") or actual.get("respuesta_correcta")
            correcto = respuesta == correcta
            st.session_state[f"respuesta_{idx}"] = respuesta

            st.session_state.resultados.append({
                "pregunta": actual["pregunta"],
                "respuesta": respuesta,
                "correcta": correcta,
                "es_correcta": correcto,
                "explicacion": actual["explicacion"]
            })
            if correcto:
                st.session_state.aciertos += 1

            st.session_state[f"verificada_{idx}"] = True
            st.rerun()

    # Mostrar resultado y explicación si ya fue verificada
    if st.session_state[f"verificada_{idx}"]:
        correcta = actual.get("correcta") or actual.get("respuesta_correcta")
        correcto = st.session_state[f"respuesta_{idx}"] == correcta

        if correcto:
            st.success("✅ ¡Correcto!")
        else:
            st.error(f"❌ Incorrecto. La respuesta correcta es: {correcta}")

        st.markdown(f"📘 **Explicación:** {actual['explicacion']}")

        # Mostrar botón para avanzar
        if idx < len(preguntas) - 1:
            if st.button("Siguiente pregunta", key=f"siguiente_{idx}"):
                st.session_state.pregunta_actual += 1
                st.rerun()
        else:
            st.success("🎉 ¡Has completado la trivia!")
            # st.info(f"Obtuviste {st.session_state.aciertos} de {len(preguntas)} respuestas correctas.")
            # ② Guarda el score una única vez (si no lo has guardado aún)
            if "score_guardado" not in st.session_state:
                guardar_score_en_sheets(
                    user_name = st.session_state.user_name,   # nombre del jugador
                    trivia_id = trivia_id,                    # o "vehiculos"
                    score     = st.session_state.aciertos,
                    total     = len(preguntas)
                )
                st.session_state.score_guardado = True       # marca que ya se guardó
            if st.button("Volver al menú principal"):
                st.session_state.aciertos = 0
                st.switch_page("app.py")
