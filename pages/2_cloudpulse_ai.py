import streamlit as st
import boto3
import json
import os
import time
from dotenv import load_dotenv

# Carrega as variaveis de ambiente
load_dotenv()

st.set_page_config(page_title="I.A.BI. MAGO", page_icon="🧙‍♂️", layout="wide")

st.title("🤖 I.A.BI. MAGO")
st.markdown("Seu Agente de Inteligência Competitiva. Pergunte qualquer coisa sobre o mercado!")

# --- CONFIGURACAO DOS CLIENTES AWS ---
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

# --- MODULO 1: HISTORICO (S3) ---
def obter_dados_s3():
    try:
        bucket = os.getenv("S3_BUCKET_NAME", "cloudpulse-fabricio-v12")
        response = s3_client.get_object(Bucket=bucket, Key="raw/coleta_atual.json")
        dados = json.loads(response["Body"].read().decode("utf-8"))
        return json.dumps(dados, ensure_ascii=False)
    except Exception as e:
        return "Nenhum dado recente encontrado ou erro no S3: " + str(e)

# --- MODULO 2: TEMPO REAL (SIMULADOR DE SCRAPER) ---
def pesquisar_preco_ao_vivo(pergunta):
    # Simula o tempo de um web scraper entrando no site
    time.sleep(2)
    pergunta_lower = pergunta.lower()
    
    if "inglês" in pergunta_lower or "wizard" in pergunta_lower or "ingles" in pergunta_lower:
        return (
            "RESULTADO DA BUSCA EM TEMPO REAL: "
            "O curso de Inglês Online ao Vivo na Wizard está R$ 289,90/mês. "
            "Há uma campanha ativa (Projeto Águias) oferecendo bolsas."
        )
    elif "cna" in pergunta_lower:
        return (
            "RESULTADO DA BUSCA EM TEMPO REAL: "
            "CNA: Inglês presencial a partir de R$ 319,90/mês com isenção de taxa de matrícula."
        )
    else:
        return (
            "RESULTADO DA BUSCA EM TEMPO REAL: "
            "Não foi possível extrair o preço exato ou a bolsa no site deste concorrente neste exato segundo."
        )

# --- GERENCIAMENTO DE MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LOGICA DO CHAT E ROTEAMENTO ---
if prompt := st.chat_input("Digite seu comando (ex: Qual o preco do curso de ingles?)..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando intenção e buscando dados..."):
            try:
                # ROTEADOR DE INTENCAO
                palavras_chave_tempo_real = ["preço", "preco", "valor", "mensalidade", "custa", "bolsa", "desconto"]
                
                if any(palavra in prompt.lower() for palavra in palavras_chave_tempo_real):
                    # ROTA 1: Aciona o agente de tempo real
                    dados_contexto = pesquisar_preco_ao_vivo(prompt)
                    aviso_rota = "*(Ativando Módulo de Busca em Tempo Real...)*\n\n"
                else:
                    # ROTA 2: Aciona o banco de dados S3
                    dados_contexto = obter_dados_s3()
                    aviso_rota = "*(Consultando Base Histórica no S3...)*\n\n"
                
                # Monta as mensagens para o Bedrock
                bedrock_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] in ["user", "assistant"]:
                        # Remove o aviso da rota para nao confundir a IA nas mensagens antigas
                        conteudo_limpo = msg["content"].replace("*(Ativando Módulo de Busca em Tempo Real...)*\n\n", "").replace("*(Consultando Base Histórica no S3...)*\n\n", "")
                        bedrock_messages.append({
                            "role": msg["role"],
                            "content": [{"text": conteudo_limpo}]
                        })

                # Prompt do sistema a prova de nano (sem aspas triplas)
                prompt_sistema = (
                    "Você é o I.A.BI. MAGO, o Agente Especialista de Inteligência Competitiva do projeto CloudPulse.\n"
                    "Sua missão é ajudar a analisar dados, concorrentes, ameaças e tendências do mercado.\n\n"
                    "Abaixo estão os dados de contexto (podem ser do histórico do S3 ou de uma busca em tempo real):\n"
                    + dados_contexto + "\n\n"
                    "REGRAS OBRIGATÓRIAS:\n"
                    "1. Baseie suas análises ESTRITAMENTE nesses dados fornecidos.\n"
                    "2. Se a informação for 'RESULTADO DA BUSCA EM TEMPO REAL', destaque na sua resposta que você acabou de buscar isso ao vivo na internet para o usuário.\n"
                    "3. Seja direto, executivo e aja como um analista sênior."
                )

                system_prompts = [{"text": prompt_sistema}]

                resposta = bedrock_client.converse(
                    modelId=os.getenv("MODEL_ID", "amazon.nova-lite-v1:0"),
                    messages=bedrock_messages,
                    system=system_prompts
                )
                
                texto_ia = resposta["output"]["message"]["content"][0]["text"]
                
                # Exibe o aviso da rota escolhida junto com a resposta da IA
                resposta_final = aviso_rota + texto_ia
                
                st.markdown(resposta_final)
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                    
            except Exception as e:
                st.error("Erro ao processar a resposta do Mago: " + str(e) + ". Verifique as credenciais no Secrets do Streamlit Cloud.")
