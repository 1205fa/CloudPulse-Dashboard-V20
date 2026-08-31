import streamlit as st
import boto3

# Configuração da página
st.set_page_config(page_title="CloudPulse AI", page_icon="🤖")
st.title("🤖 Chat - CloudPulse AI")

# Conecta com a AWS usando as chaves blindadas contra espaços invisíveis
bedrock = boto3.client(
    service_name="bedrock-runtime", 
    region_name="us-east-2",
    
    
)

# Cria um histórico de mensagens na memória
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra as mensagens antigas na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de texto para você digitar
if prompt := st.chat_input("Pergunte algo para a IA..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chama a AWS Bedrock usando a API moderna Converse
    with st.chat_message("assistant"):
        mensagem_carregando = st.empty()
        mensagem_carregando.markdown("Pensando...")
        
        try:
            # Prepara o histórico no formato exigido pela API Converse
            mensagens_formatadas = []
            for m in st.session_state.messages:
                mensagens_formatadas.append({
                    "role": m["role"],
                    "content": [{"text": m["content"]}]
                })
            
            resposta_aws = bedrock.converse(
                modelId="amazon.nova-lite-v1:0",
                messages=mensagens_formatadas,
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0.7
                }
            )
            
            texto_ia = resposta_aws["output"]["message"]["content"][0]["text"]
            
            mensagem_carregando.markdown(texto_ia)
            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
            
        except Exception as e:
            mensagem_carregando.markdown(f"**Erro de conexão com a AWS:** {e}")
