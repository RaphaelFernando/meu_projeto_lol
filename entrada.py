def solicitar_riot_id():
    print("=== Consulta de Desempenho no League of Legends ===\n")
    game_name = input("Digite o nome do Riot ID (ex: Mugetsu): ").strip()
    tag = input("Digite a tag do Riot ID (ex: Luar): ").strip()
    return game_name, tag