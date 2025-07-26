from api_handler import (
    get_account_by_riot_id,
    get_match_ids_by_puuid,
    get_match_details
)

def main():
    print("=== Consulta de Desempenho no League of Legends ===\n")

    # Entrada do Riot ID
    game_name = input("Digite o nome do Riot ID (ex: Mugetsu): ")
    tag = input("Digite a tag do Riot ID (ex: Luar): ")

    # Consulta da conta Riot (PUUID)
    conta = get_account_by_riot_id(game_name, tag)

    if conta:
        puuid = conta["puuid"]
        print(f"\nPUUID encontrado: {puuid}")

        # Busca os últimos 5 match IDs
        match_ids = get_match_ids_by_puuid(puuid, count=5)

        if match_ids:
            print("\n--- Últimas Partidas ---")
            for i, match_id in enumerate(match_ids, 1):
                print(f"{i}. {match_id}")

            # Consulta os detalhes da partida mais recente
            print("\n--- Estatísticas da Última Partida ---")
            match_data = get_match_details(match_ids[0])  # Pega a mais recente

            if match_data:
                info = match_data['info']
                game_duration = info['gameDuration'] // 60
                game_mode = info['gameMode']
                participants = info['participants']

                print(f"Modo: {game_mode}")
                print(f"Duração: {game_duration} minutos\n")

                # Busca os dados do jogador na partida
                for p in participants:
                    if p['puuid'] == puuid:
                        print(">>> Estatísticas do Jogador:")
                        print(f"Campeão: {p['championName']}")
                        print(f"Lane: {p['lane']}")
                        print(f"Kills / Deaths / Assists: {p['kills']} / {p['deaths']} / {p['assists']}")
                        print(f"Resultado: {'Vitória' if p['win'] else 'Derrota'}")
                        break
            else:
                print("Não foi possível obter os detalhes da partida.")
        else:
            print("Não foi possível obter os IDs das partidas.")
    else:
        print("Conta Riot não encontrada.")

if __name__ == "__main__":
    main()
