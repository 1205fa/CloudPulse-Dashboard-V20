import json
import logging

# Configuração de Log
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def comparar_coletas(arquivo_antigo, arquivo_novo):
    logging.info("⚖️ Agente Comparator: Iniciando cruzamento de dados...")
    
    # Lendo a coleta anterior (ontem)
    try:
        with open(arquivo_antigo, "r", encoding="utf-8") as f:
            dados_antigos = json.load(f)
    except FileNotFoundError:
        logging.warning(f"Arquivo {arquivo_antigo} não encontrado. Assumindo que tudo é novidade.")
        dados_antigos = []

    # Lendo a coleta atual (hoje)
    try:
        with open(arquivo_novo, "r", encoding="utf-8") as f:
            dados_novos = json.load(f)
    except FileNotFoundError:
        logging.error(f"Arquivo {arquivo_novo} não encontrado. Abortando comparação.")
        return None

    # O PULO DO GATO: Usamos .get('url', item.get('link')) 
    # Assim ele aceita o padrão CloudPulse novo ('url') e não quebra se ler o velho ('link')
    mapa_antigo = {item.get('url', item.get('link')): item for item in dados_antigos}
    mapa_novo = {item.get('url', item.get('link')): item for item in dados_novos}

    novidades = []
    removidos = []

    # 1. Caçando o que a concorrente lançou de novo
    for url_chave, item in mapa_novo.items():
        if url_chave not in mapa_antigo:
            novidades.append(item)

    # 2. Caçando o que a concorrente tirou do ar
    for url_chave, item in mapa_antigo.items():
        if url_chave not in mapa_novo:
            removidos.append(item)

    relatorio_diferencas = {
        "novas_campanhas_ou_cursos": novidades,
        "campanhas_encerradas": removidos
    }

    logging.info(f"Análise concluída: {len(novidades)} novidades detectadas e {len(removidos)} campanhas encerradas.")
    return relatorio_diferencas
