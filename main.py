import streamlit as st
import pandas as pd
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração da página (deve ser o primeiro comando)
st.set_page_config(
    page_title="CloudPulse Intelligence",
    page_icon="☁️",
    layout="wide"
)

# --- HERO PRINCIPAL ---
st.title("☁️ CloudPulse Intelligence Platform")
st.markdown("### Transformando dados de mercado em decisões estratégicas com Inteligência Artificial.")
st.divider()

# --- BUSCA DOS DADOS REAIS NO S3 ---
total_empresas = 0
total_campanhas = 0
categorias_ativas = 0
ultima_coleta = "Aguardando..."

try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    
    BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    FILE_KEY = "raw/coleta_atual.json"
    
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    dados_json = json.loads(response["Body"].read().decode("utf-8"))
    
    if dados_json:
        df = pd.DataFrame(dados_json)
        
        # Cálculos usando os dados reais do seu scraper
        total_campanhas = len(df)
        total_empresas = df["origem"].nunique() if "origem" in df.columns else 0
        categorias_ativas = df["categoria"].nunique() if "categoria" in df.columns else 0
        
        if "data_coleta" in df.columns:
            # Pega a data mais recente da coleta e formata
            ultima_coleta = str(df["data_coleta"].max())[:10]

except Exception as e:
    st.warning("Conectando aos dados em tempo real... (Painel aguardando credenciais na nuvem)")

# --- INDICADORES EM DESTAQUE ---
st.markdown("#### Visão Geral do Mercado (Tempo Real)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Empresas Monitoradas", value=total_empresas)
with col2:
    st.metric(label="Campanhas Ativas", value=total_campanhas)
with col3:
    st.metric(label="Categorias Mapeadas", value=categorias_ativas)
with col4:
    st.metric(label="Última Coleta", value=ultima_coleta)

st.divider()

# --- FUNCIONALIDADES ---
st.markdown("### 🌟 Nossos Diferenciais")
c1, c2, c3 = st.columns(3)

with c1:
    st.info("📊 **Dashboard Executivo**\n\nVisualização interativa com base unificada.")
    st.info("📄 **Relatórios**\n\nGeração automatizada de inteligência de mercado.")
with c2:
    st.success("🤖 **I.A.BI. MAGO**\n\nAgente autônomo respondendo com dados 100% reais.")
    st.success("🚨 **Alertas**\n\nIdentificação de anomalias, mudanças e prioridades.")
with c3:
    st.warning("🏢 **Monitoramento**\n\nMapeamento contínuo dos principais concorrentes.")
    st.warning("☁️ **Infraestrutura AWS**\n\nAlta disponibilidade Serverless com S3 e Bedrock.")

st.divider()

# --- ARQUITETURA ---
st.markdown("### 🏗️ Arquitetura de Dados")
st.markdown("""
```text
🌐 Internet ➔ 🕷️ Scraper ➔ 🪣 Amazon S3 ➔ 🧠 AWS Bedrock ➔ 🪄 I.A.BI. MAGO ➔ 📊 Dashboard
