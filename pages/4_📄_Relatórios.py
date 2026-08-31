import streamlit as st
from database import SessionLocal
from models.alerta import Alerta

st.title("📄 Relatórios")

db = SessionLocal()

dados = db.query(Alerta).all()

st.dataframe(
    [
        {
            "Empresa": a.empresa,
            "Título": a.titulo,
            "URL": a.url,
            "Data": a.criado_em
        }
        for a in dados
    ],
    use_container_width=True
)

db.close()
