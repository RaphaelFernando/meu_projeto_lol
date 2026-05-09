from riot.riot_client import RiotClient, default_client
from riot.riot_config import validate_api_key


def _headers():
    return {"X-Riot-Token": validate_api_key()}


def riot_get(url: str, *, label: str, params: dict | None = None):
    return default_client.session.get(url, headers=_headers(), params=params, timeout=default_client.timeout)
