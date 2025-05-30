# import pandas as pd
# import random
# import os
# import streamlit as st  



# @st.cache_data
# def load_data():
#     token = os.getenv('API_TUKAN')
#     df = pd.read_csv(f"https://client.tukanmx.com/visualizations/retrieve_query_csv/en/5079bf2a-58d0-4632-b02f-1c25c6c2130b/{token}", delimiter='|')
#     df["date"] = pd.to_datetime(df["date"], errors="coerce")  
#     # Eliminar columnas que terminan en '__ref'
#     df = df[[col for col in df.columns if not col.endswith("__ref")]]
#     if df["date"].isnull().any():
#         st.warning("⚠️ Algunas fechas no se pudieron convertir. Revisa el archivo CSV.")
#     return df



# def generar_pregunta_llegadas(df):
#     df_2023 = df[df["date"].dt.year == 2023]
#     resumen = df_2023.groupby("geography")["Number of tourists (sum)."].sum().sort_values(ascending=False)
    
#     top_4 = resumen.head(4)
#     correcta = top_4.idxmax()
#     opciones = top_4.sample(frac=1, random_state=random.randint(1, 9999)).index.tolist()

#     pregunta = "¿Qué nacionalidad tuvo más llegadas de turistas por aire a México en 2023?"
#     return pregunta, opciones, correcta


# def pregunta_anio_top_para_nacionalidad(df):
#     df = df.copy()
#     df["date"] = pd.to_datetime(df["date"])
#     nacionalidades = df["geography"].unique()
#     nacionalidad = random.choice(nacionalidades)
#     df_filtrado = df[df["geography"] == nacionalidad]
#     resumen = df_filtrado.groupby(df_filtrado["date"].dt.year)["Number of tourists (sum)."].sum()
#     if resumen.empty: return None
#     correcta = resumen.idxmax()
#     opciones = random.sample(list(resumen.index), min(3, len(resumen)))
#     if correcta not in opciones:
#         opciones[random.randint(0, len(opciones) - 1)] = correcta
#     random.shuffle(opciones)
#     pregunta = f"¿En qué año hubo más turistas de {nacionalidad}?"
#     return pregunta, opciones, correcta