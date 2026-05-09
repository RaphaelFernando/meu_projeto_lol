import unittest
from unittest.mock import patch

from riot.rate_limiter import RiotRateLimiter
from riot.riot_client import RiotClient
from riot.riot_services import (
    get_latest_match_summary,
    get_match,
    get_ranked_entries_by_puuid,
    get_recent_match_summaries,
    get_summoner_by_puuid,
)


class FakeResponse:
    def __init__(self, status_code, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.last_url = None

    def get(self, url, headers=None, params=None, timeout=None):
        self.last_url = url
        return self.responses.pop(0)


def _match_payload(puuid, champion, win, kills, deaths, assists, duration, queue_id):
    return {
        "info": {
            "gameDuration": duration,
            "gameCreation": 1710000000000,
            "gameMode": "CLASSIC",
            "queueId": queue_id,
            "participants": [
                {
                    "puuid": puuid,
                    "championName": champion,
                    "lane": "MIDDLE",
                    "role": "SOLO",
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "win": win,
                }
            ],
        }
    }


class RiotServicesTest(unittest.TestCase):
    def test_get_match_busca_partida_por_id(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(200, {"metadata": {"matchId": "BR1_123"}})]),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_match("BR1_123", client=client)

        self.assertEqual(resultado["metadata"]["matchId"], "BR1_123")

    def test_get_summoner_by_puuid_retorna_summoner_com_id(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(200, {"id": "encrypted-id", "puuid": "puuid"})]),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_summoner_by_puuid("puuid", client=client)

        self.assertEqual(resultado["id"], "encrypted-id")

    def test_get_summoner_by_puuid_preserva_payload_sem_id(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(200, {"puuid": "puuid", "summonerLevel": 145})]),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_summoner_by_puuid("puuid", client=client)

        self.assertEqual(resultado["summonerLevel"], 145)

    def test_get_latest_match_summary_monta_resumo_da_partida(self):
        client = RiotClient(
            session=FakeSession(
                [
                    FakeResponse(200, {"puuid": "puuid"}),
                    FakeResponse(200, ["BR1_123"]),
                    FakeResponse(200, {"puuid": "puuid", "summonerLevel": 145}),
                    FakeResponse(
                        200,
                        {
                            "info": {
                                "gameDuration": 1800,
                                "gameMode": "CLASSIC",
                                "participants": [
                                    {
                                        "puuid": "puuid",
                                        "championName": "Diana",
                                        "lane": "JUNGLE",
                                        "kills": 9,
                                        "deaths": 12,
                                        "assists": 13,
                                        "win": False,
                                    }
                                ],
                            }
                        },
                    ),
                ]
            ),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_latest_match_summary("Mugetsu", "Luar", client=client, strict=True)

        self.assertEqual(resultado["riot_id"], "Mugetsu#Luar")
        self.assertEqual(resultado["summoner"]["summonerLevel"], 145)
        self.assertEqual(resultado["match_id"], "BR1_123")
        self.assertEqual(resultado["participant"]["champion"], "Diana")

    def test_get_latest_match_summary_retorna_sem_partidas(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(200, {"puuid": "puuid"}), FakeResponse(200, [])]),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_latest_match_summary("Mugetsu", "Luar", client=client, strict=True)

        self.assertEqual(resultado["match_ids"], [])
        self.assertIsNone(resultado["participant"])

    def test_get_ranked_entries_by_puuid_usa_endpoint_por_puuid(self):
        session = FakeSession(
            [
                FakeResponse(
                    200,
                    [
                        {
                            "queueType": "RANKED_SOLO_5x5",
                            "tier": "GOLD",
                            "rank": "II",
                            "leaguePoints": 45,
                            "wins": 10,
                            "losses": 5,
                        }
                    ],
                )
            ]
        )
        client = RiotClient(session=session, rate_limiter=RiotRateLimiter())

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_ranked_entries_by_puuid("puuid", platform="br1", client=client)

        self.assertIn("/lol/league/v4/entries/by-puuid/puuid", session.last_url)
        self.assertEqual(resultado["RANKED_SOLO_5x5"]["winrate"], 66.7)

    def test_get_recent_match_summaries_retorna_multiplas_partidas(self):
        client = RiotClient(
            session=FakeSession(
                [
                    FakeResponse(200, {"puuid": "puuid"}),
                    FakeResponse(200, ["BR1_1", "BR1_2"]),
                    FakeResponse(200, _match_payload("puuid", "Ahri", True, 7, 2, 9, 1800, 420)),
                    FakeResponse(200, _match_payload("puuid", "Diana", False, 4, 6, 8, 1500, 440)),
                ]
            ),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_recent_match_summaries("Mugetsu", "Luar", count=2, client=client)

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]["match_id"], "BR1_1")
        self.assertEqual(resultado[0]["champion"], "Ahri")
        self.assertEqual(resultado[1]["queue_id"], 440)

    def test_get_recent_match_summaries_continua_quando_partida_falha(self):
        client = RiotClient(
            session=FakeSession(
                [
                    FakeResponse(200, {"puuid": "puuid"}),
                    FakeResponse(200, ["BR1_1", "BR1_2"]),
                    FakeResponse(404),
                    FakeResponse(200, _match_payload("puuid", "Diana", False, 4, 6, 8, 1500, 440)),
                ]
            ),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_recent_match_summaries("Mugetsu", "Luar", count=2, client=client)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["match_id"], "BR1_2")
        self.assertEqual(resultado[0]["failed_count"], 1)

    def test_get_recent_match_summaries_retorna_lista_vazia(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(200, {"puuid": "puuid"}), FakeResponse(200, [])]),
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            resultado = get_recent_match_summaries("Mugetsu", "Luar", count=2, client=client)

        self.assertEqual(resultado, [])


if __name__ == "__main__":
    unittest.main()
