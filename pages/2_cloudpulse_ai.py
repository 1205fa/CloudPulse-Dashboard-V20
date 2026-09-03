import streamlit as st
import boto3
import json
import os
import time
from dotenv import load_dotenv

from backend.discovery import buscar_empresa

# Carrega as variáveis de ambiente
load_dotenv()

st.set_page_config(
    page_title="I.A.BI. MAGO",
    page_icon="🧙‍♂️",
    layout="wide"
)

st.title("🤖 I.A.BI. MAGO")
st.markdown(
    "Seu Agente de Inteligência Competitiva. Pergunte qualquer coisa sobre o mercado!"
)

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

        response = s3_client.get_object(
            Bucket=bucket,
            Key="raw/coleta_atual.json"
        )

        dados = json.loads(response["Body"].read().decode("utf-8"))

        return json.dumps(
            dados,
            ensure_ascii=False,
            indent=2
        )

    except Exception as e:
        return f"Erro ao acessar o histórico: {e}"


# =====================================================
# DISCOVERY EM TEMPO REAL
# =====================================================

def pesquisar_preco_ao_vivo(pergunta):

    time.sleep(1)

    pergunta = pergunta.lower()

    empresas = [
        "wizard",
        "cna",
        "fisk",
        "ccaa",
        "cultura inglesa"
    ]

    for empresa in empresas:

        if empresa in pergunta:

            resultado = buscar_empresa(empresa)

            resposta = (
                "RESULTADO DA BUSCA EM TEMPO REAL\n\n"
                f"Empresa: {resultado['empresa']}\n"
                f"Site: {resultado['url']}\n\n"
            )

            if resultado["precos"]:

                resposta += "Preços encontrados:\n"

                for preco in resultado["precos"]:
                    resposta += f"• {preco}\n"

            else:

                resposta += "Nenhum preço público encontrado.\n"

            if resultado["promocoes"]:

                resposta += "\nPromoções encontradas:\n"

                for promo in resultado["promocoes"]:
                    resposta += f"• {promo}\n"

            return resposta

    return (
        "RESULTADO DA BUSCA EM TEMPO REAL\n\n"
        "Empresa não cadastrada no Discovery Universal."
    )


# =====================================================
# MEMÓRIA
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =====================================================
# CHAT
# =====================================================

prompt = st.chat_input(
    "Digite sua pergunta..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Consultando o CloudPulse..."):

            try:

                palavras_tempo_real = [
                    "preço",
                    "preco",
                    "valor",
                    "mensalidade",
                    "bolsa",
                    "desconto",
                    "promoção",
                    "promocao"
                ]

                if any(
                    palavra in prompt.lower()
                    for palavra in palavras_tempo_real
                ):

                    contexto = pesquisar_preco_ao_vivo(prompt)

                    aviso = (
                        "🔴 **Modo Discovery em Tempo Real**\n\n"
                    )

                else:

                    contexto = obter_dados_s3()

                    aviso = (
                        "🟢 **Modo Histórico (S3)**\n\n"
                    )

                mensagens = []

                for msg in st.session_state.messages:

                    mensagens.append(
                        {
                            "role": msg["role"],
                            "content": [
                                {
                                    "text": msg["content"]
                                }
                            ]
                        }
                    )

                prompt_sistema = f"""
Você é o I.A.BI. MAGO do CloudPulse.

Contexto disponível:

{contexto}

Regras:

- Nunca invente preços.

- Use apenas os dados recebidos.

- Se o contexto vier do Discovery,
informe claramente que acabou de realizar
uma busca em tempo real.

- Caso não exista preço disponível,
explique isso ao usuário.

- Responda como um analista de inteligência competitiva.
"""

                resposta = bedrock_client.converse(

                    modelId=os.getenv(
                        "MODEL_ID",
                        "amazon.nova-lite-v1:0"
                    ),

                    system=[
                        {
                            "text": prompt_sistema
                        }
                    ],

                    messages=mensagens

                )

                texto = resposta["output"]["message"]["content"][0]["text"]

                resposta_final = aviso + texto

                st.markdown(resposta_final)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": resposta_final
                    }
                )

            except Exception as e:

                st.error(str(e))
