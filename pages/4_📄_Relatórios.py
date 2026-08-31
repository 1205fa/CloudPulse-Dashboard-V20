import streamlit as st
import boto3
import json
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.title("📄 Relatórios")

# Cliente S3 usando as credenciais do ambiente
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

# TODO: Precisamos definir os nomes corretos aqui
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "substituir-pelo-nome-do-bucket")
FILE_KEY = "raw/coleta_atual.json"

try:
    st.info("Buscando dados mais recentes no S3...")
    
    # Faz a leitura do arquivo gerado pela Lambda
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    dados_json = json.loads(response['Body'].read().decode('utf-8'))
    
    # Exibe na tela usando o Pandas para formatar a tabela
    if dados_json:
        df = pd.DataFrame(dados_json)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("O arquivo JSON está vazio.")

except Exception as e:
    st.error(f"Erro ao conectar com o S3 ou ler o arquivo: {e}")
