import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def buscar_urls():
    """
    Agente Discovery: Entra na raiz do concorrente e mapeia todas as URLs ocultas.
    """
    url = "https://www.wizard.com.br"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = set()
            
            for tag in soup.find_all("a", href=True):
                href = urljoin(url, tag["href"])
                # Pega apenas links que pertençam ao domínio da Wizard
                if "wizard.com.br" in href:
                    links.add(href)
                    
            lista_final = sorted(list(links))
            return lista_final
            
        else:
            print(f"❌ Erro no Discovery. Status: {response.status_code}")
            return []
            
    except Exception as erro:
        print(f"❌ Erro de conexão no Discovery: {erro}")
        return []
