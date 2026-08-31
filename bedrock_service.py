import boto3
import logging

logger = logging.getLogger()

client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-2"
)

MODEL_ID = "amazon.nova-lite-v1:0"


def gerar_relatorio_executivo(alertas):

    if not alertas:
        return "Nenhum alerta encontrado."

    prompt = f"""
Você é um analista de inteligência competitiva.

Analise estes alertas:

{alertas}

Responda em português.

Faça:

1. Resumo Executivo
2. Estratégia da concorrência
3. Riscos
4. Ações recomendadas
"""

    try:

        response = client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            inferenceConfig={
                "maxTokens": 700,
                "temperature": 0.3
            }
        )

        texto = response["output"]["message"]["content"][0]["text"]

        return texto

    except Exception as e:

        logger.exception(e)

        return f"Erro Bedrock: {e}"


if __name__ == "__main__":

    teste = [
        {
            "empresa":"Wizard",
            "titulo":"Curso de Inglês 50% OFF"
        }
    ]

    print(gerar_relatorio_executivo(teste))
