import streamlit as st
from utils.questions import *
from utils.questions_ai import *
from utils.trivia_generator import *
from utils.ui_helpers import mostrar_usuario_en_esquina

st.set_page_config(page_title="Trivia de INPC", layout="centered")
mostrar_usuario_en_esquina()
trivia_generator('inpc')