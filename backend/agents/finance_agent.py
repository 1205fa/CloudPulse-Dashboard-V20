class FinanceAgent:
    def executar(self, dados):
        return {
            "precos": dados.get("precos", []),
            "promocoes": dados.get("promocoes", [])
        }
