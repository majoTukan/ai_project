import pandas as pd
import random
import json
import re
import os
import streamlit as st  # solo si estás usando Streamlit aquí
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@st.cache_data
def load_turism_data():
    token = os.getenv('API_TUKAN')
    df = pd.read_csv(f"https://client.tukanmx.com/visualizations/retrieve_query_csv/en/5079bf2a-58d0-4632-b02f-1c25c6c2130b/{token}", delimiter='|')
    df["date"] = pd.to_datetime(df["date"], errors="coerce")  # convierte a datetime
    # Eliminar columnas que terminan en '__ref'
    df = df[[col for col in df.columns if not col.endswith("__ref")]]
    if df["date"].isnull().any():
        st.warning("⚠️ Algunas fechas no se pudieron convertir. Revisa el archivo CSV.")
    return df

@st.cache_data
def load_vehicles_data():
    token = os.getenv('API_TUKAN')
    df = pd.read_csv(f"https://client.tukanmx.com/visualizations/retrieve_query_csv/es/91fce6c7-4636-4e51-b72f-1b0ee60e6400/{token}", delimiter='|')
    df["date"] = pd.to_datetime(df["date"], errors="coerce")  # convierte a datetime
    # Eliminar columnas que terminan en '__ref'
    df = df[[col for col in df.columns if not col.endswith("__ref")]]
    if df["date"].isnull().any():
        st.warning("⚠️ Algunas fechas no se pudieron convertir. Revisa el archivo CSV.")
    return df

@st.cache_data
def load_inpc_data():
    token = os.getenv('API_TUKAN')
    df = pd.read_csv(f"https://client.tukanmx.com/visualizations/retrieve_query_csv/es/0ccbd4cd-cbbd-4bac-8531-38e74539a53d/{token}", delimiter='|')
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
    Ten en cuenta que los aeropuertos están nombrados según ciudades, y esas ciudades pertenecen a estados de la república. Por lo tanto, una pregunta sobre un aeropuerto puede implicar la misma información que una pregunta sobre un estado.
    Evita generar preguntas redundantes o que puedan revelar la respuesta de otra a través esta relación ciudad-estado. Asegúrate de que las preguntas sean independientes incluso cuando se refieran a ubicaciones relacionadas.

    Sigue estas reglas estrictamente:

    1. Cubre distintos enfoques de análisis, como: diferencias por género, país de origen, estacionalidad, patrones, destinos más comunes, comparaciones entre periodos, etc.
    2. **Cada pregunta debe abordar un enfoque o idea distinta.**
    3. **Evita cualquier tipo de solapamiento o dependencia entre preguntas.** Ninguna pregunta debe sugerir, insinuar ni revelar total o parcialmente la respuesta de otra.
    4. No incluyas cifras o fechas específicas en la pregunta. **En la explicación sí puedes incluir cifras reales** si ayudan a entender la respuesta (ej. “X turistas hombres vs Y mujeres”).
    5. Las preguntas deben estar redactadas con claridad y sin ambigüedad.
    6. Las explicaciones deben ser educativas y aportar valor, con cifras o contexto adicional cuando sea útil.

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

    **IMPORTANTE:** Revisa todas las preguntas antes de finalizar y asegúrate de que ninguna dependa del contenido, tema o respuesta de otra. Todas deben poder responderse de forma independiente sin conocer las demás.

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


def generar_pregunta_vehiculos_con_gpt(data, uniques, n:int = 10):
    
    
    prompt_usuario = f"""
    Actúa como un experto en industria automotriz y educación. A partir de los siguientes datos en formato JSON sobre las ventas de vehículos ligeros en México:

    {data}

    Las cifras incluyen datos agregados de ventas por país de origen del vehículo, tipo de vehículo, marca y modelo, así como su evolución anual y mensual. Tu tarea es generar {n} preguntas didácticas en formato JSON. Las preguntas deben ser **interesantes, variadas, no obvias** y fomentar el pensamiento crítico. Deben ser de tipo "opcion_multiple" o "verdadero_falso".

    Sigue estas reglas estrictamente:

    1. Cubre distintos enfoques de análisis, como: evolución por año, cambios en preferencias de tipo de vehículo, participación por país de origen, marcas más y menos populares, impacto de la estacionalidad, y cambios en tendencias de modelos.
    2. **Cada pregunta debe abordar un enfoque o idea distinta.**
    3. **Evita cualquier tipo de solapamiento o dependencia entre preguntas.** Ninguna pregunta debe sugerir, insinuar ni revelar total o parcialmente la respuesta de otra.
    4. No incluyas cifras o fechas específicas en la **pregunta**. **En la explicación sí puedes incluir cifras reales** si ayudan a entender la respuesta (por ejemplo, “X SUV vendidos frente a Y compactos”).
    5. Las preguntas deben estar redactadas con claridad y sin ambigüedad.
    6. Las explicaciones deben ser educativas y aportar valor, con cifras o contexto adicional cuando sea útil.

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

    **IMPORTANTE:** Revisa todas las preguntas antes de finalizar y asegúrate de que ninguna dependa del contenido, tema o respuesta de otra. Todas deben poder responderse de forma independiente sin conocer las demás.

    Nota: Para preguntas de verdadero o falso, usa únicamente las opciones ["Verdadero", "Falso"].
    """



    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un generador de preguntas tipo trivia sobre venta de vehículos en México."},
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

