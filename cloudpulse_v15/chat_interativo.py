import boto3
import json
from config.settings import AWS_REGION

def iniciar_chat():
    print("\n" + "="*60)
    print("🤖 ASSISTENTE DE INTELIGÊNCIA COMPETITIVA - WIZARD")
    print("Base de dados: Cursos e Campanhas raspadas na V4.")
    print("Digite 'sair' a qualquer momento para encerrar o sistema.")
    print("="*60 + "\n")

    # 1. Carrega os dados coletados pelo seu Agente Scraper
    try:
        with open("data/cursos.json", "r", encoding="utf-8") as f:
            dados_concorrencia = json.load(f)
    except FileNotFoundError:
        print("❌ Erro: O arquivo 'data/cursos.json' não foi encontrado.")
        print("Rode o 'python3 main.py' primeiro para o Scraper capturar os dados!")
        return

    # 2. Prepara a conexão com a AWS (Requer as chaves do Rodrigo ativas)
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    # 3. O Loop Infinito da Conversa
    while True:
        pergunta = input("\n👤 Você (Banca/Diretor): ")
        
        if pergunta.lower() == 'sair':
            print("👋 Encerrando o chat interativo. Excelente apresentação!")
            break
            
        print("🧠 IA analisando os dados extraídos do S3...")
        
        # 4. Monta o cérebro da IA misturando os dados com a pergunta
        prompt = f"""
        Você é um Assistente Sênior de Inteligência Competitiva.
        Sua base de dados de mercado extraída hoje é a seguinte:
        {json.dumps(dados_concorrencia, ensure_ascii=False, indent=2)}
        
        Com base EXCLUSIVAMENTE nesses dados, responda à pergunta do usuário.
        Seja direto, estratégico e profissional.
        
        Pergunta do usuário: {pergunta}
        """

        # 5. Envia a pergunta para o Claude 3 na AWS
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })

            resposta = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0", 
                body=body
            )
            
            response_body = json.loads(resposta.get("body").read())
            texto_ia = response_body["content"][0]["text"]
            
            print(f"\n🤖 Assistente IA Bedrock:\n{texto_ia}")
            
        except Exception as e:
            print("\n❌ AVISO: Falha ao contatar a AWS Bedrock.")
            print("O código está perfeito, mas as credenciais da AWS ainda não foram inseridas no terminal!")
            print(f"Detalhe técnico para o Rodrigo: {e}")

if __name__ == "__main__":
    iniciar_chat()
