from riot.riot_client import default_client
from riot.riot_config import DEFAULT_REGION, DEFAULT_ROUTING, PLATFORMS, validate_api_key
from riot.riot_services import (
    _normalize_entries,
    find_platform_by_summoner_id,
    find_platform_for_puuid,
    get_account_by_riot_id,
    get_active_game,
    get_champion_mastery,
    get_champion_rotations,
    get_encrypted_summoner_id_and_platform_hint,
    get_last_matches_stats,
    get_latest_match_summary,
    get_match,
    get_match_details,
    get_match_ids_by_puuid,
    get_match_timeline,
    get_player_stats_from_match,
    get_ranked_entries,
    get_ranked_entries_by_puuid,
    get_ranked_entries_by_puuid,
    get_ranked_entries_raw,
    get_recent_match_summaries,
    get_summoner_by_name,
    get_summoner_by_puuid,
    probe_rank_across_platforms,
)

ACCOUNT_REGION = DEFAULT_ROUTING
MATCH_REGION = DEFAULT_ROUTING
DEFAULT_PLATFORM = DEFAULT_REGION


def _headers():
    return {"X-Riot-Token": validate_api_key()}


def _get(url: str, *, label: str, params: dict | None = None):
    return default_client.session.get(url, headers=_headers(), params=params, timeout=default_client.timeout)


riot_get = _get
