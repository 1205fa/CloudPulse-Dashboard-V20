import streamlit as st


def mostrar_cards(metricas):

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "📊 Campanhas",
            metricas["total"]
        )

    with c2:
        st.metric(
            "🏢 Empresas",
            metricas["empresas"]
        )

    with c3:
        st.metric(
            "👑 Líder",
            metricas["lider"]
        )
