from backend.agents.supervisor import SupervisorAgent

class CloudPulseOrchestrator:
    """
    Orquestrador Enterprise do CloudPulse.
    Delega a execução da pesquisa em tempo real para o Supervisor.
    """
    def __init__(self):
        self.supervisor = SupervisorAgent()

    def executar(self, empresa):
        # O Orquestrador apenas coordena o fluxo, passando a missão para o Supervisor
        relatorio_final = self.supervisor.executar(empresa)
        return relatorio_final
