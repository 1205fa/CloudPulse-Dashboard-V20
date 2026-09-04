class CorrectionAgent:
    def executar(self, dados, relatorio_gerado):
        avisos = []
        
        # Regra de Validação 1: Funil Fechado vs Campanhas
        if dados.get("promocoes") and not dados.get("precos"):
            avisos.append("⚠️ ALERTA DE FUNIL FECHADO: O concorrente possui campanhas ativas de captação, mas esconde os preços no site. Recomenda-se acionar time de Cliente Oculto.")
            
        # Regra de Validação 2: Dados Vazios (Blindagem contra falhas)
        if not dados.get("cursos"):
            avisos.append("⚠️ AVISO DE QUALIDADE: Nenhum curso foi detectado no rastreio atual. Possível mudança no layout do site alvo.")
            
        # Anexa a auditoria ao final do relatório se houver avisos
        if avisos:
            relatorio_gerado += "\n### 🛡️ AUDITORIA DO AGENTE DE CORREÇÃO (Self-Correction)\n"
            for aviso in avisos:
                relatorio_gerado += f"- {aviso}\n"
                
        return relatorio_gerado
