import streamlit as st
import random
from utils.questions_ai import *
st.set_page_config(page_title="Adivina el INPC", layout="centered")

x, y = generar_data_adivina_inpc(df)