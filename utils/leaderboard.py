import gspread
import pandas as pd
from datetime import datetime
import streamlit as st

@st.cache_resource
def _sheet(sheet_name: str):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open(sheet_name)
    return sh.worksheet("Scores")

def record_score(sheet_name: str, trivia_id: str, user: str, score: int, total: int):
    ws = _sheet(sheet_name)
    ts = datetime.utcnow().isoformat(timespec="seconds")
    ws.append_row([ts, trivia_id, user, score, total])

def get_leaderboard(sheet_name: str, trivia_id: str, top_n: int = 20) -> pd.DataFrame:
    ws = _sheet(sheet_name)
    df = pd.DataFrame(ws.get_all_records())
    df = df[df["trivia_id"] == trivia_id]
    df["pct"] = (df["score"] / df["total"]).round(2)
    return df.sort_values(["score", "timestamp"], ascending=[False, True]).head(top_n).reset_index(drop=True)
