import requests
from config import RIOT_API_KEY

# Endpoints por região
SUMMONER_REGION = "br1"
ACCOUNT_REGION = "americas"

def get_summoner_by_name(summoner_name):
    """
    Busca os dados de invocador pelo nome (ex: Mugetsu)
    """
    url = f"https://{SUMMONER_REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[Summoner] Erro {response.status_code} - {response.text}")
        return None


def get_account_by_riot_id(game_name, tag_line):
    """
    Busca os dados da conta Riot usando o Riot ID (ex: Mugetsu#Luar)
    """
    url = f"https://{ACCOUNT_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[Account] Erro {response.status_code} - {response.text}")
        return None
