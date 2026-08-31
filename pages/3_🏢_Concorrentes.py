import streamlit as st
import pandas as pd
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Concorrentes", page_icon="🏢")
st.title("🏢 Painel de Concorrentes")

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
FILE_KEY = "dados_finais.json"  # <-- Vamos ajustar esse nome real no próximo passo!

try:
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    dados_json = json.loads(response['Body'].read().decode('utf-8'))
    
    if not dados_json:
        st.warning("Nenhum dado encontrado no S3.")
    else:
        df = pd.DataFrame(dados_json)
        
        st.subheader("📊 Volume por Empresa")
        df_agrupado = df.groupby('empresa').size().reset_index(name='Total de Campanhas')
        st.dataframe(df_agrupado, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🗂️ Base de Dados Completa")
        st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Aguardando leitura do S3... (Detalhe: {e})")
