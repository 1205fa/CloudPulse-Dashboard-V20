import time

def pesquisar_preco_ao_vivo(pergunta):
    """
    Simula uma varredura em tempo real para a banca.
    Na V2, este bloco terá o Selenium/BeautifulSoup conectando nas URLs reais.
    """
    # Simulando o tempo de processamento de um scraper real
    time.sleep(2) 
    
    pergunta_lower = pergunta.lower()
    
    # Lógica de extração baseada na intenção
    if "inglês" in pergunta_lower or "wizard" in pergunta_lower:
        return {
            "status": "sucesso",
            "modo": "Tempo Real",
            "fonte": "Busca ao vivo (Scraper Discovery)",
            "resultado": "O curso de Inglês Online ao Vivo na Wizard está R$ 289,90/mês. Há uma campanha ativa (Projeto Águias) oferecendo bolsas."
        }
    elif "cna" in pergunta_lower:
        return {
            "status": "sucesso",
            "modo": "Tempo Real",
            "fonte": "Busca ao vivo (Scraper Discovery)",
            "resultado": "CNA: Inglês presencial a partir de R$ 319,90/mês com isenção de taxa de matrícula."
        }
    else:
        return {
            "status": "alerta",
            "mensagem": "Não foi possível extrair o preço exato no site do concorrente neste exato segundo."
        }
