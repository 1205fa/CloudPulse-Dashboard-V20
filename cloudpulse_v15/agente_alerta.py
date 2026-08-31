import logging
import json
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def gerar_alertas(relatorio_comparador):
    """
    Recebe as diferenças encontradas pelo comparador e 
    gera alertas focados para a equipe de Marketing.
    """
    logging.info("🚨 Alert Agent: Analisando as mudanças do mercado...")
    
    if not relatorio_comparador:
        logging.warning("Nenhum relatório para analisar.")
        return []

    alertas_gerados = []
    data_alerta = datetime.now().isoformat()

    # 1. Alertas de Lançamentos e Promoções (O que entrou de novo)
    for novidade in relatorio_comparador.get("novas_campanhas_ou_cursos", []):
        # Filtra para alertar apenas o que importa (Alta prioridade)
        if novidade.get("prioridade") == "Alta" or novidade.get("tipo_conteudo") == "PROMOCAO":
            alerta = {
                "tipo_alerta": novidade["tipo_conteudo"],
                "prioridade": "URGENTE",
                "titulo": "🔥 Nova campanha da concorrência detectada!",
                "empresa": novidade.get("origem", "Wizard"),
                "descricao": f"Identificamos um novo conteúdo estratégico: {novidade['titulo']}",
                "url": novidade["url"],
                "data_alerta": data_alerta
            }
            alertas_gerados.append(alerta)
            logging.info(f"ALERTA GERADO: {alerta['titulo']} - {alerta['descricao']}")

    return alertas_gerados

# ==========================================
# TESTE LOCAL DO AGENTE DE ALERTA
# ==========================================
if __name__ == "__main__":
    print("\n🚨 Testando o Alert Agent...\n")
    
    # Simulando a resposta que vem do nosso comparador.py
    simulacao_comparador = {
        "novas_campanhas_ou_cursos": [
            {
                "tipo_conteudo": "PROMOCAO",
                "categoria": "Marketing",
                "titulo": "Inglês Business 50% OFF",
                "url": "site.com/promo",
                "prioridade": "Alta",
                "origem": "Wizard"
            },
            {
                "tipo_conteudo": "ARTIGO",
                "titulo": "Como estudar em casa",
                "url": "site.com/blog",
                "prioridade": "Média"
            }
        ],
        "campanhas_encerradas": []
    }
    
    resultado = gerar_alertas(simulacao_comparador)
    
    print("Alertas Finais Gerados:")
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
