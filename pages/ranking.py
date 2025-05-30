import streamlit as st
import pandas as pd
from utils.google_sheets import obtener_datos_scores

st.title("🏆 Ranking de Puntajes")

df_scores = obtener_datos_scores()

if df_scores.empty:
    st.info("No hay puntajes aún.")
else:
    # Ordenar por score descendente, luego por fecha ascendente (timestamp)
    df_scores['timestamp'] = pd.to_datetime(df_scores['timestamp'])
     # Obtener los IDs únicos de trivia
    trivia_ids = df_scores['trivia_id'].unique()

    for trivia in trivia_ids:
        st.subheader(f"📋 Ranking para Trivia: {trivia}")
        df_trivia = df_scores[df_scores['trivia_id'] == trivia].copy()

        # Ordenar por score descendente y timestamp ascendente
        df_trivia = df_trivia.sort_values(by=['score', 'timestamp'], ascending=[False, True])
        df_trivia = df_trivia.reset_index(drop=True)
        df_trivia.index += 1
        df_trivia.index.name = "Puesto"
        df_trivia['date'] = df_trivia['timestamp'].dt.strftime('%d-%m-%Y')
        # Mostrar tabla con columnas seleccionadas
        st.dataframe(df_trivia[['user', 'score', 'total', 'date']], hide_index=False)

if st.button("Volver al menú principal"):
    st.switch_page("app.py")