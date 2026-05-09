import json
import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riot.endpoints import MATCH_BY_ID
from riot.riot_client import default_client
from riot.riot_config import DEFAULT_ROUTING

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

game_ids = [
    "BR1_3120917901",
    "BR1_3120863516",
    "BR1_3120279328",
    "BR1_3120248715",
    "BR1_3120224544",
]

output_file = os.path.join(os.getcwd(), "matches_dump.json")
all_matches = []

for match_id in game_ids:
    url = MATCH_BY_ID.format(routing=DEFAULT_ROUTING, match_id=match_id)
    logger.info("Buscando partida %s...", match_id)
    try:
        all_matches.append(default_client.get(url, label="Match Dump"))
    except Exception:
        logger.exception("Exceção ao buscar %s", match_id)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_matches, f, ensure_ascii=False, indent=2)

logger.info("%s partidas salvas em: %s", len(all_matches), output_file)
