import logging
from typing import Any, Dict, Optional, Tuple

from . import endpoints
from .exceptions import RiotApiError, RiotForbiddenError, RiotNotFoundError
from .riot_client import RiotClient, default_client
from .riot_config import DEFAULT_REGION, DEFAULT_ROUTING, PLATFORMS

logger = logging.getLogger(__name__)


def get_account_by_riot_id(
    game_name: str,
    tag_line: str,
    *,
    client: RiotClient = default_client,
    strict: bool = False,
) -> Optional[dict]:
    """Return Riot account data for a Riot ID."""
    url = endpoints.ACCOUNT_BY_RIOT_ID.format(routing=DEFAULT_ROUTING, game_name=game_name, tag_line=tag_line)
    return _safe_get(client, url, label="Account", strict=strict)


def get_summoner_by_puuid(
    puuid: str,
    platform: str = DEFAULT_REGION,
    *,
    client: RiotClient = default_client,
    strict: bool = False,
) -> Optional[dict]:
    """Return summoner data for a PUUID on a platform region."""
    url = endpoints.SUMMONER_BY_PUUID.format(region=platform, puuid=puuid)
    data = _safe_get(client, url, label="Summoner by PUUID", strict=strict)
    if isinstance(data, dict):
        return data
    return None


def get_summoner_by_name(
    summoner_name: str,
    platform: str = DEFAULT_REGION,
    *,
    client: RiotClient = default_client,
) -> Optional[dict]:
    """Compatibility lookup by summoner name for legacy callers."""
    url = endpoints.SUMMONER_BY_NAME.format(region=platform, summoner_name=summoner_name)
    return _safe_get(client, url, label="Summoner by Name")


def get_match_ids_by_puuid(
    puuid: str,
    count: int = 5,
    *,
    start: int = 0,
    client: RiotClient = default_client,
    strict: bool = False,
) -> Optional[list[str]]:
    """Return recent match ids for a PUUID."""
    url = endpoints.MATCH_IDS_BY_PUUID.format(routing=DEFAULT_ROUTING, puuid=puuid)
    params = {"start": start, "count": count}
    return _safe_get(client, url, label="Match IDs", params=params, strict=strict)


def get_match(match_id: str, *, client: RiotClient = default_client, strict: bool = False) -> Optional[dict]:
    """Return match details by match id."""
    url = endpoints.MATCH_BY_ID.format(routing=DEFAULT_ROUTING, match_id=match_id)
    return _safe_get(client, url, label="Match Details", strict=strict)


def get_match_timeline(match_id: str, *, client: RiotClient = default_client) -> Optional[dict]:
    """Return match timeline by match id."""
    url = endpoints.MATCH_TIMELINE_BY_ID.format(routing=DEFAULT_ROUTING, match_id=match_id)
    return _safe_get(client, url, label="Match Timeline")


def get_ranked_entries_by_puuid(
    puuid: str,
    platform: str = DEFAULT_REGION,
    *,
    client: RiotClient = default_client,
) -> Dict[str, dict]:
    """Return normalized ranked entries for a PUUID."""
    url = endpoints.LEAGUE_BY_PUUID.format(region=platform, puuid=puuid)
    try:
        raw_entries = client.get(url, label="League Entries by PUUID")
    except RiotForbiddenError:
        logger.info("ranked_entries_unavailable platform=%s reason=forbidden", platform)
        return {}
    except RiotNotFoundError:
        logger.info("ranked_entries_unavailable platform=%s reason=not_found", platform)
        return {}
    except RiotApiError as exc:
        logger.warning("ranked_entries_failed platform=%s error=%s", platform, exc)
        return {}
    return _normalize_entries(raw_entries)


def get_champion_mastery(
    puuid: str,
    platform: str = DEFAULT_REGION,
    *,
    client: RiotClient = default_client,
) -> Optional[list[dict]]:
    """Return champion mastery entries for a PUUID."""
    url = endpoints.CHAMPION_MASTERY_BY_PUUID.format(region=platform, puuid=puuid)
    return _safe_get(client, url, label="Champion Mastery")