def generar_preguntas_inpc_con_gpt(data, uniques, n:int = 10):
    prompt_usuario = f"""
    Actúa como un experto en economía y educación. A partir de los siguientes datos en formato JSON sobre el Índice Nacional de Precios al Consumidor (INPC) en México:

    {data}
    Se te comparten los valores únicos de los estados disponibles y de los productos: {uniques}.
    Tu tarea es generar {n} preguntas didácticas en formato JSON. Las preguntas deben ser **interesantes, variadas, no obvias** y fomentar el pensamiento crítico. Deben ser de tipo "opcion_multiple" o "verdadero_falso".

    Sigue estas reglas estrictamente:

    1. Cubre distintos enfoques de análisis, como: variaciones por estado, productos más caros y baratos, evolución del INPC por año, impacto de la inflación en diferentes categorías, etc.
    2. **Cada pregunta debe abordar un enfoque o idea distinta.**
    3. **Evita cualquier tipo de solapamiento o dependencia entre preguntas.** Ninguna pregunta debe sugerir, insinuar ni revelar total o parcialmente la respuesta de otra.
    4. No incluyas cifras o fechas específicas en la **pregunta**. **En la explicación sí debes incluir cifras reales** para ayudar a entender la respuesta (por ejemplo, “X% de aumento en el INPC”).
    5. Las preguntas deben estar redactadas con claridad y sin ambigüedad.
    6. Las explicaciones deben ser educativas y aportar valor, con cifras o contexto adicional cuando sea útilb y convirtiendo decimales a formato porcentual cuando corresponda (ejemplo: 0.05 REPRESENTA EL 5%).

    Formato esperado:
    Genera una lista en formato JSON con preguntas de opción múltiple sobre el INPC en México. Evita que la respuesta correcta sea casi siempre la primera opción.
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

    **IMPORTANTE:** Revisa todas las preguntas antes de finalizar y asegúrate de que ninguna dependa del contenido, tema o respuesta de otra. Todas deben poder responderse de forma independiente sin conocer las demás.

    Nota: Para preguntas de verdadero o falso, usa únicamente las opciones ["Verdadero", "Falso"], de otra forma solo debe haber 4 posibles opciones.
    """


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un generador de preguntas tipo trivia sobre el Índice Nacional de Precios al Consumidor (INPC) en México. Responde solo con JSON válido. No agregues comentarios, explicaciones o texto adicional fuera del JSON."},
            {"role": "user", "content": prompt_usuario},
            ],
        temperature=0.7
    )
    content = response.choices[0].message.content
    cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()

    # Parsear la respuesta
    try:
        preguntas = json.loads(cleaned)
        assert isinstance(preguntas, list), "El resultado no es una lista de preguntas."
        return preguntas
    except Exception as e:
        raise ValueError(f"No se pudo parsear la respuesta: {content}, tokens: {int(len(content.split()) * 1.33)}") from e

#---Resumir data turismo---
def resume_turism_data(df):
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
def generar_preguntas_turismo(df, n=10):
    
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
    data = resume_turism_data(df_completo)
    return generar_pregunta_con_gpt(data, airports, n)


