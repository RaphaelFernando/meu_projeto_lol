import requests
import json
import time
import os

# Sua API KEY da Riot
API_KEY = "RGAPI-712c7072-b578-4daf-9516-c972157127c1"
HEADERS = {"X-Riot-Token": API_KEY}

# Substitua pelos gameIds que você quer buscar
game_ids = [
    "BR1_3120917901",
    "BR1_3120863516",
    "BR1_3120279328",
    "BR1_3120248715",
    "BR1_3120224544",
    ]

# Arquivo de destino
output_file = os.path.join(os.getcwd(), "matches_dump.json")

# Lista para armazenar os resultados
all_matches = []

# Requisição de cada partida
for match_id in game_ids:
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    print(f"🔄 Buscando partida {match_id}...")
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            match_data = response.json()
            all_matches.append(match_data)
        else:
            print(f"⚠ Erro {response.status_code} ao buscar {match_id}")
    except Exception as e:
        print(f"❌ Exceção ao buscar {match_id}: {e}")
    
    time.sleep(1.2)  # Evita rate limit (ajuste se necessário)

# Salvar tudo em um único JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_matches, f, ensure_ascii=False, indent=2)

print(f"\n✅ {len(all_matches)} partidas salvas em: {output_file}")
