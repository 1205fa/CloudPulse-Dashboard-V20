class SelfCorrectionAgent:
    """
    Responsável por validar o relatório antes da entrega.
    """
    def validar(self, relatorio: str) -> str:
        observacoes = []

        if "[]" in relatorio:
            observacoes.append(
                "Alguns campos não possuem informações públicas disponíveis."
            )

        if "None" in relatorio:
            observacoes.append(
                "Foram encontrados valores nulos durante a coleta."
            )

        if "Erro" in relatorio:
            observacoes.append(
                "O relatório contém mensagens de erro que devem ser revisadas."
            )

        if observacoes:
            relatorio += "\n\n### ✅ Validação Automática\n"
            for obs in observacoes:
                relatorio += f"- {obs}\n"
        else:
            relatorio += (
                "\n\n### ✅ Validação Automática\n"
                "- Relatório validado automaticamente.\n"
                "- Nenhuma inconsistência encontrada.\n"
            )

        return relatorio
