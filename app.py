import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

st.set_page_config(page_title="iFood Partner Guard", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

dados = {
    "Restaurante": [
        "Burger King Lapa", "Pizza Hut Centro", "Sushi Mania",
        "Frango Express", "Taco Bell Pinheiros", "Veggie House",
        "Churrascao do Ze", "Crepe Paris", "Acai Power", "Macarrao e Cia"
    ],
    "Pedidos_Ultimos_30d": [320, 45, 180, 90, 210, 30, 15, 150, 400, 60],
    "Ticket_Medio":        [42,  38,  75,  28,  35,  45, 55,  30,  22,  40],
    "Avaliacao_Media":     [4.5, 3.1, 4.2, 2.8, 4.0, 3.5, 2.5, 4.3, 4.7, 3.8],
    "Reclamacoes_30d":     [5,   22,  8,   30,  6,   18,  35,  4,   2,   15],
    "Dias_Sem_Pedido":     [0,   3,   1,   7,   0,   5,   12,  1,   0,   4]
}

df = pd.DataFrame(dados)

def calcular_score(row):
    score  = min(row["Pedidos_Ultimos_30d"] / 400 * 30, 30)
    score += min(row["Avaliacao_Media"] / 5 * 25, 25)
    score += max(0, 25 - (row["Reclamacoes_30d"] / 35 * 25))
    score += max(0, 20 - (row["Dias_Sem_Pedido"] / 12 * 20))
    return round(score, 1)

def classificar(score):
    if score >= 70:   return "Saudavel"
    elif score >= 45: return "Atencao"
    else:             return "Critico"

df["Score"]  = df.apply(calcular_score, axis=1)
df["Status"] = df["Score"].apply(classificar)
df = df.sort_values("Score", ascending=True)

st.title("iFood Partner Guard")
st.markdown("**Monitoramento de saude de restaurantes parceiros com deteccao de risco de churn**")
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Criticos",  len(df[df["Status"] == "Critico"]))
col2.metric("Atencao",   len(df[df["Status"] == "Atencao"]))
col3.metric("Saudaveis", len(df[df["Status"] == "Saudavel"]))

st.divider()

cores = {"Saudavel": "#00C853", "Atencao": "#FFD600", "Critico": "#D50000"}
fig = px.bar(
    df, x="Score", y="Restaurante", orientation="h", color="Status",
    color_discrete_map=cores,
    title="Score de Saude por Restaurante",
    labels={"Score": "Score de Saude (0-100)"}
)
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Tabela de Restaurantes")
st.dataframe(
    df[["Restaurante","Pedidos_Ultimos_30d","Avaliacao_Media",
        "Reclamacoes_30d","Dias_Sem_Pedido","Score","Status"]],
    use_container_width=True, hide_index=True
)

st.divider()
st.subheader("Agente de IA - Plano de Acao")
st.markdown("Selecione um restaurante em risco e gere um plano de acao personalizado.")

# mostra modelos disponíveis para debug
try:
    modelos = client.models.list()
    ids = [m.id for m in modelos.data]
    st.caption("Modelos disponiveis: " + ", ".join(ids))
except Exception as e:
    st.error(f"Erro ao listar modelos: {e}")
    ids = []

restaurantes_risco = df[df["Status"] != "Saudavel"]["Restaurante"].tolist()
selecionado = st.selectbox("Escolha o restaurante:", restaurantes_risco)

if ids:
    MODELO = "openai/gpt-oss-20b"
st.caption(f"Modelo em uso: {MODELO}")

    if st.button("Gerar Plano de Acao com IA"):
        r = df[df["Restaurante"] == selecionado].iloc[0]
        prompt = f"""
Voce e um consultor especialista em marketplaces de delivery como iFood.
Um Executivo de Contas precisa recuperar o restaurante abaixo, em risco de churn.

Restaurante: {r['Restaurante']}
Score de Saude: {r['Score']}/100 - {r['Status']}
Pedidos nos ultimos 30 dias: {r['Pedidos_Ultimos_30d']}
Avaliacao media: {r['Avaliacao_Media']}
Reclamacoes nos ultimos 30 dias: {r['Reclamacoes_30d']}
Dias sem pedido: {r['Dias_Sem_Pedido']}

Gere um plano de acao com:
1. Diagnostico em 2 frases
2. 3 acoes imediatas (proximas 48h)
3. 2 acoes de medio prazo (proximas 2 semanas)
4. Uma metrica para acompanhar a recuperacao
"""
        with st.spinner("Gerando plano de acao..."):
            resposta = client.chat.completions.create(
                                model=MODELO,
                messages=[{"role": "user", "content": prompt}]
            )
        st.success("Plano gerado!")
        st.markdown(resposta.choices[0].message.content)
