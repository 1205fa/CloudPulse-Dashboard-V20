import os
import streamlit as st
import boto3
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="CloudPulse AI", page_icon="🤖")
st.title("🤖 CloudPulse AI")

# Configuração do Cliente S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
FILE_KEY = "raw/coleta_atual.json"  # <-- ATENÇÃO: Ajustaremos esse nome final em breve

try:
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    dados_json = json.loads(response['Body'].read().decode('utf-8'))
    
    if not dados_json:
        st.warning("Nenhum dado encontrado no S3 para análise.")
    else:
        df = pd.DataFrame(dados_json)
        
        total = len(df)
        df_agrupado = df.groupby('origem').size().reset_index(name='Campanhas')
        df_ultimos = df.sort_values(by="data_coleta", ascending=False).head(5)
        
        texto = f"Existem {total} campanhas.\n"
        for _, row in df_agrupado.iterrows():
            texto += f"{row['origem']}: {row['Campanhas']}\n"
            
        texto += "\nÚltimas campanhas:\n"
        for _, alerta in df_ultimos.iterrows():
            texto += f"- [{alerta['origem']}] {alerta['titulo']}\n"
            
        st.code(texto)

        if st.button("Gerar Insight"):
            try:
                cliente = boto3.client(
                    "bedrock-runtime",
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
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
                    modelId=os.getenv("MODEL_ID", "amazon.titan-text-lite-v1"), # Fallback seguro de modelo
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ]
                )

                texto_ia = resposta["output"]["message"]["content"][0]["text"]
                st.success(texto_ia)
            except Exception as bedrock_err:
                 st.error(f"Erro no Bedrock: {bedrock_err}. Verifique se o MODEL_ID está no Secrets.")

except Exception as e:
    st.error(f"Falha na leitura do S3. Verifique o nome do arquivo FILE_KEY. (Detalhe: {e})")
