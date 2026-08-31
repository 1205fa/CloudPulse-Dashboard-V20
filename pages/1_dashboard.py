import streamlit as st
import pandas as pd
import plotly.express as px
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Dashboard", page_icon="📊")
st.title("📊 Dashboard Executivo")

# S3 Client setup
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "substituir-pelo-nome-do-bucket")
FILE_KEY = "substituir-pelo-nome-do-arquivo.json"

try:
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    dados_json = json.loads(response['Body'].read().decode('utf-8'))
    
    if not dados_json:
        st.warning("Nenhum dado encontrado no S3.")
    else:
        # Transforma o JSON do S3 em um DataFrame do Pandas
        df = pd.DataFrame(dados_json)
        
        # Calculando totais com Pandas em vez do PostgreSQL
        total_campanhas = len(df)
        total_empresas = df['empresa'].nunique()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Campanhas", total_campanhas)
        with col2:
            st.metric("Empresas", total_empresas)
            
        st.divider()
        
        # Agrupando dados para o gráfico
        df_agrupado = df.groupby('empresa').size().reset_index(name='Campanhas')
        
        fig = px.bar(
            df_agrupado,
            x="empresa",
            y="Campanhas",
            color="empresa",
            text="Campanhas",
            height=500,
            labels={"empresa": "Empresa"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader("Últimas campanhas")
        
        # Pegando os 10 últimos registros baseados na data
        df_ultimos = df.sort_values(by="criado_em", ascending=False).head(10)
        
        for _, alerta in df_ultimos.iterrows():
            st.info(
                f"""
**Empresa:** {alerta['empresa']}

**Título:** {alerta['titulo']}

🔗 {alerta['url']}
"""
            )

except Exception as e:
    st.error(f"Aguardando configuração das credenciais do S3... (Detalhe: {e})")
