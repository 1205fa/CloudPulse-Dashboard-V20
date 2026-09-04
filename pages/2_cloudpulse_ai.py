import streamlit as st
import boto3
import json
import os
import time
from dotenv import load_dotenv

# IMPORTAÇÃO DO NOSSO ORQUESTRADOR ENTERPRISE
from backend.orchestrator import CloudPulseOrchestrator

# Carrega as variáveis de ambiente
load_dotenv()

st.set_page_config(
    page_title="I.A.BI. MAGO",
    page_icon="🧙‍♂️",
    layout="wide"
)

st.title("🤖 I.A.BI. MAGO")
st.markdown("Seu Agente de Inteligência Competitiva. Pergunte qualquer coisa sobre o mercado!")

# =====================================================
# AWS
# =====================================================
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2")
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2")
)

# =====================================================
# HISTÓRICO (S3)
# =====================================================
def obter_dados_s3():
    try:
        bucket = os.getenv("S3_BUCKET_NAME", "cloudpulse-fabricio-v12")
        response = s3_client.get_object(Bucket=bucket, Key="raw/coleta_atual.json")
        dados = json.loads(response["Body"].read().decode("utf-8"))
        return json.dumps(dados, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erro ao acessar o histórico: {e}"

# =====================================================
# DISCOVERY EM TEMPO REAL (IA MULTIAGENTE)
# =====================================================
def pesquisar_preco_ao_vivo(pergunta):
    time.sleep(1)
    pergunta = pergunta.lower()
    empresas = ["wizard", "cna", "fisk", "ccaa", "cultura inglesa"]

    for empresa in empresas:
        if empresa in pergunta:
            # Aciona o Orquestrador Enterprise
            orquestrador = CloudPulseOrchestrator()
            resposta_orquestrada = orquestrador.executar(empresa)
            
            return resposta_orquestrada

    return "❌ **Erro:** Empresa não cadastrada no motor de agentes."

# =====================================================
# MEMÓRIA E CHAT
# =====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ex: Quais cursos a Fisk oferece? ou Qual o preço da Wizard?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Os Agentes de IA estão varrendo a web e validando os dados..."):
            try:
                # GATILHOS ATUALIZADOS PARA O CRAWLER V20
                palavras_tempo_real = [
                    "preço", "preco", "valor", "mensalidade", "bolsa", 
                    "desconto", "promoção", "promocao", "curso", "cursos",
                    "whatsapp", "link", "links", "contato", "telefone", 
                    "redes", "social", "campanha", "oferta"
                ]

                if any(palavra in prompt.lower() for palavra in palavras_tempo_real):
                    contexto = pesquisar_preco_ao_vivo(prompt)
                    usar_bedrock = False
                    aviso = "🔴 **Modo IA Multiagente Ativado (Orquestrador Enterprise)**\n\n"
                else:
                    contexto = obter_dados_s3()
                    usar_bedrock = True
                    aviso = "🟢 **Modo Histórico (AWS S3 & Bedrock)**\n\n"

                mensagens = [
                    {"role": msg["role"], "content": [{"text": msg["content"]}]}
                    for msg in st.session_state.messages
                ]

                prompt_sistema = f"""
Você é o I.A.BI. MAGO do CloudPulse.
Contexto:
{contexto}
Regras:
- Responda SOMENTE usando o contexto.
- Nunca invente preços ou dados.
- Seja objetivo e executivo.
"""
                if usar_bedrock:
                    resposta = bedrock_client.converse(
                        modelId=os.getenv("MODEL_ID", "amazon.nova-lite-v1:0"),
                        system=[{"text": prompt_sistema}],
                        messages=mensagens
                    )
                    texto = resposta["output"]["message"]["content"][0]["text"]
                else:
                    texto = contexto

                resposta_final = aviso + texto
                st.markdown(resposta_final)
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})

            except Exception as e:
                st.error(f"Ocorreu um erro: {str(e)}")
