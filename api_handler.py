import requests

# Chave da API
from config import RIOT_API_KEY

# Região base da API
REGIAO = "br1"

def get_summoner_info(summoner_name):
    """
    Retorna os dados básicos do invocador a partir do nome.
    """
    url = f"https://{REGIAO}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"

    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao acessar a API: {response.status_code} - {response.text}")
        return None
