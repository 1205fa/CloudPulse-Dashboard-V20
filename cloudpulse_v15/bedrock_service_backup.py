import boto3
import json
import logging

logger = logging.getLogger()

def gerar_relatorio_executivo(alertas):
    logging.info("🤖 Bedrock Agent: Solicitando análise executiva para a IA...")
    
    if not alertas:
        return "Nenhum alerta crítico para analisar no momento."

    # O "Cérebro" do nosso analista virtual
    prompt = f"""Você é um analista de Inteligência Competitiva Sênior da nossa empresa.
    Analise estes alertas recentes capturados em tempo real do site da concorrência:
    {json.dumps(alertas, ensure_ascii=False, indent=2)}

    Gere um relatório executivo curto e direto (máximo de 3 parágrafos) focado em:
    1. Qual é a estratégia atual da concorrência (ex: foco em quais idiomas/formatos)?
    2. Quais os riscos para a nossa fatia de mercado?
    3. Uma recomendação de ação imediata para a nossa equipe de Marketing reagir.
    """

    try:
        # Conectando na AWS (vai usar as credenciais que estiverem no ambiente)
        client = boto3.client('bedrock-runtime', region_name='us-east-1')

        # Usando o padrão Claude 3 (Muito comum e rápido no Bedrock)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })

        # Chama a IA na AWS
        response = client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0", # Ajuste se usarem outro modelo
            body=body
        )

        response_body = json.loads(response.get('body').read())
        relatorio = response_body.get('content')[0].get('text')
        
        logging.info("✅ Relatório gerado com sucesso pelo Amazon Bedrock!")
        return relatorio

    except Exception as e:
        logging.error(f"Falha ao conectar com o Bedrock: {e}")
        return "⚠️ (Simulação Local) A IA detectou forte ofensiva em múltiplos idiomas. Sugere-se campanha imediata de bolsas para retenção de mercado. (Conecte a AWS para relatório completo)."

# ==========================================
# TESTE LOCAL DO BEDROCK
# ==========================================
if __name__ == "__main__":
    teste_alerta = [{"titulo": "Inglês 50% OFF", "empresa": "Wizard"}]
    print(gerar_relatorio_executivo(teste_alerta))