def resume_vehicles_data(df):
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month

    resumen = {}
    resumen['descripcion_tabla'] = 'Datos de ventas de vehículos ligeros para las 22 empresas afiliadas a la Asociación Mexicana de la Industria Automotriz, (AMIA), Mitsubishi Motors y Giant Motors Latinoamérica, clasificados por el país de origen (importación) del vehículo.'
    # Aeropuerto con más y menos llegadas
    pais_ventas = df.groupby('geography')["Ventas totales de vehículos (suma)."].sum().sort_values(ascending=False)
    resumen['pais_top1_mas_ventas'] = pais_ventas.head(1).to_dict()
    resumen['pais_top1_menos_ventas'] = pais_ventas[pais_ventas > 0].tail(1).to_dict()
    resumen['top_5_paises_mas_ventas'] = pais_ventas.head(5).to_dict()
    resumen['top_5_paises_menos_ventas'] = pais_ventas.tail(5).to_dict()

    ventas_por_anio = df.groupby('year')["Ventas totales de vehículos (suma)."].sum().sort_index()
    resumen['anio_mas_ventas'] = ventas_por_anio.idxmax()
    resumen['total_ventas_por_anio'] = ventas_por_anio.to_dict()
    resumen['crecimiento_anual'] = ventas_por_anio.pct_change().round(3).fillna(0).to_dict()

    ventas_por_mes = df.groupby('month')["Ventas totales de vehículos (suma)."].sum()
    resumen['mes_con_mas_ventas'] = ventas_por_mes.idxmax()
    ventas_positivas = ventas_por_mes[ventas_por_mes > 0]
    resumen['mes_con_menos_ventas'] = ventas_positivas.idxmin()

    ventas_por_pais = df.groupby('geography')["Ventas totales de vehículos (suma)."].sum().sort_values(ascending=False)
    resumen['pais_con_mas_ventas'] = ventas_por_pais.head(1).to_dict()
    resumen['top_5_paises_origen'] = ventas_por_pais.head(5).to_dict()

    ventas_por_marca = df.groupby('car_brand')["Ventas totales de vehículos (suma)."].sum().sort_values(ascending=False)
    resumen['marca_con_mas_ventas'] = ventas_por_marca.head(1).to_dict()
    resumen['marca_con_menos_ventas'] = ventas_por_marca.tail(1).to_dict()
    resumen['top_5_marcas_mas_ventas'] = ventas_por_marca.head(5).to_dict()
    resumen['top_5_marcas_menos_ventas'] = ventas_por_marca.tail(5).to_dict()

    ventas_por_modelo = df.groupby('mex_vehicle_models')["Ventas totales de vehículos (suma)."].sum().sort_values(ascending=False)
    resumen['modelo_mas_vendido'] = ventas_por_modelo.head(1).to_dict()
    resumen['modelo_menos_vendido'] = ventas_por_modelo.tail(1).to_dict()

    ventas_por_tipo = df.groupby('vehicle_type')["Ventas totales de vehículos (suma)."].sum().sort_values(ascending=False)
    resumen['tipo_mas_vendido'] = ventas_por_tipo.head(1).to_dict()
    resumen['porcentaje_por_tipo'] = (
        ventas_por_tipo / ventas_por_tipo.sum() * 100
    ).round(2).to_dict()

    # Por país por año
    top_pais_anual = (
        df.groupby(['year', 'geography'])["Ventas totales de vehículos (suma)."]
        .sum()
        .reset_index()
        .sort_values(['year', "Ventas totales de vehículos (suma)."], ascending=[True, False])
    )
    # resumen['pais_con_mas_ventas_por_anio'] = (
    #     top_pais_anual.groupby('year').first().reset_index().to_dict(orient='records')
    # )

    # Por marca por año
    top_marca_anual = (
        df.groupby(['year', 'car_brand'])["Ventas totales de vehículos (suma)."]
        .sum()
        .reset_index()
        .sort_values(['year', "Ventas totales de vehículos (suma)."], ascending=[True, False])
    )
    # resumen['marca_con_mas_ventas_por_anio'] = (
    #     top_marca_anual.groupby('year').first().reset_index().to_dict(orient='records')
    # )

    # Por tipo de vehículo por año (más vendido y %)
    ventas_tipo_anual = (
        df.groupby(['year', 'vehicle_type'])["Ventas totales de vehículos (suma)."]
        .sum()
        .reset_index()
    )

    # Tipo más vendido por año
    top_tipo_anual = (
        ventas_tipo_anual.sort_values(['year', "Ventas totales de vehículos (suma)."], ascending=[True, False])
        .groupby('year')
        .first()
        .reset_index()
    )
    resumen['tipo_mas_vendido_por_anio'] = top_tipo_anual.to_dict(orient='records')

    # Calculamos porcentaje por tipo por año
    porcentaje_tipo_anual = (
        ventas_tipo_anual.assign(
            porcentaje=ventas_tipo_anual.groupby('year')["Ventas totales de vehículos (suma)."]
            .transform(lambda x: (x / x.sum() * 100).round(2))
        )
        .loc[:, ['year', 'vehicle_type', 'porcentaje']]
    )
    # print(porcentaje_tipo_anual)
    resumen['porcentaje_por_tipo_por_anio'] = {}
    for year, group in porcentaje_tipo_anual.groupby('year'):
        resumen['porcentaje_por_tipo_por_anio'][year] = dict(zip(group['vehicle_type'], group['porcentaje']))

    return resumen

