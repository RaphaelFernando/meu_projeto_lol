def exibir_partidas(estatisticas):
    print("\n--- Estatísticas das 5 Últimas Partidas ---")
    print(estatisticas)
    for i, partida in enumerate(estatisticas, 1):
        print(f"\nPartida {i}:")
        print(f"Campeão: {partida['champion']}")
        print(f"Lane: {partida['lane']}")
        print(f"Kills / Deaths / Assists: {partida['kills']} / {partida['deaths']} / {partida['assists']}")
        print(f"Tempo de jogo: {partida['duration']} min")
        print(f"Resultado: {'Vitória' if partida['win'] else 'Derrota'}")
        print(f"Modo de Jogo: {partida['game_mode']}")

def exibir_medias(medias):
    print("\n=== MÉDIAS GERAIS ===")
    print(f"{'Kills':<20}: {medias['media_kills']}")
    print(f"{'Deaths':<20}: {medias['media_deaths']}")
    print(f"{'Assists':<20}: {medias['media_assists']}")
    print(f"{'KDA Médio':<20}: {medias['media_kda']}")
    print(f"{'Winrate':<20}: {medias['vitorias']} vitórias em 5 ({medias['winrate']}%)")
    print(f"{'Duração média':<20}: {medias['tempo_medio']} minutos")
    print(f"{'Mais jogado':<20}: {medias['campeao_mais_usado']}")