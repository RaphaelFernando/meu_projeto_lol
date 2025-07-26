from api_handler import (
    get_account_by_riot_id,
    get_last_matches_stats,
    calcular_medias
)
from graficos import plot_kda_bar, plot_resultados_pizza

def main():
    print("=== Consulta de Desempenho no League of Legends ===\n")

    # Entrada do Riot ID
    game_name = input("Digite o nome do Riot ID (ex: Mugetsu): ").strip()
    tag = input("Digite a tag do Riot ID (ex: Luar): ").strip()

    # Consulta da conta Riot (PUUID)
    conta = get_account_by_riot_id(game_name, tag)

    if conta:
        puuid = conta["puuid"]
        print(f"\nPUUID encontrado: {puuid}")

        # Coleta e exibe estatísticas das partidas
        print("\n--- Estatísticas das 5 Últimas Partidas ---")
        estatisticas = get_last_matches_stats(puuid)

        if estatisticas:
            for i, partida in enumerate(estatisticas, 1):
                print(f"\nPartida {i}:")
                print(f"Campeão: {partida['champion']}")
                print(f"Lane: {partida['lane']}")
                print(f"Kills / Deaths / Assists: {partida['kills']} / {partida['deaths']} / {partida['assists']}")
                print(f"Tempo de jogo: {partida['duration']} min")
                print(f"Resultado: {'Vitória' if partida['win'] else 'Derrota'}")
                print(f"Modo de Jogo: {partida['game_mode']}")
        else:
            print("Não foi possível obter estatísticas das partidas.")
    else:
        print("Conta Riot não encontrada.")
    # Exibe as médias após mostrar as 5 partidas
    medias = calcular_medias(estatisticas)
    print("\n=== MÉDIAS GERAIS ===")
    for chave, valor in medias.items():
        if "duration" in chave:
            print(f"- {chave.capitalize()}: {valor:.1f} min")
        elif "%" in chave:
            print(f"- {chave}: {valor:.1f}%")
        else:
            print(f"- {chave.capitalize()}: {valor:.1f}")
    print("\n=== VISUALIZAÇÃO GRÁFICA ===")
    plot_kda_bar(estatisticas)
    plot_resultados_pizza(estatisticas)

if __name__ == "__main__":
    main()