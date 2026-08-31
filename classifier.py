import logging

def classificar_conteudo(url, texto_pagina):
    """
    Analisa o conteúdo cru e a URL para classificar o evento de mercado.
    Retorna um dicionário com a estrutura padrão CloudPulse.
    """
    texto_pagina = texto_pagina.lower()
    url = url.lower()

    # Classificação padrão caso não ache nada específico
    categoria = "Institucional"
    tipo = "PAGINA_GERAL"
    prioridade = "Baixa"

    # Motor de Regras (Heurística)
    if any(kw in texto_pagina for kw in ["desconto", "off", "promoção", "bolsa"]):
        categoria = "Marketing"
        tipo = "PROMOCAO"
        prioridade = "Alta"
    elif "curso" in url or "turmas" in url:
        categoria = "Produto"
        tipo = "CURSO"
        prioridade = "Alta"
    elif "blog" in url or "dicas" in url or "noticia" in url:
        categoria = "Conteúdo"
        tipo = "ARTIGO"
        prioridade = "Média"
    elif "faq" in url or "duvidas" in texto_pagina or "dúvidas" in texto_pagina:
        categoria = "Atendimento"
        tipo = "FAQ"
        prioridade = "Média"
    elif "franquia" in url or "parceria" in texto_pagina:
        categoria = "Expansão"
        tipo = "PARCERIA"
        prioridade = "Média"

    return {
        "categoria": categoria,
        "tipo_conteudo": tipo,
        "prioridade": prioridade
    }

# ==========================================
# TESTE LOCAL DO CÉREBRO CLASSIFICADOR
# ==========================================
if __name__ == "__main__":
    print("\n🧠 Iniciando Teste do Classificador CloudPulse...\n")
    
    # Simulando a página de uma promoção
    teste_promo = classificar_conteudo("site.com/ingles", "Aproveite 50% de DESCONTO hoje!")
    print(f"Teste 1 (Página com desconto): {teste_promo}")
    
    # Simulando uma página de dúvidas
    teste_faq = classificar_conteudo("site.com/faq", "Veja as dúvidas frequentes dos alunos.")
    print(f"Teste 2 (Página de Dúvidas): {teste_faq}")
    
    # Simulando um blog
    teste_blog = classificar_conteudo("site.com/blog/ingles-rapido", "Aprenda dicas valiosas.")
    print(f"Teste 3 (Página de Blog): {teste_blog}\n")
