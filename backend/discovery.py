import requests
import re

EMPRESAS = {
    "wizard": {
        "nome": "Wizard",
        "url": "https://www.wizard.com.br/cursos/ingles/"
    },
    "cna": {
        "nome": "CNA",
        "url": "https://www.cna.com.br/"
    },
    "fisk": {
        "nome": "Fisk",
        "url": "https://www.fisk.com.br/"
    },
    "ccaa": {
        "nome": "CCAA",
        "url": "https://www.ccaa.com.br/"
    },
    "cultura inglesa": {
        "nome": "Cultura Inglesa",
        "url": "https://www.culturainglesa.com.br/"
    }
}


def buscar_empresa(nome_empresa):
    empresa = EMPRESAS.get(nome_empresa.lower())

    if not empresa:
        return {
            "status": "erro",
            "erro": "Empresa não cadastrada."
        }

    try:

        resposta = requests.get(
            empresa["url"],
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        html = resposta.text.lower()

        precos = re.findall(r"r\$ ?\d+[.,]?\d*", html)

        promocoes = []

        palavras = [
            "promoção",
            "promoções",
            "bolsa",
            "bolsas",
            "desconto",
            "grátis",
            "gratuito",
            "matrícula",
            "2 aulas"
        ]

        for palavra in palavras:
            if palavra in html:
                promocoes.append(palavra)

        return {
            "empresa": empresa["nome"],
            "status": "ok",
            "url": empresa["url"],
            "precos": list(set(precos)),
            "promocoes": list(set(promocoes))
        }

    except Exception as e:

        return {
            "empresa": empresa["nome"],
            "status": "erro",
            "erro": str(e)
        }


def buscar_preco_wizard():
    return buscar_empresa("wizard")
