import streamlit as st
import pandas as pd
import plotly.express as px
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Dashboard", page_icon="📊")
st.title("📊 Painel Executivo")

# Cliente S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
FILE_KEY = "raw/coleta_atual.json"

try:
    response = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=FILE_KEY
    )

    dados_json = json.loads(
        response["Body"].read().decode("utf-8")
    )

    if not dados_json:
        st.warning("Nenhum dado encontrado no S3.")

    else:
        # Cria o DataFrame
        df = pd.DataFrame(dados_json)

        # Indicadores
        total_campanhas = len(df)
        total_empresas = df["origem"].nunique()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Campanhas", total_campanhas)

        with col2:
            st.metric("Empresas", total_empresas)

        st.divider()

        # Gráfico
        df_agrupado = (
            df.groupby("origem")
            .size()
            .reset_index(name="Campanhas")
        )

        fig = px.bar(
            df_agrupado,
            x="origem",
            y="Campanhas",
            color="origem",
            text="Campanhas",
            height=500,
            labels={
                "origem": "Empresa",
                "Campanhas": "Quantidade"
            }
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("📋 Últimas campanhas")

        if "data_coleta" in df.columns:
            df = df.sort_values(
                by="data_coleta",
                ascending=False
            )

        for _, alerta in df.head(10).iterrows():
            with st.container(border=True):
                st.markdown(f"**Empresa:** {alerta.get('origem', '-')}")
                st.markdown(f"**Título:** {alerta.get('titulo', '-')}")
                st.markdown(f"**Categoria:** {alerta.get('categoria', '-')}")
                st.markdown(f"**Prioridade:** {alerta.get('prioridade', '-')}")
                st.markdown(f"🔗 {alerta.get('url', '-')}")

except Exception as e:
    st.error(f"Erro ao carregar dados do S3: {e}")
