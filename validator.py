import logging

def validar_json(dados):
    logging.info("🛡️ Agente Validator: Iniciando inspeção de qualidade dos dados CloudPulse...")
    if not dados:
        logging.warning("Nenhum dado para validar.")
        return False

    # Estes são os novos campos obrigatórios da nossa arquitetura de BI
    campos_obrigatorios = [
        "tipo_conteudo", "categoria", "titulo", "url", 
        "origem", "data_coleta", "prioridade"
    ]

    for item in dados:
        for campo in campos_obrigatorios:
            if campo not in item:
                logging.error(f"Validação falhou: Falta o campo '{campo}' no item {item.get('titulo', 'Desconhecido')}.")
                return False
            
        # Garante que os valores principais não vieram em branco
        if not str(item["titulo"]).strip() or not str(item["url"]).strip():
            logging.error("Validação falhou: Título ou URL vieram completamente vazios.")
            return False

    logging.info(f"✅ Validação aprovada: {len(dados)} eventos de mercado estão íntegros e estruturados.")
    return True
