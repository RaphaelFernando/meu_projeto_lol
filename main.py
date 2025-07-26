from entrada import solicitar_riot_id
from api_handler import get_account_by_riot_id, get_last_matches_stats
from processamento import calcular_estatisticas
from exibicao import exibir_partidas, exibir_medias
from graficos import plot_kda_bar, plot_resultados_pizza

def main():
    game_name, tag = solicitar_riot_id()
    conta = get_account_by_riot_id(game_name, tag)

    if not conta:
        print("Conta Riot não encontrada.")
        return

    puuid = conta["puuid"]
    print(f"\nPUUID encontrado: {puuid}")
    estatisticas = get_last_matches_stats(puuid)

    if not estatisticas:
        print("Não foi possível obter estatísticas.")
        return

    exibir_partidas(estatisticas)
    medias = calcular_estatisticas(estatisticas)
    exibir_medias(medias)
    print("\n=== VISUALIZAÇÃO GRÁFICA ===")
    plot_kda_bar(estatisticas)
    plot_resultados_pizza(estatisticas)

if __name__ == "__main__":
    main()