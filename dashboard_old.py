import streamlit as st

from services.analytics import obter_metricas
from components.cards import mostrar_cards
from components.charts import grafico_empresas


st.set_page_config(
    page_title="CloudPulse Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CloudPulse Intelligence")

st.write(
    "Dashboard Executivo de Inteligência Competitiva"
)

metricas = obter_metricas()

mostrar_cards(metricas)

st.divider()

grafico_empresas(metricas)

st.divider()

st.subheader("📰 Últimas campanhas")

for alerta in metricas["ultimas"]:

    st.markdown(
        f"""
**{alerta.empresa}**

{alerta.titulo}

{alerta.criado_em}

---
"""
    )
