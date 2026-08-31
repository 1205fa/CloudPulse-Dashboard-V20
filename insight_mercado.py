import os
import boto3
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import func

from database import SessionLocal
from models.alerta import Alerta

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
MODEL_ID = os.getenv("MODEL_ID")


def obter_contexto():
    db = SessionLocal()

    try:

        total = db.query(Alerta).count()

        empresas = (
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

        contexto = f"Total de campanhas detectadas: {total}\n\n"

        contexto += "Campanhas por empresa:\n"

        for empresa, qtd in empresas:
            contexto += f"- {empresa}: {qtd}\n"

        contexto += "\nÚltimas campanhas:\n"

        for alerta in ultimos:
            contexto += (
                f"- [{alerta.empresa}] "
                f"{alerta.titulo}\n"
            )

        return contexto

    finally:
        db.close()


def gerar_insight():

    contexto = obter_contexto()

    prompt = f"""
Você é um especialista em Inteligência Competitiva.

Analise os dados abaixo.

{contexto}

Escreva um relatório executivo contendo:

1. Qual empresa está mais agressiva.
2. Quais tendências aparecem.
3. O que merece atenção.
4. Uma recomendação estratégica.

Responda em português.
"""

    cliente = boto3.client(
        "bedrock-runtime",
        region_name=AWS_REGION
    )

    resposta = cliente.converse(
        modelId=MODEL_ID,
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

    return resposta["output"]["message"]["content"][0]["text"]


# ============================
# STREAMLIT
# ============================

st.set_page_config(
    page_title="CloudPulse Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CloudPulse Intelligence")

st.write(
    """
Este módulo utiliza os dados armazenados no PostgreSQL
para gerar análises estratégicas utilizando
Amazon Nova Lite.
"""
)

if st.button("🚀 Gerar Insight Estratégico"):

    with st.spinner("Consultando PostgreSQL e IA..."):

        try:

            contexto = obter_contexto()

            st.subheader("Dados encontrados")

            st.code(contexto)

            insight = gerar_insight()

            st.subheader("Insight Estratégico")

            st.success(insight)

        except Exception as e:

            st.error(e)
