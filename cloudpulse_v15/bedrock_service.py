import boto3
import json
import logging

logger = logging.getLogger()

REGION = "us-east-1"
MODEL_ID = "amazon.nova-lite-v1:0"


def gerar_relatorio_executivo(alertas):
    logger.info("🤖 Bedrock Agent: Gerando relatório executivo com Amazon Nova Lite...")

    if not alertas:
        return "Nenhum alerta crítico para analisar."

    prompt = f"""
Você é um Analista Sênior de Inteligência Competitiva.

Analise os alertas abaixo:

{json.dumps(alertas, ensure_ascii=False, indent=2)}

Crie um relatório executivo contendo:

1. Resumo executivo
2. Estratégia observada da concorrência
3. Riscos para nossa empresa
4. Oportunidades identificadas
5. Recomendações imediatas

Responda em português do Brasil.
"""

    try:

        client = boto3.client(
            "bedrock-runtime",
            region_name=REGION
        )

        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 700,
                "temperature": 0.3,
                "top_p": 0.9
            }
        }

        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        resposta = json.loads(
            response["body"].read()
        )

        texto = resposta["output"]["message"]["content"][0]["text"]

        logger.info("✅ Relatório gerado com sucesso!")

        return texto

    except Exception as erro:

        logger.exception("Erro ao chamar o Amazon Bedrock")

        return f"""
⚠️ Falha ao consultar o Amazon Bedrock.

Erro:

{erro}
"""


if __name__ == "__main__":

    alertas = [
        {
            "empresa": "Wizard",
            "titulo": "50% OFF Inglês"
        }
    ]

    print(
        gerar_relatorio_executivo(alertas)
    )
