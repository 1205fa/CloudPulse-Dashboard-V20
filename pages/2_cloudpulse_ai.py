import os
import streamlit as st
import boto3
from dotenv import load_dotenv

from database import SessionLocal
from models.alerta import Alerta
from sqlalchemy import func

load_dotenv()

st.set_page_config(page_title="CloudPulse AI", page_icon="🤖")

st.title("🤖 CloudPulse AI")

db = SessionLocal()

total = db.query(Alerta).count()

empresa = (
    db.query(
        Alerta.empresa,
        func.count(Alerta.id)
    )
    .group_by(Alerta.empresa)
    .all()
)

ultimos = (
    db.query(Alerta)
    .order_by(Alerta.criado_em.desc())
    .limit(5)
    .all()
)

db.close()

texto = f"Existem {total} campanhas.\n"

for e, q in empresa:
    texto += f"{e}: {q}\n"

texto += "\nÚltimas campanhas:\n"

for a in ultimos:
    texto += f"- [{a.empresa}] {a.titulo}\n"

st.code(texto)

if st.button("Gerar Insight"):

    cliente = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION")
    )

    prompt = f"""
Você é um analista de inteligência competitiva.

Dados:

{texto}

Faça:

1. Empresa líder.
2. Tendências.
3. Oportunidades.
4. Recomendações.
"""

    resposta = cliente.converse(
        modelId=os.getenv("MODEL_ID"),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    )

    texto_ia = resposta["output"]["message"]["content"][0]["text"]

    st.success(texto_ia)
