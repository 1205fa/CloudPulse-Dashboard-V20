import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from classifier import classificar_conteudo
from alerta_repository import salvar_alerta

# ==========================================================
# CONFIGURAÇÃO DE LOG
# ==========================================================

logger = logging.getLogger()

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s"
    )

# ==========================================================
# SCRAPER PRINCIPAL
# ==========================================================

def extrair_eventos_mercado():

    logger.info("🕷️ Content Intelligence Agent iniciado...")

    caminhos = [
        "/tmp/descobertas.json",
        "data/descobertas.json"
    ]

    urls = []

    # Procura o arquivo de URLs
    for caminho in caminhos:
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                urls = json.load(arquivo)
                break
        except FileNotFoundError:
            continue

    if not urls:
        logger.error("❌ Nenhuma URL encontrada pelo Discovery.")
        return []

    eventos = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    data_coleta = datetime.now().isoformat()

    logger.info("🧠 Classificando conteúdos encontrados...")

    # Limite para testes
    for url in urls[:7]:

        try:

            resposta = requests.get(
                url,
                headers=headers,
                timeout=8
            )

            if resposta.status_code != 200:
                logger.warning(f"URL ignorada ({resposta.status_code}): {url}")
                continue

            # Corrige problemas de acentuação
            resposta.encoding = resposta.apparent_encoding

            soup = BeautifulSoup(
                resposta.text,
                "html.parser"
            )

            titulo = (
                soup.title.get_text(strip=True)
                if soup.title
                else "Página sem título"
            )

            texto = soup.get_text(
                separator=" ",
                strip=True
            )

            classificacao = classificar_conteudo(
                url,
                texto
            )

            evento = {
                "tipo_conteudo": classificacao["tipo_conteudo"],
                "categoria": classificacao["categoria"],
                "titulo": titulo,
                "url": url,
                "origem": "Wizard",
                "data_coleta": data_coleta,
                "prioridade": classificacao["prioridade"]
            }

            eventos.append(evento)

            logger.info(
                f"✅ [{evento['origem']}] {titulo}"
            )

            # ==========================================
            # Salva automaticamente no PostgreSQL
            # ==========================================

            try:

                salvou = salvar_alerta(
                    empresa="Wizard",
                    titulo=titulo,
                    url=url
                )

                if salvou:
                    logger.info("💾 Alerta salvo no PostgreSQL.")
                else:
                    logger.info("📌 Alerta já existia no banco.")

            except Exception:
                logger.exception("❌ Erro ao salvar no banco")

        except Exception:
            logger.exception(f"❌ Falha ao acessar {url}")

    return eventos


# ==========================================================
# TESTE LOCAL
# ==========================================================

if __name__ == "__main__":

    eventos = extrair_eventos_mercado()

    print("\n" + "=" * 60)
    print(f"Foram encontrados {len(eventos)} eventos.")
    print("=" * 60)

    for evento in eventos:
        print(evento)
