from api_handler import get_account_by_riot_id

def main():
    print("=== Consulta de Conta Riot (Riot ID) ===")
    
    game_name = input("Digite o nome do Riot ID (ex: Mugetsu): ")
    tag = input("Digite a tag do Riot ID (ex: Luar): ")
    
    data = get_account_by_riot_id(game_name, tag)
    
    if data:
        print("\n--- Dados da Conta Riot ---")
        print(f"Game Name: {data['gameName']}")
        print(f"Tag Line: {data['tagLine']}")
        print(f"PUUID: {data['puuid']}")
    else:
        print("Conta Riot não encontrada ou erro na requisição.")

if __name__ == "__main__":
    main()
