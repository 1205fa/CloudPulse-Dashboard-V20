import streamlit as st
import boto3
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

st.set_page_config(page_title="I.A.BI. MAGO", page_icon="🧙‍♂️", layout="wide")

st.title("🤖 I.A.BI. MAGO")
st.markdown("Seu Agente de Inteligência Competitiva. Pergunte qualquer coisa sobre o mercado!")

# --- CONFIGURAÇÃO DOS CLIENTES AWS ---
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2")
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2")
)

def obter_dados_s3():
    """Busca os dados reais da coleta direto do S3."""
    try:
        bucket = os.getenv("S3_BUCKET_NAME", "cloudpulse-fabricio-v12")
        response = s3_client.get_object(Bucket=bucket, Key="raw/coleta_atual.json")
        dados = json.loads(response['Body'].read().decode('utf-8'))
        return json.dumps(dados, ensure_ascii=False)
    except Exception as e:
        return f"Nenhum dado recente encontrado ou erro no S3: {str(e)}"

# --- GERENCIAMENTO DE MEMÓRIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DO CHAT ---
if prompt := st.chat_input("Digite seu comando (ex: Faça um resumo do mercado)..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando cenário competitivo..."):
            try:
                dados_mercado = obter_dados_s3()
                
                bedrock_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] in ["user", "assistant"]:
                        bedrock_messages.append({
                            "role": msg["role"],
                            "content": [{"text": msg["content"]}]
                        })

                prompt_sistema = f"""Você é o I.A.BI. MAGO, o Agente Especialista de Inteligência Competitiva do projeto CloudPulse.
Sua missão é ajudar a analisar dados, concorrentes, ameaças e tendências do mercado.

Abaixo estão os dados REAIS e mais recentes de mercado coletados (em formato JSON):
{dados_mercado}

REGRAS OBRIGATÓRIAS:
1. Baseie suas análises ESTRITAMENTE nesses dados fornecidos quando o usuário perguntar sobre números de campanhas, foco, ou estratégias atuais.
2. Se a pergunta for genérica, use seu conhecimento estratégico, mas tente cruzar com as informações dos dados reais.
3. Seja direto, executivo e aja como um analista sênior."""

                system_prompts = [{"text": prompt_sistema}]

                resposta = bedrock_client.converse(
                    modelId=os.getenv("MODEL_ID", "amazon.nova-lite-v1:0"),
                    messages=bedrock_messages,
                    system=system_prompts
                )
                
                texto_ia = resposta["output"]["message"]["content"][0]["text"]
                st.markdown(texto_ia)
                st.session_state.messages.append({"role": "assistant", "content": texto_ia})
                    
            except Exception as e:
                st.error(f"Erro ao processar a resposta do Mago: {e}. Verifique as credenciais no Secrets do Streamlit Cloud.")
