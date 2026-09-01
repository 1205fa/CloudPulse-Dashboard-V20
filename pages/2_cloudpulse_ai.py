import streamlit as st
import requests

st.set_page_config(page_title="I.A.BI. MAGO", page_icon="🧙‍♂️", layout="wide")

st.title("🤖 I.A.BI. MAGO")
st.markdown("Seu Agente de Inteligência Competitiva. Pergunte qualquer coisa sobre o mercado!")

# Inicializa o histórico de chat na memória do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Desenha as mensagens anteriores na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de texto estilo ChatGPT
if prompt := st.chat_input("Digite seu comando (ex: Quais as maiores ameaças do mercado?)..."):
    
    # Salva e mostra a pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chama a nossa API do Mago
    with st.chat_message("assistant"):
        with st.spinner("Analisando cenário competitivo..."):
            try:
                # Envia o histórico inteiro para o backend
                resposta = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"mensagens": st.session_state.messages}
                )
                
                if resposta.status_code == 200:
                    texto_ia = resposta.json().get("resposta", "Erro ao decodificar a resposta.")
                    st.markdown(texto_ia)
                    # Salva a resposta na memória
                    st.session_state.messages.append({"role": "assistant", "content": texto_ia})
                else:
                    st.error(f"Erro na API do Mago: {resposta.text}")
                    
            except Exception as e:
                st.error("O servidor do Mago (Backend) parece estar desligado. Deixe o Uvicorn rodando no terminal!")
