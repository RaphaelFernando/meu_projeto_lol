import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riot import riot_services
from riot.exceptions import (
    RiotApiError,
    RiotAuthenticationError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotServerError,
    RiotTimeoutError,
)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")


def main() -> int:
    """Run a real Riot API smoke test: Riot ID -> PUUID -> Match IDs -> Match Details."""
    game_name = input("gameName: ").strip()
    tag_line = input("tagLine: ").strip()

    if not game_name or not tag_line:
        print("Erro: gameName e tagLine são obrigatórios.")
        return 1

    try:
        print("Validando Account API...")
        print("Validando Match IDs API...")
        print("Validando Summoner API...")
        print("Validando Match Details API...")
        summary = riot_services.get_latest_match_summary(game_name, tag_line, count=5, strict=True)
        if not summary:
            print("Erro: não foi possível montar o resumo para este Riot ID.")
            return 1

        puuid = summary["puuid"]
        match_ids = summary["match_ids"]
        if not match_ids:
            print("Nenhuma partida encontrada para este PUUID.")
            return 1

        first_match_id = summary["match_id"]
        summoner = summary["summoner"]
        participant = summary["participant"]
        if not participant:
            print("Erro: participante do PUUID não encontrado na primeira partida.")
            return 1

        result = "win" if participant["win"] else "loss"

        print("\nSMOKE TEST RIOT API OK")
        print(f"Riot ID: {summary['riot_id']}")
        print(f"PUUID: {_mask_puuid(puuid)}")
        print(f"Summoner Level: {summoner.get('summonerLevel', 'N/A') if summoner else 'N/A'}")
        print(f"Quantidade de partidas encontradas: {len(match_ids)}")
        print(f"Match ID da primeira partida: {first_match_id}")
        print(f"Champion: {participant['champion']}")
        print(f"K/D/A: {participant['kills']}/{participant['deaths']}/{participant['assists']}")
        print(f"Resultado: {result}")
        print("\nEndpoints OK:")
        print("- account-v1 /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}")
        print("- match-v5 /lol/match/v5/matches/by-puuid/{puuid}/ids")
        print("- summoner-v4 /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}")
        print("- match-v5 /lol/match/v5/matches/{matchId}")
        return 0

    except RiotAuthenticationError:
        print("Erro 401: API key ausente, inválida ou expirada. Verifique RIOT_API_KEY no .env.")
    except RiotForbiddenError:
        print("Erro 403: acesso negado. A chave Riot pode estar expirada ou sem permissão.")
    except RiotNotFoundError:
        print("Erro 404: Riot ID, PUUID, summoner ou partida não encontrado.")
    except RiotRateLimitError:
        print("Erro 429: rate limit atingido. Aguarde e tente novamente.")
    except RiotTimeoutError:
        print("Erro de timeout: a Riot API não respondeu dentro do tempo limite.")
    except RiotServerError:
        print("Erro 500+: falha temporária da Riot API. Tente novamente mais tarde.")
    except RiotApiError as exc:
        print(f"Erro Riot API: {exc}")
    except KeyError as exc:
        print(f"Resposta inesperada da Riot API. Campo ausente: {exc}")

    return 1


def _mask_puuid(puuid: str) -> str:
    if len(puuid) <= 12:
        return "***"
    return f"{puuid[:6]}...{puuid[-6:]}"


if __name__ == "__main__":
    raise SystemExit(main())
