from api_handler import get_summoner_info

def main():
    print("=== Analisador de Desempenho - League of Legends ===")
    summoner_name = input("Digite o nome do invocador: ")

    # Chama a função para buscar os dados da Riot
    data = get_summoner_info(summoner_name)

    if data:
        print("\nDados encontrados:")
        print(f"Nome: {data['name']}")
        print(f"Nível: {data['summonerLevel']}")
        print(f"ID do Invocador: {data['id']}")
    else:
        print("Não foi possível encontrar o invocador. Verifique o nome e tente novamente.")

if __name__ == "__main__":
    main()