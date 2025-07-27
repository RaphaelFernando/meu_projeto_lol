import requests
from config import RIOT_API_KEY

# Regiões específicas para cada API
SUMMONER_REGION = "br1"
ACCOUNT_REGION = "americas"
MATCH_REGION = "americas"

#Consulta a conta Riot usando Riot ID (ex: Mugetsu#Luar)
def get_account_by_riot_id(game_name, tag_line):
    url = f"https://{ACCOUNT_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[Account] Erro {response.status_code} - {response.text}")
        return None


#Consulta dados de invocador pelo nome visível (caso queira usar no futuro)
def get_summoner_by_name(summoner_name):
    url = f"https://{SUMMONER_REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[Summoner] Erro {response.status_code} - {response.text}")
        return None


#Busca os últimos IDs de partidas com base no PUUID
def get_match_ids_by_puuid(puuid, count=5):
    """
    Retorna os últimos IDs de partidas de um jogador, com base no PUUID.
    """
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    params = {"start": 0, "count": count}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[Match IDs] Erro {response.status_code} - {response.text}")
        return None
    
# Consulta os detalhes de uma partida específica pelo ID
def get_match_details(match_id):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[Match Details] Erro {response.status_code} - {response.text}")
        return None
    
# Extrai as estatísticas do jogador a partir dos dados da partida
    
def get_player_stats_from_match(match_data, puuid):
    try:
        info = match_data["info"]
        participants = info["participants"]
        game_duration = info["gameDuration"] // 60
        game_mode = info["gameMode"]

        for p in participants:
            if p["puuid"] == puuid:
                return {
                    "champion": p["championName"],
                    "lane": p["lane"],
                    "kills": p["kills"],
                    "deaths": p["deaths"],
                    "assists": p["assists"],
                    "win": p["win"],
                    "duration": game_duration,
                    "game_mode": game_mode
                }
    except Exception as e:
        print(f"[Match Parse] Erro ao extrair dados do jogador: {e}")
        return None

def get_last_matches_stats(puuid, count=20):
    match_ids = get_match_ids_by_puuid(puuid, count=count)
    stats = []

    if match_ids:
        for match_id in match_ids:
            match_data = get_match_details(match_id)
            if match_data:
                player_stats = get_player_stats_from_match(match_data, puuid)
                if player_stats:
                    stats.append(player_stats)
    return stats

def calcular_medias(stats):
    """
    Calcula médias de desempenho com base nas partidas.
    """
    if not stats:
        print("Nenhuma estatística disponível para calcular médias.")
        return {}

    total_kills = sum(s["kills"] for s in stats)
    total_deaths = sum(s["deaths"] for s in stats)
    total_assists = sum(s["assists"] for s in stats)
    total_duration = sum(s["duration"] for s in stats)
    total_wins = sum(1 for s in stats if s["win"])

    count = len(stats)
    medias = {
        "kills": total_kills / count,
        "deaths": total_deaths / count,
        "assists": total_assists / count,
        "duration": total_duration / count,
        "taxa_vitorias (%)": (total_wins / count) * 100
    }
    return medias