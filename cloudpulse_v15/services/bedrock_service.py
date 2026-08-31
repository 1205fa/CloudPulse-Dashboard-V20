import boto3
import json
import logging
from config.settings import AWS_REGION

def gerar_relatorio_ia(arquivo_json):
    logging.info("🧠 Agente IA: Iniciando análise com Amazon Bedrock...")
    
    # 1. Lê os dados raspados
    try:
        with open(arquivo_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        logging.error(f"❌ Erro: Arquivo {arquivo_json} não encontrado.")
        return None

    # 2. Monta o Prompt Estratégico
    prompt = f"""
    Você é um Analista de Inteligência Competitiva Sênior.
    Analise os seguintes cursos extraídos do concorrente Wizard:
    {json.dumps(dados, ensure_ascii=False, indent=2)}
    
    Com base nesses dados:
    1. Compare os cursos encontrados com a estratégia de mercado de idiomas.
    2. Identifique oportunidades ou padrões.
    3. Gere um relatório executivo curto e direto para a diretoria.
    """

    # 3. Comunicação com a AWS Bedrock (Claude 3 Haiku)
    try:
        client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        })

        resposta = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0", 
            body=body
        )
        
        response_body = json.loads(resposta.get("body").read())
        relatorio = response_body["content"][0]["text"]
        
        logging.info("✔ Relatório executivo gerado com sucesso pela IA!")
        
        # Salva o relatório em TXT
        with open("data/relatorio_executivo.txt", "w", encoding="utf-8") as f:
            f.write(relatorio)
            
        return relatorio

    except Exception as e:
        logging.error(f"❌ Erro de comunicação com o Bedrock: {e}")
        return None
