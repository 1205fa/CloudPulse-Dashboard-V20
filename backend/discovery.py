import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

EMPRESAS = {
    "wizard": {"nome": "Wizard", "url": "https://www.wizard.com.br"},
    "cna": {"nome": "CNA", "url": "https://www.cna.com.br"},
    "fisk": {"nome": "Fisk", "url": "https://www.fisk.com.br"},
    "ccaa": {"nome": "CCAA", "url": "https://www.ccaa.com.br"},
    "cultura inglesa": {"nome": "Cultura Inglesa", "url": "https://www.culturainglesa.com.br"}
}

CURSOS_ALVO = ["inglês", "espanhol", "francês", "alemão", "italiano", "japonês", "coreano", "programação", "robótica"]

# Rotas estratégicas que o crawler vai visitar em cada concorrente
ROTAS_ALVO = [
    "", "/blog", "/promocoes", "/ofertas", "/contato", 
    "/franquias", "/escolas", "/cursos", "/perguntas-frequentes", "/teste-de-ingles"
]

def buscar_empresa(nome_empresa):
    empresa = EMPRESAS.get(nome_empresa.lower())

    if not empresa:
        return {"status": "erro", "erro": "Empresa não cadastrada.", "mensagem": "Empresa desconhecida."}

    # Variáveis globais para armazenar os dados de TODAS as páginas visitadas
    links_encontrados = set()
    whatsapps = set()
    redes_sociais = set()
    formularios = set()
    blog = set()
    faq = set()
    franquias_links = set()
    campanhas = set()
    telefones = set()
    emails = set()
    precos = set()
    cursos = set()
    promocoes = set()
    enderecos = set()
    ceps = set()
    cnpjs = set()
    meta_titulos = set()
    meta_descricoes = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    # ==========================================
    # PREPARAÇÃO DA SESSÃO DE ALTA PERFORMANCE
    # ==========================================
    session = requests.Session()
    session.headers.update(headers)
    visitadas = set()

    # ==========================================
    # O CRAWLER: Visitando página por página
    # ==========================================
    for rota in ROTAS_ALVO:
        url_alvo = urljoin(empresa["url"], rota)
        
        # Evita visitar a mesma página duas vezes
        if url_alvo in visitadas:
            continue
            
        visitadas.add(url_alvo)
        
        try:
            # Timeout otimizado: 3s para conectar, 5s para baixar os dados
            resposta = session.get(url_alvo, timeout=(3, 5), allow_redirects=True, verify=True)
            resposta.raise_for_status()
            
            # Adiciona a URL final aos visitados (caso tenha ocorrido redirecionamento)
            visitadas.add(resposta.url)
            
        except requests.RequestException:
            # Se a página não existir (404) ou der timeout, apenas pula para a próxima rota
            continue

        soup = BeautifulSoup(resposta.text, "html.parser")
        html_raw = resposta.text.lower()
        texto_limpo = soup.get_text(" ").lower()

        # 1. Meta Tags (Títulos e Descrições)
        if soup.title and soup.title.text:
            meta_titulos.add(soup.title.text.strip())
            
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_descricoes.add(meta_tag.get("content").strip())

        # 2. Rastreio de Links (Convertendo relativos para absolutos com urljoin)
        for a in soup.find_all("a", href=True):
            href_absoluto = urljoin(url_alvo, a["href"])
            
            if href_absoluto.startswith("http"):
                links_encontrados.add(href_absoluto)
                href_lower = href_absoluto.lower()
                
                if "wa.me" in href_lower or "whatsapp" in href_lower or "api.whatsapp.com" in href_lower:
                    whatsapps.add(href_absoluto)
                if any(rs in href_lower for rs in ["instagram.com", "facebook.com", "linkedin.com", "youtube.com", "tiktok.com"]):
                    redes_sociais.add(href_absoluto)
                if any(f in href_lower for f in ["contato", "matricula", "fale-conosco", "cadastro"]):
                    formularios.add(href_absoluto)
                if "blog" in href_lower or "noticias" in href_lower:
                    blog.add(href_absoluto)
                if "faq" in href_lower or "duvidas" in href_lower or "perguntas" in href_lower:
                    faq.add(href_absoluto)
                if "franquia" in href_lower or "seja-um-franqueado" in href_lower:
                    franquias_links.add(href_absoluto)
                if "campanha" in href_lower or "oferta" in href_lower or "promocao" in href_lower:
                    campanhas.add(href_absoluto)

        # 3. Telefones (Regex aprimorada e blindada)
        tel_regex = re.compile(r"\b(?:\+55\s?)?(?:\(?\d{2}\)?[\s-]?)?(?:9\d{4}|\d{4})[\s-]?\d{4}\b")
        telefones_raw = tel_regex.findall(html_raw)
        for t in telefones_raw:
            t_limpo = t.strip()
            so_numeros = re.sub(r"\D", "", t_limpo)
            if 10 <= len(so_numeros) <= 13:
                if "-" in t_limpo or "(" in t_limpo or " " in t_limpo:
                    telefones.add(t_limpo)

        # 4. E-mails (Blindados contra fakes)
        emails_raw = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html_raw)
        palavras_fake = ["seuemail", "exemplo", "example", "email.com", "teste"]
        for e in emails_raw:
            e_lower = e.lower()
            invalido = e_lower.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))
            fake = any(fw in e_lower for fw in palavras_fake)
            if not invalido and not fake:
                emails.add(e_lower)

        # 5. Preços, CEPs e CNPJs
        precos.update(re.findall(r"r\$\s?\d+(?:[.,]\d{2})?", html_raw, re.IGNORECASE))
        ceps.update(re.findall(r"\b\d{5}-?\d{3}\b", texto_limpo))
        cnpjs.update(re.findall(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", texto_limpo))

        # 6. Cursos
        cursos.update([curso for curso in CURSOS_ALVO if curso in texto_limpo])

        # 7. Promoções e Endereços
        for addr in soup.find_all("address"):
            enderecos.add(addr.get_text(" ", strip=True))
        
        palavras_promo = ["promoção", "bolsa", "desconto", "grátis", "gratuita", "matrícula", "oferta", "2 aulas"]
        palavras_end = ["rua ", "avenida ", "av. ", "cep ", "praça ", "rodovia ", "alameda ", "travessa ", "estrada ", "bairro ", "número "]

        for texto in soup.stripped_strings:
            texto_lower = texto.lower()
            if len(texto) < 200 and any(p in texto_lower for p in palavras_promo):
                promocoes.add(texto)
            if len(texto) < 150 and any(p in texto_lower for p in palavras_end):
                enderecos.add(texto)

    # ==========================================
    # 8. CONSOLIDAÇÃO DO DOSSIÊ (JSON RICO)
    # ==========================================
    dados_finais = {
        "empresa": empresa["nome"],
        "url": empresa["url"],
        "status": "ok",
        "meta_titulos": sorted(list(meta_titulos)),
        "meta_descricoes": sorted(list(meta_descricoes)),
        "cursos": sorted(list(cursos)),
        "precos": sorted(list(precos)),
        "promocoes": sorted(list(promocoes)),
        "telefones": sorted(list(telefones)),
        "emails": sorted(list(emails)),
        "whatsapp": sorted(list(whatsapps)),
        "enderecos": sorted(list(enderecos)),
        "ceps": sorted(list(ceps)),
        "cnpjs": sorted(list(cnpjs)),
        "redes_sociais": sorted(list(redes_sociais)),
        "formularios": sorted(list(formularios)),
        "campanhas": sorted(list(campanhas)),
        "blog": sorted(list(blog)),
        "faq": sorted(list(faq)),
        "franquias": sorted(list(franquias_links)),
        "dados": {
            "total_links": len(links_encontrados),
            "total_cursos": len(cursos),
            "total_promocoes": len(promocoes),
            "total_redes": len(redes_sociais)
        },
        "links": sorted(list(links_encontrados))
    }

    if not dados_finais["cursos"] and not dados_finais["promocoes"] and not dados_finais["telefones"]:
        dados_finais["mensagem"] = "Nenhuma informação estratégica encontrada nas rotas mapeadas."
    else:
        dados_finais["mensagem"] = "Dossiê corporativo extraído e consolidado com sucesso."

    return dados_finais

def buscar_preco_wizard():
    return buscar_empresa("wizard")