def get_active_game(
    puuid: str,
    platform: str = DEFAULT_REGION,
    *,
    client: RiotClient = default_client,
) -> Optional[dict]:
    """Return active game data for the summoner identified by PUUID."""
    summoner = get_summoner_by_puuid(puuid, platform=platform, client=client)
    if not summoner or "id" not in summoner:
        logger.warning("active_game_requires_summoner_id platform=%s", platform)
        return None
    url = endpoints.ACTIVE_GAME.format(region=platform, encrypted_summoner_id=summoner["id"])
    return _safe_get(client, url, label="Active Game")


def get_champion_rotations(platform: str = DEFAULT_REGION, *, client: RiotClient = default_client) -> Optional[dict]:
    """Return current champion rotation for a platform."""
    url = endpoints.CHAMPION_ROTATIONS.format(region=platform)
    return _safe_get(client, url, label="Champion Rotations")


def get_latest_match_summary(
    game_name: str,
    tag_line: str,
    *,
    count: int = 5,
    client: RiotClient = default_client,
    strict: bool = False,
) -> Optional[dict]:
    """Return a UI-friendly summary for the latest match of a Riot ID."""
    account = get_account_by_riot_id(game_name, tag_line, client=client, strict=strict)
    if not account:
        return None

    puuid = account["puuid"]
    match_ids = get_match_ids_by_puuid(puuid, count=count, client=client, strict=strict) or []
    if not match_ids:
        return {
            "riot_id": f"{game_name}#{tag_line}",
            "puuid": puuid,
            "summoner": None,
            "match_ids": [],
            "match_id": None,
            "participant": None,
        }

    first_match_id = match_ids[0]
    detected_region = _region_from_match_id(first_match_id) or DEFAULT_REGION
    summoner = get_summoner_by_puuid(puuid, platform=detected_region, client=client, strict=strict)
    match = get_match(first_match_id, client=client, strict=strict)
    participant = get_player_stats_from_match(match, puuid) if match else None

    return {
        "riot_id": f"{game_name}#{tag_line}",
        "puuid": puuid,
        "summoner": summoner,
        "match_ids": match_ids,
        "match_id": first_match_id,
        "participant": participant,
        "region": detected_region,
    }


def get_recent_match_summaries(
    game_name: str,
    tag_line: str,
    count: int = 10,
    platform: Optional[str] = None,
    routing: Optional[str] = None,
    *,
    client: RiotClient = default_client,
    strict: bool = False,
) -> list[dict]:
    """Return summaries for recent matches, skipping individual match failures."""
    account = get_account_by_riot_id(game_name, tag_line, client=client, strict=strict)
    if not account:
        return []

    puuid = account["puuid"]
    selected_routing = routing or DEFAULT_ROUTING
    match_ids_url = endpoints.MATCH_IDS_BY_PUUID.format(routing=selected_routing, puuid=puuid)
    match_ids = _safe_get(
        client,
        match_ids_url,
        label="Match IDs",
        params={"start": 0, "count": count},
        strict=strict,
    ) or []
    summaries = []
    failed_count = 0

    for match_id in match_ids:
        match_url = endpoints.MATCH_BY_ID.format(routing=selected_routing, match_id=match_id)
        match = _safe_get(client, match_url, label="Match Details")
        if not match:
            failed_count += 1
            logger.warning("recent_match_skipped match_id=%s reason=match_fetch_failed", match_id)
            continue

        summary = _build_match_summary(match_id, match, puuid)
        if not summary:
            failed_count += 1
            logger.warning("recent_match_skipped match_id=%s reason=participant_not_found", match_id)
            continue

        summaries.append(summary)

    if summaries:
        summaries[0]["failed_count"] = failed_count
    elif failed_count:
        logger.warning("recent_matches_all_failed failed_count=%s", failed_count)

    return summaries


