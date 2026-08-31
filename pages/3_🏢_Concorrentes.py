import streamlit as st
from database import SessionLocal
from models.alerta import Alerta

st.title("🏢 Concorrentes")

db = SessionLocal()

dados = db.query(Alerta).all()

for a in dados:

    with st.expander(a.empresa):

        st.write("Título")

        st.write(a.titulo)

        st.write(a.url)

db.close()
