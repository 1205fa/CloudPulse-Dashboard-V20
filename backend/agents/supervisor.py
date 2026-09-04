from backend.agents.crawler_agent import CrawlerAgent
from backend.agents.finance_agent import FinanceAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.self_correction_agent import SelfCorrectionAgent

class SupervisorAgent:
    def __init__(self):
        # Instanciando a equipe de agentes no construtor
        self.crawler = CrawlerAgent()
        self.financeiro = FinanceAgent()
        self.report_agent = ReportAgent()
        self.validator = SelfCorrectionAgent()

    def executar(self, empresa):
        # 1. Busca
        dados = self.crawler.executar(empresa)

        # 2. Financeiro
        dados_financeiros = self.financeiro.executar(dados)
        dados.update(dados_financeiros)

        # 3. Relatório
        relatorio = self.report_agent.executar(dados)
        
        # 4. Validação (Self-Correction)
        relatorio = self.validator.validar(relatorio)

        return relatorio