@st.cache_data
def generar_preguntas_vehiculos(df, n=10):
    
    # df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    # Asegúrate de que 'date' esté en formato datetime
    df['date'] = pd.to_datetime(df['date'])

    # Extraer año y mes como columnas auxiliares
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Contar cuántos meses únicos hay por año
    meses_por_anio = df.groupby('year')['month'].nunique()
    anios_completos = meses_por_anio[meses_por_anio == 12].index
    df_completo = df[df['year'].isin(anios_completos)].copy()
    df_completo['date'] = df_completo['date'].dt.strftime('%Y-%m-%d')

    # Elimina las columnas auxiliares si ya no las necesitas
    df_completo = df_completo.drop(columns=['year', 'month'])
    brands = list(df_completo.car_brand.unique())
    models = list(df_completo.mex_vehicle_models.unique())
    types = list(df_completo.vehicle_type.unique())
    uniques = {'brands_uniques':brands,
               'models_uniques':models,
               'types_uniques':types}
    data = resume_vehicles_data(df_completo)
    return generar_pregunta_vehiculos_con_gpt(data, uniques, n)

def resumen_ampliado_inpc(df):
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df = df.rename(columns={
        "Índice Nacional de Precios al Consumidor (INPC) (suma).": "inpc"
    })

    resumen = {}
    resumen['descripcion_tabla'] = (
        "Índice Nacional de Precios al Consumidor (INPC) por Objeto de Gasto a Nivel Estatal. "
        "Proporciona valores mensuales del INPC para diferentes productos y servicios, "
        "por entidad federativa, desde 2018 hasta 2025."
    )

    year_min = df['year'].min()
    year_max = df['year'].max()
    resumen['rango_anios'] = {'inicio': int(year_min), 'fin': int(year_max)}

    # ---------- Productos más caros y baratos por año ----------
    productos_por_anio = {}
    for y in sorted(df['year'].unique()):
        subset = df[df['year'] == y]
        avg_by_product = subset.groupby('mex_inegi_cpi_product_structure')['inpc'].mean()
        productos_por_anio[y] = {
            'productos_mas_caros': avg_by_product.sort_values(ascending=False).head(5).round(2).to_dict(),
            'productos_mas_baratos': avg_by_product.sort_values(ascending=True).head(5).round(2).to_dict()
        }
    resumen['productos_por_anio'] = productos_por_anio

    # ---------- Estados más caros y baratos (último año) ----------
    latest_year = df['year'].max()
    df_latest = df[df['year'] == latest_year]
    state_avg = df_latest.groupby('geography')['inpc'].mean()
    resumen['estados_mas_caros'] = state_avg.sort_values(ascending=False).head(5).round(2).to_dict()
    resumen['estados_mas_baratos'] = state_avg.sort_values(ascending=True).head(5).round(2).to_dict()

    # ---------- Productos más caros y baratos (último año) ----------
    product_avg_latest = df_latest.groupby('mex_inegi_cpi_product_structure')['inpc'].mean()
    resumen['productos_mas_caros_recientes'] = product_avg_latest.sort_values(ascending=False).head(5).round(2).to_dict()
    resumen['productos_mas_baratos_recientes'] = product_avg_latest.sort_values().head(5).round(2).to_dict()

    # ---------- Productos con mayor inflación 2020–2024 ----------
    inpc_avg = df.groupby(['mex_inegi_cpi_product_structure', 'year'])['inpc'].mean().unstack()
    if 2020 in inpc_avg.columns and 2024 in inpc_avg.columns:
        crecimiento_pct = ((inpc_avg[2024] - inpc_avg[2020]) / inpc_avg[2020])
        resumen['productos_mayor_inflacion_2020_2024'] = crecimiento_pct.sort_values(ascending=False).head(5).round(3).to_dict()
        resumen['productos_menor_inflacion_2020_2024'] = crecimiento_pct.sort_values().head(5).round(3).to_dict()

    # ---------- Estados con mayor inflación por año ----------
    inflacion_por_estado_anio = {}
    for y in range(year_min + 1, year_max + 1):
        pivot = df[df['year'].isin([y-1, y])].groupby(['geography', 'year'])['inpc'].mean().unstack()
        if y-1 in pivot.columns and y in pivot.columns:
            delta = ((pivot[y] - pivot[y-1]) / pivot[y-1]).sort_values(ascending=False)
            inflacion_por_estado_anio[y] = {
                'top_5_estados_mayor_inflacion': delta.head(5).round(3).to_dict(),
                'top_5_estados_menor_inflacion': delta.tail(5).round(3).to_dict()
            }
    resumen['inflacion_estados_por_anio'] = inflacion_por_estado_anio

    # ---------- Insumos que se elevaron en pandemia y se mantuvieron caros ----------
    if 2019 in inpc_avg.columns and 2020 in inpc_avg.columns and 2024 in inpc_avg.columns:
        aumento_pandemia = (inpc_avg[2020] - inpc_avg[2019]) / inpc_avg[2019]
        mantuvo_precio = (inpc_avg[2024] - inpc_avg[2020]) / inpc_avg[2020]
        combinado = (aumento_pandemia > 0.1) & (mantuvo_precio > 0)
        resumen['productos_alzaron_en_pandemia_y_siguen_caros'] = inpc_avg.loc[combinado].mean(axis=1).sort_values(ascending=False).head(5).round(2).to_dict()

    # ---------- Estado donde X producto es más caro y más barato ----------
    # estado_producto = (
    #     df[df['year'] == df['year'].max()]
    #     .groupby(['mex_inegi_cpi_product_structure', 'geography'])['inpc']
    #     .mean()
    #     .unstack()
    # )

    # resumen['estado_por_producto_mas_y_menos_caro'] = {}

    # for producto, fila in estado_producto.iterrows():
    #     estado_mas_caro = fila.idxmax()
    #     estado_mas_barato = fila.idxmin()
    #     resumen['estado_por_producto_mas_y_menos_caro'][producto] = {
    #         'mas_caro': {
    #             'estado': estado_mas_caro,
    #             'inpc': round(fila[estado_mas_caro], 2)
    #         },
    #         'mas_barato': {
    #             'estado': estado_mas_barato,
    #             'inpc': round(fila[estado_mas_barato], 2)
    #         }
    #     }

    # ---------- Top estados más caros/baratos por categoría clave ----------
    productos_clave = {
        "renta_vivienda": "Renta de vivienda",
        "vivienda_propia": "Vivienda propia",
        "educacion_universidad": "Universidad",
        "alimentacion_tortilla": "Tortilla de maíz",
        "automoviles": "Automóviles",
        # "seguro de auto": "Seguro de automóvil",
        "Huevo": "Huevo",
        "consulta_medica": "Consulta médica",
        "estacionamiento": "Estacionamiento",
        "cine": "Cine",
        "hoteles": "Hoteles",
        "gasolina_bajo_octanaje": "Gasolina de bajo octanaje",
    }

    resumen['top_estados_por_categoria'] = {}
    ultimo_anio = df['year'].max()

    for clave, producto in productos_clave.items():
        df_prod = df[df['mex_inegi_cpi_product_structure'].str.contains(producto, case=False, na=False)]
        df_prod = df_prod[df_prod['year'] == ultimo_anio]

        if df_prod.empty:
            continue

        inpc_estado = df_prod.groupby('geography')['inpc'].mean().sort_values()

        resumen['top_estados_por_categoria'][clave] = {
            'top_5_mas_baratos': inpc_estado.head(5).round(2).to_dict(),
            'top_5_mas_caros': inpc_estado.tail(5).sort_values(ascending=False).round(2).to_dict()
        }
    


    return resumen


@st.cache_data
def generar_preguntas_inpc(df, n=10):
    
    # df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    # Asegúrate de que 'date' esté en formato datetime
    df['date'] = pd.to_datetime(df['date'])

    # Extraer año y mes como columnas auxiliares
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Contar cuántos meses únicos hay por año
    meses_por_anio = df.groupby('year')['month'].nunique()
    anios_completos = meses_por_anio[meses_por_anio == 12].index
    df_completo = df[df['year'].isin(anios_completos)].copy()
    df_completo['date'] = df_completo['date'].dt.strftime('%Y-%m-%d')

    # Elimina las columnas auxiliares si ya no las necesitas
    df_completo = df_completo.drop(columns=['year', 'month'])
    products = list(df_completo.mex_inegi_cpi_product_structure.unique())
    states = list(df_completo.geography.unique())
    uniques = {'products':products,
               'states':states}
    data = resumen_ampliado_inpc(df_completo)
    return generar_preguntas_inpc_con_gpt(data, uniques, n)

