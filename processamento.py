from collections import Counter

def calcular_estatisticas(partidas):
    total_kills = total_deaths = total_assists = total_duration = vitorias = 0
    campeoes = []

    for p in partidas:
        total_kills += p['kills']
        total_deaths += p['deaths']
        total_assists += p['assists']
        total_duration += p['duration'] * 60
        if p['win']:
            vitorias += 1
        campeoes.append(p['champion'])

    num_partidas = len(partidas)
    media_kills = total_kills / num_partidas
    media_deaths = total_deaths / num_partidas
    media_assists = total_assists / num_partidas
    media_kda = (total_kills + total_assists) / max(1, total_deaths)
    tempo_medio = total_duration // num_partidas // 60
    campeao_mais_usado = Counter(campeoes).most_common(1)[0][0]

    return {
        "media_kills": round(media_kills, 2),
        "media_deaths": round(media_deaths, 2),
        "media_assists": round(media_assists, 2),
        "media_kda": round(media_kda, 2),
        "vitorias": vitorias,
        "winrate": round((vitorias / num_partidas) * 100, 1),
        "tempo_medio": tempo_medio,
        "campeao_mais_usado": campeao_mais_usado
    }