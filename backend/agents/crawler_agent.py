from backend.discovery import buscar_empresa

class CrawlerAgent:
    def executar(self, empresa):
        return buscar_empresa(empresa)
