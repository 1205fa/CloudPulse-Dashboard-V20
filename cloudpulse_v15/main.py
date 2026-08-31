import json
import logging
import os

from config.settings import AWS_BUCKET, AWS_REGION
from agente_discovery import buscar_urls
from scraper import extrair_eventos_mercado
from validator import validar_json
from comparador import comparar_coletas
from agente_alerta import gerar_alertas
from bedrock_service import gerar_relatorio_executivo
from services.s3_service import enviar_para_s3

# Configuração de Log
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Função principal acionada pela AWS Lambda.
    """
    logger.info("🚀 Iniciando a execução da Lambda (CloudPulse BI)")

    # ==========================================================
    # FASE 1 - DISCOVERY
    # ==========================================================
    logger.info("--- 🔎 FASE 1: DISCOVERY ---")

    urls = buscar_urls()

    if urls:
        caminho_descobertas = "/tmp/descobertas.json"

        with open(caminho_descobertas, "w", encoding="utf-8") as f:
            json.dump(urls, f, indent=4, ensure_ascii=False)

        logger.info(f"Mapeados {len(urls)} links.")

    # ==========================================================
    # FASE 2 - CONTENT INTELLIGENCE
    # ==========================================================
    logger.info("--- 🧠 FASE 2: CONTENT INTELLIGENCE ---")

    eventos = extrair_eventos_mercado()

    if eventos:

        caminho_dados = "/tmp/eventos_mercado.json"

        with open(caminho_dados, "w", encoding="utf-8") as f:
            json.dump(eventos, f, indent=4, ensure_ascii=False)

        logger.info(
            f"Extraídos {len(eventos)} eventos de negócios estruturados."
        )

        # ==========================================================
        # FASE 3 - VALIDAÇÃO E STORAGE
        # ==========================================================
        if validar_json(eventos):

            logger.info("--- ☁️ FASE 3: UPLOAD AWS S3 ---")

            sucesso = enviar_para_s3(
                AWS_BUCKET,
                caminho_dados,
                "raw/coleta_atual.json"
            )

            if sucesso:
                logger.info("✅ Upload realizado para o Amazon S3.")
            else:
                logger.error("❌ Falha no upload para o Amazon S3.")

            # ==========================================================
            # FASE 4 - BUSINESS INTELLIGENCE
            # ==========================================================
            logger.info("--- ⚖️ FASE 4: BUSINESS INTELLIGENCE ---")

            caminho_ontem = "/tmp/ontem.json"

            if not os.path.exists(caminho_ontem):
                falso_ontem = [
                    {
                        "link": "site.com/antigo",
                        "titulo": "Velho"
                    }
                ]

                with open(caminho_ontem, "w", encoding="utf-8") as f:
                    json.dump(falso_ontem, f)

            relatorio_mudancas = comparar_coletas(
                caminho_ontem,
                caminho_dados
            )

            # ==========================================================
            # FASE 5 - ALERTAS
            # ==========================================================
            logger.info("--- 🚨 FASE 5: ALERTAS ---")

            alertas = gerar_alertas(relatorio_mudancas)

            if alertas:

                logger.info(
                    f"✅ FINALIZADO: {len(alertas)} alertas de alta prioridade prontos!"
                )

                # ==========================================================
                # FASE 6 - AMAZON BEDROCK
                # ==========================================================
                logger.info("--- 🤖 FASE 6: IA EXECUTIVA (Bedrock) ---")

                relatorio_ia = gerar_relatorio_executivo(alertas)

                print("\n" + "=" * 60)
                print("📊 RELATÓRIO EXECUTIVO CLOUDPULSE")
                print("=" * 60)
                print(relatorio_ia)
                print("=" * 60 + "\n")

            else:
                logger.info("Nenhuma mudança crítica detectada hoje.")

            return {
                "statusCode": 200,
                "body": json.dumps(
                    "Sucesso: Pipeline CloudPulse rodou com sucesso!"
                ),
            }

        else:

            logger.error("Falha na validação dos dados.")

            return {
                "statusCode": 400,
                "body": json.dumps("Erro de Validação"),
            }

    logger.error("Nenhum dado foi extraído pelo scraper.")

    return {
        "statusCode": 500,
        "body": json.dumps("Erro: Sem dados do Scraper"),
    }


if __name__ == "__main__":
    resultado = lambda_handler({}, {})
    print(f"\nResultado da Execução: {resultado}")
