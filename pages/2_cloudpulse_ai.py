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
# DISCOVERY EM TEMPO REAL (O NOVO CRAWLER)
# =====================================================
def pesquisar_preco_ao_vivo(pergunta):
    time.sleep(1)
    pergunta = pergunta.lower()
    empresas = ["wizard", "cna", "fisk", "ccaa", "cultura inglesa"]

    for empresa in empresas:
        if empresa in pergunta:
            resultado = buscar_empresa(empresa)

            resposta = (
                "### 📊 DOSSIÊ DE INTELIGÊNCIA EM TEMPO REAL\n\n"
                f"**Empresa:** {resultado.get('empresa', empresa.title())}\n"
                f"**Site:** {resultado.get('url', 'N/A')}\n\n"
            )

            if resultado.get("precos"):
                resposta += "💰 **Preços Mapeados:**\n"
                for preco in resultado["precos"]: resposta += f"• {preco}\n"
            else:
                resposta += "💰 **Preços Mapeados:** Funil fechado (sem valores públicos).\n"

            if resultado.get("promocoes"):
                resposta += "\n🎁 **Promoções e Ofertas:**\n"
                for promo in resultado["promocoes"]: resposta += f"• {promo}\n"

            if resultado.get("cursos"):
                resposta += "\n📚 **Cursos Detectados:**\n"
                for curso in resultado["cursos"]: resposta += f"• {curso.title()}\n"

            if resultado.get("telefones"):
                resposta += "\n☎️ **Telefones:**\n"
                for tel in resultado["telefones"]: resposta += f"• {tel}\n"

            if resultado.get("emails"):
                resposta += "\n📧 **E-mails:**\n"
                for email in resultado["emails"]: resposta += f"• {email}\n"

            if resultado.get("whatsapp"):
                resposta += "\n🟢 **WhatsApp:**\n"
                for wpp in resultado["whatsapp"]: resposta += f"• {wpp}\n"

            if resultado.get("redes_sociais"):
                resposta += "\n📱 **Redes Sociais:**\n"
                for rede in resultado["redes_sociais"]: resposta += f"• {rede}\n"

            if resultado.get("campanhas"):
                resposta += "\n🎯 **Links de Campanhas:**\n"
                for camp in resultado["campanhas"]: resposta += f"• {camp}\n"

            if resultado.get("links"):
                resposta += "\n🌐 **Principais Links Mapeados (Amostra):**\n"
                # Pega só os 10 primeiros para não poluir a tela
                for link in resultado["links"][:10]: resposta += f"• {link}\n" 

            return resposta

    return "❌ **Erro:** Empresa não cadastrada no motor do Crawler."

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
        with st.spinner("O Crawler V20 está varrendo a web..."):
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
                    aviso = "🔴 **Modo Crawler em Tempo Real (Web Scraper)**\n\n"
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
