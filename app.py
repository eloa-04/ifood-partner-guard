import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="iFood Partner Guard",
        page_icon=":pizza:",
    layout="wide"
)

# ─── GROQ ─────────────────────────────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── DETECTA MODELO DISPONÍVEL ────────────────────────────────────────────────
@st.cache_resource
def get_model():
    models = client.models.list()
    ids = [m.id for m in models.data]
    preferidos = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]
    for p in preferidos:
        if p in ids:
            return p
    # fallback: primeiro modelo de chat disponível
    chat_models = [m.id for m in models.data if "whisper" not in m.id.lower()]
    return chat_models[0] if chat_models else None

modelo_ativo = get_model()

# ─── DADOS SIMULADOS ──────────────────────────────────────────────────────────
dados = {
    "Restaurante": [
        "Burger King Lapa", "Pizza Hut Centro", "Sushi Mania",
        "Frango Express", "Taco Bell Pinheiros", "Veggie House",
        "Churrascão do Zé", "Crepe Paris", "Açaí Power", "Macarrão & Cia"
    ],
    "Pedidos_Ultimos_30d": [320, 45, 180, 90, 210, 30, 15, 150, 400, 60],
    "Ticket_Medio_R$":     [42,  38,  75,  28,  35,  45, 55,  30,  22,  40],
    "Avaliacao_Media":     [4.5, 3.1, 4.2, 2.8, 4.0, 3.5, 2.5, 4.3, 4.7, 3.8],
    "Reclamacoes_Ultimos_30d": [5, 22, 8, 30, 6, 18, 35, 4, 2, 15],
    "Dias_Sem_Pedido":     [0,   3,   1,   7,   0,   5,  12,  1,   0,   4]
}

df = pd.DataFrame(dados)

# ─── SCORE ────────────────────────────────────────────────────────────────────
def calcular_score(row):
    score  = min(row["Pedidos_Ultimos_30d"] / 400 * 30, 30)
    score += min(row["Avaliacao_Media"] / 5 * 25, 25)
    score += max(0, 25 - (row["Reclamacoes_Ultimos_30d"] / 35 * 25))
    score += max(0, 20 - (row["Dias_Sem_Pedido"] / 12 * 20))
    return round(score, 1)

def classificar(score):
    if score >= 70:  return "🟢 Saudável"
    elif score >= 45: return "🟡 Atenção"
    else:             return "🔴 Crítico"

df["Score"]  = df.apply(calcular_score, axis=1)
df["Status"] = df["Score"].apply(classificar)
df = df.sort_values("Score", ascending=True)

# ─── INTERFACE ────────────────────────────────────────────────────────────────
st.title("iFood Partner Guard")
