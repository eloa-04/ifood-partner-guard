import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="iFood Partner Guard",
    page_icon="🍕",
    layout="wide"
)

# ─── GEMINI ───────────────────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ─── DADOS SIMULADOS ──────────────────────────────────────────────────────────
dados = {
    "Restaurante": [
        "Burger King Lapa", "Pizza Hut Centro", "Sushi Mania",
        "Frango Express", "Taco Bell Pinheiros", "Veggie House",
        "Churrascão do Zé", "Crepe Paris", "Açaí Power", "Macarrão & Cia"
    ],
    "Pedidos_Ultimos_30d": [320, 45, 180, 90, 210, 30, 15, 150, 400, 60],
    "Ticket_Medio_R$": [42, 38, 75, 28, 35, 45, 55, 30, 22, 40],
    "Avaliacao_Media": [4.5, 3.1, 4.2, 2.8, 4.0, 3.5, 2.5, 4.3, 4.7, 3.8],
    "Reclamacoes_Ultimos_30d": [5, 22, 8, 30, 6, 18, 35, 4, 2, 15],
    "Dias_Sem_Pedido": [0, 3, 1, 7, 0, 5, 12, 1, 0, 4]
}

df = pd.DataFrame(dados)

# ─── SCORE ────────────────────────────────────────────────────────────────────
def calcular_score(row):
    score = 0
    score += min(row["Pedidos_Ultimos_30d"] / 400 * 30, 30)
    score += min(row["Avaliacao_Media"] / 5 * 25, 25)
    score += max(0, 25 - (row["Reclamacoes_Ultimos_30d"] / 35 * 25))
    score += max(0, 20 - (row["Dias_Sem_Pedido"] / 12 * 20))
    return round(score, 1)

df["Score"] = df.apply(calcular_score, axis=1)

def classificar(score):
    if score >= 70:
        return "🟢 Saudável"
    elif score >= 45:
        return "🟡 Atenção"
    else:
        return "🔴 Crítico"

df["Status"] = df["Score"].apply(classificar)
df = df.sort_values("Score", ascending=True)

# ─── INTERFACE ────────────────────────────────────────────────────────────────
st.title("🍕 iFood Partner Guard")
st.markdown("**Monitoramento de saúde de restaurantes parceiros com detecção de risco de churn**")
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("🔴 Críticos",  len(df[df["Status"] == "🔴 Crítico"]))
col2.metric("🟡 Atenção",   len(df[df["Status"] == "🟡 Atenção"]))
col3.metric("🟢 Saudáveis", len(df[df["Status"] == "🟢 Saudável"]))

st.divider()

fig = px.bar(
    df, x="Score", y="Restaurante", orientation="h", color="Status",
    color_discrete_map={
        "🟢 Saudável": "#00C853",
        "🟡 Atenção":  "#FFD600",
        "🔴 Crítico":  "#D50000"
    },
    title="Score de Saúde por Restaurante",
    labels={"Score": "Score de Saúde (0–100)"}
)
fig.update_layout(showlegend=True, height=420)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Tabela de Restaurantes")
st.dataframe(
    df[["Restaurante", "Pedidos_Ultimos_30d", "Avaliacao_Media",
        "Reclamacoes_Ultimos_30d", "Dias_Sem_Pedido", "Score", "Status"]],
    use_container_width=True, hide_index=True
)

# ─── AGENTE DE IA ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("🤖 Agente de IA — Plano de Ação")
st.markdown("Selecione um restaurante em risco e gere um plano de ação personalizado.")

restaurantes_risco = df[df["Status"] != "🟢 Saudável"]["Restaurante"].tolist()
selecionado = st.selectbox("Escolha o restaurante:", restaurantes_risco)

if st.button("🚀 Gerar Plano de Ação com IA"):
    dados_rest = df[df["Restaurante"] == selecionado].iloc[0]

    prompt = f"""
Você é um consultor especialista em marketplaces de delivery como iFood.

Um Executivo de Contas precisa de ajuda para recuperar o restaurante abaixo, que está em risco de churn.

**Restaurante:** {dados_rest['Restaurante']}
**Score de Saúde:** {dados_rest['Score']}/100 — {dados_rest['Status']}
**Pedidos nos últimos 30 dias:** {dados_rest['Pedidos_Ultimos_30d']}
**Avaliação média:** {dados_rest['Avaliacao_Media']}
**Reclamações nos últimos 30 dias:** {dados_rest['Reclamacoes_Ultimos_30d']}
**Dias sem pedido:** {dados_rest['Dias_Sem_Pedido']}

Gere um plano de ação direto e prático com:
1. Diagnóstico em 2 frases (qual é o problema principal)
2. 3 ações imediatas (próximas 48h)
3. 2 ações de médio prazo (próximas 2 semanas)
4. Uma métrica para acompanhar a recuperação

Seja específico, objetivo e use linguagem de negócios.
"""

    with st.spinner("Analisando dados e gerando plano de ação..."):
        resposta = model.generate_content(prompt)

    st.success("✅ Plano gerado com sucesso!")
    st.markdown(resposta.text)
