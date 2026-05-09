import json
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riot.endpoints import MATCH_BY_ID
from riot.riot_client import default_client
from riot.riot_config import DEFAULT_ROUTING

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

match_id = "BR1_3120917901"
url = MATCH_BY_ID.format(routing=DEFAULT_ROUTING, match_id=match_id)
match_data = default_client.get(url, label="Match Debug")

logger.info("Dados da partida %s:\n%s", match_id, json.dumps(match_data, ensure_ascii=False, indent=2))
