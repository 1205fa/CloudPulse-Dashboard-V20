from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import os
import json
from dotenv import load_dotenv
from typing import List, Dict

# Carrega as variáveis de ambiente
load_dotenv()

app = FastAPI(title="CloudPulse IA Backend - I.A.BI. MAGO")

# Clientes AWS
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

class ChatRequest(BaseModel):
    mensagens: List[Dict[str, str]]

def obter_dados_s3():
    """Função ninja para puxar os dados reais da coleta antes de responder."""
    try:
        bucket = os.getenv("S3_BUCKET_NAME", "cloudpulse-fabricio-v12")
        response = s3_client.get_object(Bucket=bucket, Key="raw/coleta_atual.json")
        dados = json.loads(response['Body'].read().decode('utf-8'))
        return json.dumps(dados, ensure_ascii=False)
    except Exception as e:
        return f"Nenhum dado recente encontrado ou erro no S3: {str(e)}"

@app.post("/chat")
async def chat_com_ia(request: ChatRequest):
    try:
        # 1. Busca os dados reais do S3
        dados_mercado = obter_dados_s3()

        # 2. Monta o histórico de mensagens
        bedrock_messages = []
        for msg in request.mensagens:
            if msg["role"] in ["user", "assistant"]:
                bedrock_messages.append({
                    "role": msg["role"],
                    "content": [{"text": msg["content"]}]
                })

        # 3. Injeta os dados reais no cérebro do Mago
        prompt_sistema = f"""Você é o I.A.BI. MAGO, o Agente Especialista de Inteligência Competitiva do projeto CloudPulse.
Sua missão é ajudar a analisar dados, concorrentes, ameaças e tendências do mercado.

Abaixo estão os dados REAIS e mais recentes de mercado coletados pelo nosso sistema (em formato JSON):
{dados_mercado}

REGRAS OBRIGATÓRIAS:
1. Baseie suas análises ESTRITAMENTE nesses dados fornecidos quando o usuário perguntar sobre números de campanhas, foco, ou estratégias atuais.
2. Se a pergunta for genérica, use seu conhecimento estratégico, mas tente cruzar com as informações dos dados reais.
3. Seja direto, executivo e aja como um analista sênior."""

        system_prompts = [{"text": prompt_sistema}]

        # 4. Chama a AWS Bedrock
        resposta = bedrock_client.converse(
            modelId=os.getenv("MODEL_ID", "amazon.nova-lite-v1:0"),
            messages=bedrock_messages,
            system=system_prompts
        )

        texto_ia = resposta["output"]["message"]["content"][0]["text"]
        return {"resposta": texto_ia}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Mago: {str(e)}")

@app.get("/")
def root():
    return {"status": "I.A.BI. MAGO Online, com Memória e lendo dados reais do S3!"}
