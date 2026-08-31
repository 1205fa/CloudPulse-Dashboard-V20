import pandas as pd
import streamlit as st


def grafico_empresas(metricas):

    if not metricas["ranking"]:
        st.warning("Nenhum dado encontrado.")
        return

    df = pd.DataFrame(
        metricas["ranking"],
        columns=[
            "Empresa",
            "Campanhas"
        ]
    )

    st.subheader("📈 Campanhas por Empresa")

    st.bar_chart(
        df.set_index("Empresa")
    )
