# iFood Partner Guard

Dashboard inteligente de monitoramento de saúde de restaurantes parceiros,
com detecção de risco de churn e agente de IA para geração de planos de ação.

## Problema

Restaurantes parceiros que reduzem pedidos, recebem mais reclamações ou ficam
dias sem atividade tendem a abandonar a plataforma. Executivos de Contas precisam
identificar esses sinais cedo e agir com rapidez — mas sem uma ferramenta
centralizada, esse monitoramento é manual e reativo.

## Solução

O iFood Partner Guard automatiza esse monitoramento com três camadas:

1. **Score de Saúde** — algoritmo que combina volume de pedidos, avaliação média,
reclamações e dias sem atividade em um índice de 0 a 100
2. **Dashboard interativo** — visualização em tempo real dos restaurantes em risco,
classificados em Crítico, Atenção e Saudável
3. **Agente de IA** — gera planos de ação personalizados para cada restaurante
em risco com ações imediatas e de médio prazo

## Automação
![Fluxo N8N](./Fluxo%20N8N.png)
Um workflow no N8N roda diariamente às 8h, filtra os restaurantes críticos
e envia alertas automáticos por e-mail para o Executivo de Contas responsável,
garantindo que nenhum parceiro em risco passe despercebido.

## Arquitetura

```
Dados dos restaurantes
        ↓
Cálculo do Score de Saúde (Python + Pandas)
        ↓
Dashboard interativo (Streamlit + Plotly)
        ↓
Agente de IA — Plano de Ação (Groq API)

N8N (Schedule diário)
        ↓
Filtra restaurantes críticos
        ↓
Alerta por e-mail ao Executivo de Contas
```

## Stack

- Python, Pandas, Streamlit, Plotly
- Groq API (LLM para geração de planos de ação)
- N8N (automação de alertas)

## Demo

[Acessar o dashboard ao vivo](https://ifood-partner-guard-m4kenwmqhkdf85uhnhxddb.streamlit.app/)

## Como rodar localmente

```bash
pip install streamlit pandas plotly groq
streamlit run app.py
```
