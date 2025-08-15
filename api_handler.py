import requests
from typing import Dict, Tuple, Optional
from config import RIOT_API_KEY

# ===== Rotas / Regiões =====
ACCOUNT_REGION = "americas"
MATCH_REGION = "americas"

# Plataformas para Summoner/League
PLATFORMS: Dict[str, str] = {
    "BR1 (Brazil)": "br1",
    "NA1 (North America)": "na1",
    "EUW1 (Europe West)": "euw1",
    "EUN1 (Europe Nordic & East)": "eun1",
    "LA1 (LAN)": "la1",
    "LA2 (LAS)": "la2",
    "KR (Korea)": "kr",
    "OC1 (Oceania)": "oc1",
    "TR1 (Turkey)": "tr1",
    "RU (Russia)": "ru",
    "JP1 (Japan)": "jp1",
}
DEFAULT_PLATFORM = "br1"


def _headers():
    return {"X-Riot-Token": RIOT_API_KEY}


# ===== Account (Riot ID -> PUUID) =====
def get_account_by_riot_id(game_name: str, tag_line: str):
    url = f"https://{ACCOUNT_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"[Account] {r.status_code} - {r.text}")
    return None


# ===== Summoner (PUUID -> encryptedSummonerId) =====
# Mantido apenas por compatibilidade; pode vir filtrado sem 'id' em algumas chaves.
def get_summoner_by_puuid(puuid: str, platform: str = DEFAULT_PLATFORM):
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict) and "id" in data:
            return data
        print(f"[Summoner by PUUID] Sem 'id' (platform={platform}): {data}")
        return None
    print(f"[Summoner by PUUID] {r.status_code} - {r.text}")
    return None


def get_summoner_by_name(summoner_name: str, platform: str = DEFAULT_PLATFORM):
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"[Summoner] {r.status_code} - {r.text}")
    return None


# ===== Match-V5 =====
def get_match_ids_by_puuid(puuid: str, count: int = 5):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    r = requests.get(url, headers=_headers(), params=params, timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"[Match IDs] {r.status_code} - {r.text}")
    return None


def get_match_details(match_id: str):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"[Match Details] {r.status_code} - {r.text}")
    return None


def get_player_stats_from_match(match_data: dict, puuid: str):
    """Extrai estatísticas + summonerId/summonerName do participante do PUUID."""
    try:
        info = match_data["info"]
        participants = info["participants"]
        game_duration = info.get("gameDuration", 0) // 60
        game_mode = info.get("gameMode", "")
        for p in participants:
            if p.get("puuid") == puuid:
                return {
                    "champion": p.get("championName"),
                    "lane": p.get("lane"),
                    "kills": p.get("kills", 0),
                    "deaths": p.get("deaths", 0),
                    "assists": p.get("assists", 0),
                    "win": p.get("win", False),
                    "duration": game_duration,
                    "game_mode": game_mode,
                    "summonerId": p.get("summonerId"),
                    "summonerName": p.get("summonerName"),
                }
    except Exception as e:
        print(f"[Match Parse] erro: {e}")
    return None


def get_last_matches_stats(puuid: str, count: int = 20):
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


# ===== Pegar encryptedSummonerId e plataforma sugerida a partir do último match =====
def get_encrypted_summoner_id_and_platform_hint(puuid: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Busca 1 partida recente e retorna:
      - 'summonerId' do jogador (encryptedSummonerId)
      - plataforma sugerida, extraída do prefixo do matchId (ex.: BR1_ -> 'br1')
    """
    ids = get_match_ids_by_puuid(puuid, count=1)
    if not ids:
        return None, None
    match_id = ids[0]  # ex.: "BR1_123456789"
    platform_hint = None
    try:
        prefix = match_id.split("_", 1)[0].lower()  # "br1"
        platform_hint = prefix
    except Exception:
        platform_hint = None

    details = get_match_details(match_id)
    if not details:
        return None, platform_hint
    me = get_player_stats_from_match(details, puuid)
    enc_id = me.get("summonerId") if me else None
    return enc_id, platform_hint


# ===== League-V4 =====
def _normalize_entries(raw_list) -> Dict[str, dict]:
    result = {}
    for q in raw_list:
        queue = q.get("queueType")
        wins = q.get("wins", 0)
        losses = q.get("losses", 0)
        total = max(1, wins + losses)
        winrate = round((wins / total) * 100, 1)
        result[queue] = {
            "tier": q.get("tier", "UNRANKED"),
            "rank": q.get("rank", ""),
            "lp": q.get("leaguePoints", 0),
            "wins": wins,
            "losses": losses,
            "winrate": winrate,
        }
    return result


def get_ranked_entries_raw(encrypted_summoner_id: str, platform: str) -> Tuple[Dict[str, dict], int]:
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code == 200:
        return _normalize_entries(r.json()), 200
    print(f"[League Entries] {r.status_code} - {r.text}")
    return {}, r.status_code


def get_ranked_entries(encrypted_summoner_id: str, platform: str = DEFAULT_PLATFORM) -> Dict[str, dict]:
    entries, status = get_ranked_entries_raw(encrypted_summoner_id, platform)
    return entries if status == 200 else {}


def find_platform_for_puuid(puuid: str):
    """(mantido) tenta achar plataforma via summoner/by-puuid."""
    for plat in PLATFORMS.values():
        summ = get_summoner_by_puuid(puuid, platform=plat)
        if summ and isinstance(summ, dict) and "id" in summ:
            return plat, summ
    return None, None


def find_platform_by_summoner_id(encrypted_summoner_id: str, preferred: Optional[str] = None):
    """
    Prioriza 'preferred' (ex.: 'br1'), depois varre todas.
    Critério: primeira plataforma com HTTP 200 e entries NÃO vazias.
    Fallback: primeira plataforma com HTTP 200 (mesmo {}).
    """
    platforms = list(PLATFORMS.values())
    if preferred and preferred in platforms:
        platforms.remove(preferred)
        platforms = [preferred] + platforms

    first_ok_platform = None
    first_ok_entries: Dict[str, dict] = {}

    for plat in platforms:
        entries, status = get_ranked_entries_raw(encrypted_summoner_id, plat)
        if status == 200:
            if first_ok_platform is None:
                first_ok_platform, first_ok_entries = plat, entries
            if len(entries.keys()) > 0:
                return plat, entries

    if first_ok_platform is not None:
        return first_ok_platform, first_ok_entries

    return None, {}


# ===== Diagnóstico (opcional) =====
def probe_rank_across_platforms(puuid: str, game_name: str):
    results = {}
    for plat in PLATFORMS.values():
        summary = {"summoner_ok": False, "has_id": False, "entries_len": 0, "status": ""}
        try:
            summ = get_summoner_by_puuid(puuid, platform=plat)
            if summ:
                summary["summoner_ok"] = True
                summary["has_id"] = "id" in summ
                if "id" in summ:
                    entries = get_ranked_entries(summ["id"], platform=plat)
                    summary["entries_len"] = len(entries.keys())
                    summary["status"] = "ok"
                else:
                    summary["status"] = "summoner sem 'id'"
            else:
                summary["status"] = "summoner não encontrado"
        except Exception as e:
            summary["status"] = f"erro: {e}"
        results[plat] = summary
    return results