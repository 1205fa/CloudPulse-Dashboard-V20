import json

def iniciar_buscador():
    print("\n==================================")
    print(" ☁️  CLOUDPULSE SEARCH ENGINE ☁️")
    print("==================================\n")

    try:
        with open("banco_cloudpulse.json", "r", encoding="utf-8") as f:
            eventos = json.load(f)
    except FileNotFoundError:
        print("❌ Banco de dados não encontrado.")
        return

    while True:
        pesquisa = input("🔎 Pesquisar (ou 'sair' para encerrar): ").strip()
        
        if pesquisa.lower() == 'sair':
            print("Encerrando CloudPulse Search...\n")
            break
            
        print("-" * 34)
        encontrados = []
        
        for item in eventos:
            if pesquisa.lower() in item["titulo"].lower():
                encontrados.append(item)
                
        if encontrados:
            print(f"✅ Encontrados {len(encontrados)} resultados para '{pesquisa}':\n")
            for resultado in encontrados:
                print(f"📌 {resultado['titulo']}")
                print(f"   Prioridade: {resultado['prioridade']}")
                print("-" * 34)
        else:
            print(f"❌ Nenhum resultado encontrado para '{pesquisa}'.")
            print("-" * 34)
        print("\n")

if __name__ == "__main__":
    iniciar_buscador()
