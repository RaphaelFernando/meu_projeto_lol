import requests

API_KEY = "RGAPI-712c7072-b578-4daf-9516-c972157127c1 "
match_id = "BR1_3120917901"  # Substitua por um matchId real
url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"

headers = {
    "X-Riot-Token": API_KEY
}

response = requests.get(url, headers=headers)
match_data = response.json()

print(match_data)