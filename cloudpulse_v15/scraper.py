import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from classifier import classificar_conteudo

# Configuração de Log CloudPulse
logger = logging.getLogger()
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s"
    )


def extrair_eventos_mercado():
    logging.info("🕷️ Content Intelligence Agent: Buscando páginas para leitura...")

    caminhos_tentativa = [
        "/tmp/descobertas.json",
        "data/descobertas.json"
    ]

    urls = []

    for caminho in caminhos_tentativa:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                urls = json.load(f)
                break
        except FileNotFoundError:
            continue

    if not urls:
        logging.error("Nenhum link encontrado pelo Discovery. Abortando inteligência.")
        return []

    eventos_coletados = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    data_atual = datetime.now().isoformat()

    logging.info("🧠 Acionando o Classificador CloudPulse para análise de conteúdo...")

    for url in urls[:7]:

        try:
            resposta = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            if resposta.status_code != 200:
                continue

            # Corrige a codificação automaticamente
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

            texto_pagina = soup.get_text(
                separator=" ",
                strip=True
            )

            classificacao = classificar_conteudo(
                url,
                texto_pagina
            )

            evento = {
                "tipo_conteudo": classificacao["tipo_conteudo"],
                "categoria": classificacao["categoria"],
                "titulo": titulo,
                "url": url,
                "origem": "Wizard",
                "data_coleta": data_atual,
                "prioridade": classificacao["prioridade"]
            }

            eventos_coletados.append(evento)

            logging.info(
                f"Classificado [{evento['prioridade']}]: "
                f"{evento['tipo_conteudo']} - {titulo}"
            )

        except Exception as e:
            logging.warning(f"Falha ao acessar {url}: {e}")

    return eventos_coletados
