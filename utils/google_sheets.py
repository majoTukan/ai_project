from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
from datetime import datetime
import pandas as pd


def guardar_usuario_en_sheets(user_name):
    # json_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    json_path = "proyecto-aplicar-sql-76873ce6150b.json"
    # print(json_path)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open('TriviaScores').sheet1  # o usa .worksheet('nombre_hoja')

    # Agregar el usuario a la siguiente fila vacía
    sheet.append_row([str(datetime.now()), '', user_name, '', ''])



def guardar_score_en_sheets(user_name, trivia_id, score, total):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    json_path = "proyecto-aplicar-sql-76873ce6150b.json"

    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open('TriviaScores').sheet1

    data = sheet.get_all_records()
    
    for idx, row in enumerate(data, start=2):  # empieza desde la fila 2 (después del header)
        if row['user'] == user_name and row['trivia_id'] == trivia_id:
            if row['score'] is None or score > row['score']:
                # actualizar fila
                sheet.update(f"A{idx}:E{idx}", [[str(datetime.now()), trivia_id, user_name,  score, total]])
            return  # ya se procesó, salimos

    # si no lo encontró, es nuevo → insertamos
    sheet.append_row([str(datetime.now()),  trivia_id, user_name, score, total])



def obtener_datos_scores():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    json_path = "proyecto-aplicar-sql-76873ce6150b.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open('TriviaScores').sheet1

    # Obtener todas las filas
    datos = sheet.get_all_records()  # Regresa lista de dicts

    # Convertir a DataFrame para facilitar manejo y orden
    df = pd.DataFrame(datos)
    df = df.dropna(subset=[ 'trivia_id', 'score', 'total'])
    cols_a_checar = [ 'trivia_id', 'score', 'total']
    for col in cols_a_checar:
        df = df[df[col].astype(str).str.strip() != '']

    return df