import logging
import os
from pathlib import Path
from typing import Dict

from .exceptions import RiotAuthenticationError

logger = logging.getLogger(__name__)

DEFAULT_REGION = os.getenv("RIOT_REGION", "br1")
DEFAULT_ROUTING = os.getenv("RIOT_ROUTING", "americas")
DEFAULT_TIMEOUT = 10

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


def load_dotenv(path: str | Path = ".env") -> None:
    """Load simple KEY=VALUE pairs from .env into os.environ without logging secrets."""
    dotenv_path = Path(path)
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY", "")


def validate_api_key() -> str:
    """Return the Riot API key or raise a configuration error."""
    api_key = os.getenv("RIOT_API_KEY", "")
    if not api_key:
        raise RiotAuthenticationError(
            "RIOT_API_KEY não configurada. Defina a variável de ambiente "
            "RIOT_API_KEY ou crie um arquivo .env local."
        )
    return api_key
