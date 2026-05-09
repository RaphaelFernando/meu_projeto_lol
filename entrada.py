def solicitar_riot_id():
    game_name = input(
        "=== Consulta de Desempenho no League of Legends ===\n\n"
        "Digite o nome do Riot ID (ex: Mugetsu): "
    ).strip()
    tag = input("Digite a tag do Riot ID (ex: Luar): ").strip()
    return game_name, tag