def get_match_details(match_id: str, *, client: RiotClient = default_client) -> Optional[dict]:
    """Compatibility alias for get_match."""
    return get_match(match_id, client=client)


def get_player_stats_from_match(match_data: dict, puuid: str) -> Optional[dict]:
    """Extract relevant participant stats from a match payload."""
    try:
        info = match_data.get("info", {})
        participants = info.get("participants", [])
        if not isinstance(participants, list):
            return None

        game_duration = info.get("gameDuration", 0) // 60
        game_mode = info.get("gameMode", "")
        for participant in participants:
            if participant.get("puuid") == puuid:
                return {
                    "champion": participant.get("championName"),
                    "lane": participant.get("lane"),
                    "kills": participant.get("kills", 0),
                    "deaths": participant.get("deaths", 0),
                    "assists": participant.get("assists", 0),
                    "win": participant.get("win", False),
                    "duration": game_duration,
                    "game_mode": game_mode,
                    "role": participant.get("role"),
                    "summonerId": participant.get("summonerId"),
                    "summonerName": participant.get("summonerName"),
                }
    except Exception as exc:
        logger.exception("match_parse_failed error=%s", exc)
    return None


def _build_match_summary(match_id: str, match_data: dict, puuid: str) -> Optional[dict]:
    info = match_data.get("info", {})
    participant = get_player_stats_from_match(match_data, puuid)
    if not participant:
        return None

    return {
        "match_id": match_id,
        "champion": participant["champion"],
        "kills": participant["kills"],
        "deaths": participant["deaths"],
        "assists": participant["assists"],
        "win": participant["win"],
        "game_mode": info.get("gameMode", participant.get("game_mode", "")),
        "queue_id": info.get("queueId"),
        "game_duration": info.get("gameDuration", 0),
        "game_creation": info.get("gameCreation"),
        "role": participant.get("role"),
        "lane": participant.get("lane"),
    }


def get_last_matches_stats(puuid: str, count: int = 20, *, client: RiotClient = default_client) -> list[dict]:
    """Return parsed player stats for recent matches."""
    match_ids = get_match_ids_by_puuid(puuid, count=count, client=client)
    stats = []
    if match_ids:
        for match_id in match_ids:
            match_data = get_match(match_id, client=client)
            if match_data:
                player_stats = get_player_stats_from_match(match_data, puuid)
                if player_stats:
                    stats.append(player_stats)
    return stats


def get_encrypted_summoner_id_and_platform_hint(
    puuid: str,
    *,
    client: RiotClient = default_client,
) -> Tuple[Optional[str], Optional[str]]:
    """Infer encrypted summoner id and platform from the most recent match."""
    ids = get_match_ids_by_puuid(puuid, count=1, client=client)
    if not ids:
        return None, None

    match_id = ids[0]
    try:
        platform_hint = match_id.split("_", 1)[0].lower()
    except Exception:
        platform_hint = None

    details = get_match(match_id, client=client)
    if not details:
        return None, platform_hint
    me = get_player_stats_from_match(details, puuid)
    enc_id = me.get("summonerId") if me else None
    return enc_id, platform_hint


def _normalize_entries(raw_list: list[dict]) -> Dict[str, dict]:
    """Normalize raw League entries by queue type."""
    result = {}
    for queue_entry in raw_list:
        queue = queue_entry.get("queueType")
        wins = queue_entry.get("wins", 0)
        losses = queue_entry.get("losses", 0)
        total = max(1, wins + losses)
        result[queue] = {
            "tier": queue_entry.get("tier", "UNRANKED"),
            "rank": queue_entry.get("rank", ""),
            "lp": queue_entry.get("leaguePoints", 0),
            "wins": wins,
            "losses": losses,
            "winrate": round((wins / total) * 100, 1),
        }
    return result


