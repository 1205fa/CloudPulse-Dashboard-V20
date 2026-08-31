import streamlit as st
import pandas as pd
import plotly.express as px
from database import SessionLocal
from models.alerta import Alerta
from sqlalchemy import func

st.set_page_config(page_title="Dashboard", page_icon="📊")

st.title("📊 Dashboard Executivo")

db = SessionLocal()

total = db.query(Alerta).count()

empresas = (
    db.query(
        Alerta.empresa,
        func.count(Alerta.id).label("Total")
    )
    .group_by(Alerta.empresa)
    .all()
)

ultimos = (
    db.query(Alerta)
    .order_by(Alerta.criado_em.desc())
    .limit(10)
    .all()
)

db.close()

col1, col2 = st.columns(2)

with col1:
    st.metric("Campanhas", total)

with col2:
    st.metric("Empresas", len(empresas))

st.divider()

df = pd.DataFrame(empresas, columns=["Empresa", "Campanhas"])

fig = px.bar(
    df,
    x="Empresa",
    y="Campanhas",
    color="Empresa",
    text="Campanhas",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Últimas campanhas")

for alerta in ultimos:
    st.info(
        f"""
**Empresa:** {alerta.empresa}

**Título:** {alerta.titulo}

🔗 {alerta.url}
"""
    )
