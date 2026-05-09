import unittest

from match_service import get_player_stats_from_match
from rank_service import _normalize_entries


class GetPlayerStatsFromMatchTest(unittest.TestCase):
    def test_extrai_estatisticas_do_participante_pelo_puuid(self):
        match_data = {
            "info": {
                "gameDuration": 1860,
                "gameMode": "CLASSIC",
                "participants": [
                    {
                        "puuid": "outro-puuid",
                        "championName": "Lux",
                    },
                    {
                        "puuid": "meu-puuid",
                        "championName": "Ahri",
                        "lane": "MIDDLE",
                        "kills": 8,
                        "deaths": 3,
                        "assists": 11,
                        "win": True,
                        "summonerId": "encrypted-id",
                        "summonerName": "Jogador",
                    },
                ],
            }
        }

        resultado = get_player_stats_from_match(match_data, "meu-puuid")

        self.assertEqual(
            resultado,
            {
                "champion": "Ahri",
                "lane": "MIDDLE",
                "kills": 8,
                "deaths": 3,
                "assists": 11,
                "win": True,
                "duration": 31,
                "game_mode": "CLASSIC",
                "role": None,
                "summonerId": "encrypted-id",
                "summonerName": "Jogador",
            },
        )

    def test_retorna_none_quando_participante_nao_existe(self):
        match_data = {
            "info": {
                "participants": [
                    {
                        "puuid": "outro-puuid",
                        "championName": "Lux",
                    }
                ]
            }
        }

        self.assertIsNone(get_player_stats_from_match(match_data, "meu-puuid"))

    def test_retorna_none_para_payload_invalido(self):
        self.assertIsNone(get_player_stats_from_match({}, "meu-puuid"))


class NormalizeEntriesTest(unittest.TestCase):
    def test_normaliza_filas_rankeadas_por_queue_type(self):
        resultado = _normalize_entries(
            [
                {
                    "queueType": "RANKED_SOLO_5x5",
                    "tier": "GOLD",
                    "rank": "II",
                    "leaguePoints": 45,
                    "wins": 10,
                    "losses": 5,
                }
            ]
        )

        self.assertEqual(
            resultado["RANKED_SOLO_5x5"],
            {
                "tier": "GOLD",
                "rank": "II",
                "lp": 45,
                "wins": 10,
                "losses": 5,
                "winrate": 66.7,
            },
        )


if __name__ == "__main__":
    unittest.main()
