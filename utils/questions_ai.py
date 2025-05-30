import pandas as pd
import random
import json

import os
import streamlit as st  # solo si estás usando Streamlit aquí
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@st.cache_data
def load_data():
    token = os.getenv('API_TUKAN')
    df = pd.read_csv(f"https://client.tukanmx.com/visualizations/retrieve_query_csv/en/5079bf2a-58d0-4632-b02f-1c25c6c2130b/{token}", delimiter='|')
    df["date"] = pd.to_datetime(df["date"], errors="coerce")  # convierte a datetime
    # Eliminar columnas que terminan en '__ref'
    df = df[[col for col in df.columns if not col.endswith("__ref")]]
    if df["date"].isnull().any():
        st.warning("⚠️ Algunas fechas no se pudieron convertir. Revisa el archivo CSV.")
    return df


def generar_pregunta_con_gpt(data, uniques, n:int = 10):
    
    
    prompt_usuario = f"""
    Actúa como un experto en turismo y educación. A partir de los siguientes datos en formato JSON sobre llegadas de turistas a México:

    {data}

    También se te comparten los valores únicos de los aeropuertos disponibles: {uniques}.
    Las claves `destination_geography` representan los estados de México.

    Tu tarea es generar {n} preguntas didácticas en formato JSON. Las preguntas deben ser **interesantes, variadas, no obvias** y fomentar el pensamiento crítico. Deben ser de tipo "opcion_multiple" o "verdadero_falso".

    Sigue estas reglas:

    1. Cubre distintos enfoques de análisis, como: diferencias por género, país de origen, estacionalidad, patrones, destinos más comunes, comparaciones entre periodos, etc.
    2. **Evita repetir temas, enfoques o respuestas**. Las preguntas no deben revelar la respuesta de otras ni apoyarse en la misma idea.
    3. No incluyas cifras o fechas específicas en la pregunta. **Pero en la explicación sí puedes incluir cifras reales** si ayudan a entender la respuesta (ej. “X turistas hombres vs Y mujeres”).
    4. Las preguntas deben ser claras, bien redactadas y no ambiguas.
    5. Las explicaciones deben ser educativas y aportar valor con cifras o contexto adicional del dato cuando sea útil.

    Formato esperado:

    [
    {{
        "tipo": "opcion_multiple" o "verdadero_falso",
        "pregunta": "...",
        "opciones": ["...", "...", "...", "..."],  # Solo dos opciones si es verdadero/falso
        "respuesta_correcta": "...",
        "explicacion": "..."  # Incluye cifras reales cuando aporten contexto educativo, sin spoilear otras preguntas
    }},
    ...
    ]

    Nota: Para preguntas de verdadero o falso, usa únicamente las opciones ["Verdadero", "Falso"].
    """


    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un generador de preguntas tipo trivia sobre turismo en México."},
            {"role": "user", "content": prompt_usuario},
        ],
        temperature=0.7
    )
    content = response.choices[0].message.content
    # Parsear la respuesta
    try:
        preguntas = json.loads(content)
        assert isinstance(preguntas, list), "El resultado no es una lista de preguntas."
        return preguntas
    except Exception as e:
        raise ValueError(f"No se pudo parsear la respuesta: {content}") from e



def resume_data(df):
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month

    resumen = {}

    # Aeropuerto con más y menos llegadas
    aeropuerto_llegadas = df.groupby('airport_iata')["Number of tourists (sum)."].sum().sort_values(ascending=False)
    resumen['aeropuerto_con_mas_llegadas'] = aeropuerto_llegadas.head(1).to_dict()
    resumen['aeropuerto_con_menos_llegadas'] = aeropuerto_llegadas[aeropuerto_llegadas > 0].tail(1).to_dict()
    resumen['top_5_aeropuertos'] = aeropuerto_llegadas.head(5).to_dict()

    # Año más visitado y crecimiento año a año
    turistas_por_anio = df.groupby('year')["Number of tourists (sum)."].sum().sort_index()
    resumen['anio_mas_visitado'] = turistas_por_anio.idxmax()
    resumen['total_turistas_por_anio'] = turistas_por_anio.to_dict()
    resumen['crecimiento_anual'] = turistas_por_anio.pct_change().round(3).fillna(0).to_dict()

    # Mes con más turistas acumulado
    mes_acumulado = df.groupby('month')["Number of tourists (sum)."].sum()
    resumen['mes_con_mas_turistas'] = mes_acumulado.idxmax()

    # Estado más visitado por año y top 5 acumulado
    estado_anual = df.groupby(['year', 'destination_geography'])["Number of tourists (sum)."].sum().reset_index()
    top_estado_por_anio = estado_anual.sort_values(['year', 'Number of tourists (sum).'], ascending=[True, False])
    resumen['estado_mas_visitado_por_anio'] = (
        top_estado_por_anio.groupby('year').first().reset_index().to_dict(orient='records')
    )

    estado_acumulado = df.groupby('destination_geography')["Number of tourists (sum)."].sum().sort_values(ascending=False)
    resumen['top_5_estados_mas_visitados'] = estado_acumulado.head(5).to_dict()

    # País con más turistas y top 5
    pais_acumulado = df.groupby('geography')["Number of tourists (sum)."].sum().sort_values(ascending=False)
    resumen['pais_con_mas_turistas'] = pais_acumulado.head(1).to_dict()
    resumen['top_5_paises_emisores'] = pais_acumulado.head(5).to_dict()

    # Porcentaje por sexo
    total_turistas = df["Number of tourists (sum)."].sum()
    resumen['porcentaje_por_sexo'] = (
        df.groupby('sex')["Number of tourists (sum)."]
        .sum()
        .apply(lambda x: round(x / total_turistas * 100, 2))
        .to_dict()
    )

    return resumen

@st.cache_data
def generar_preguntas(df, n=10):
    
    # df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    # Asegúrate de que 'date' esté en formato datetime
    df['date'] = pd.to_datetime(df['date'])

    # Extraer año y mes como columnas auxiliares
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Contar cuántos meses únicos hay por año
    meses_por_anio = df.groupby('year')['month'].nunique()

    # Seleccionar solo los años con 12 meses de datos
    anios_completos = meses_por_anio[meses_por_anio == 12].index

    # Filtrar el DataFrame original
    df_completo = df[df['year'].isin(anios_completos)].copy()

    # Si necesitas el campo 'date' en formato string otra vez
    df_completo['date'] = df_completo['date'].dt.strftime('%Y-%m-%d')

    # Elimina las columnas auxiliares si ya no las necesitas
    df_completo = df_completo.drop(columns=['year', 'month'])
    airports = list(df_completo.airport_iata.unique())
    data = resume_data(df_completo)
    return generar_pregunta_con_gpt(data, airports, n)