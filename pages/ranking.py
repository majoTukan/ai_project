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
    df_scores = df_scores.sort_values(by=['score', 'timestamp'], ascending=[False, True])

    # Mostrar tabla con columnas seleccionadas
    st.dataframe(df_scores[['user', 'trivia_id', 'score', 'total', 'timestamp']])
