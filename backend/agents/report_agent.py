class ReportAgent:
    def executar(self, dados):
        resposta = f"""
### 📊 RELATÓRIO EXECUTIVO
**Empresa:** {dados.get('empresa', 'Não encontrada')}

**📚 Cursos:** 
{dados.get('cursos', [])}

**💰 Preços:** 
{dados.get('precos', [])}

**🎁 Promoções:** 
{dados.get('promocoes', [])}
"""
        return resposta