def get_ranked_entries_raw(
    encrypted_summoner_id: str,
    platform: str,
    *,
    client: RiotClient = default_client,
) -> Tuple[Dict[str, dict], int]:
    """Return normalized ranked entries and an HTTP-like status code."""
    url = endpoints.LEAGUE_BY_SUMMONER_ID.format(region=platform, encrypted_summoner_id=encrypted_summoner_id)
    try:
        raw_entries = client.get(url, label="League Entries")
    except RiotNotFoundError:
        return {}, 404
    except RiotApiError as exc:
        logger.warning("ranked_entries_failed platform=%s error=%s", platform, exc)
        return {}, 0
    return _normalize_entries(raw_entries), 200


def get_ranked_entries(
    encrypted_summoner_id: str,
    platform: str = DEFAULT_REGION,
    *,
    client: RiotClient = default_client,
) -> Dict[str, dict]:
    """Return normalized ranked entries or an empty dict on failure."""
    entries, status = get_ranked_entries_raw(encrypted_summoner_id, platform, client=client)
    return entries if status == 200 else {}


def find_platform_for_puuid(puuid: str, *, client: RiotClient = default_client):
    """Find the first platform where the PUUID resolves to a summoner."""
    for platform in PLATFORMS.values():
        summoner = get_summoner_by_puuid(puuid, platform=platform, client=client)
        if summoner and isinstance(summoner, dict) and "id" in summoner:
            return platform, summoner
    return None, None


def find_platform_by_summoner_id(
    encrypted_summoner_id: str,
    preferred: Optional[str] = None,
    *,
    client: RiotClient = default_client,
):
    """Find the most likely platform for an encrypted summoner id."""
    platforms = list(PLATFORMS.values())
    if preferred and preferred in platforms:
        platforms.remove(preferred)
        platforms = [preferred] + platforms

    first_ok_platform = None
    first_ok_entries: Dict[str, dict] = {}

    for platform in platforms:
        entries, status = get_ranked_entries_raw(encrypted_summoner_id, platform, client=client)
        if status == 200:
            if first_ok_platform is None:
                first_ok_platform, first_ok_entries = platform, entries
            if entries:
                return platform, entries

    if first_ok_platform is not None:
        return first_ok_platform, first_ok_entries
    return None, {}


def probe_rank_across_platforms(puuid: str, game_name: str, *, client: RiotClient = default_client):
    """Diagnostic helper to inspect rank lookup across all configured platforms."""
    results = {}
    for platform in PLATFORMS.values():
        summary = {"summoner_ok": False, "has_id": False, "entries_len": 0, "status": ""}
        try:
            summoner = get_summoner_by_puuid(puuid, platform=platform, client=client)
            if summoner:
                summary["summoner_ok"] = True
                summary["has_id"] = "id" in summoner
                if "id" in summoner:
                    entries = get_ranked_entries(summoner["id"], platform=platform, client=client)
                    summary["entries_len"] = len(entries.keys())
                    summary["status"] = "ok"
                else:
                    summary["status"] = "summoner sem 'id'"
            else:
                summary["status"] = "summoner não encontrado"
        except Exception as exc:
            summary["status"] = f"erro: {exc}"
        results[platform] = summary
    return results


def _safe_get(
    client: RiotClient,
    url: str,
    *,
    label: str,
    params: Optional[dict[str, Any]] = None,
    strict: bool = False,
) -> Optional[Any]:
    try:
        return client.get(url, params=params, label=label)
    except RiotNotFoundError:
        if strict:
            raise
        logger.info("riot_resource_not_found label=%s", label)
        return None
    except RiotApiError as exc:
        if strict:
            raise
        logger.warning("riot_service_failed label=%s error=%s", label, exc)
        return None


def _region_from_match_id(match_id: str) -> Optional[str]:
    if "_" not in match_id:
        return None
    return match_id.split("_", 1)[0].lower()
