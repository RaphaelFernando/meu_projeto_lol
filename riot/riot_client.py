import logging
import time
from typing import Any, Optional

import requests

from .exceptions import (
    RiotApiError,
    RiotAuthenticationError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotServerError,
    RiotTimeoutError,
)
from .rate_limiter import RiotRateLimiter, default_rate_limiter
from .riot_config import DEFAULT_TIMEOUT, validate_api_key

logger = logging.getLogger(__name__)


class RiotClient:
    """Centralized Riot HTTP client with session reuse, retries, logging and rate limiting."""

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 2,
        session: Optional[requests.Session] = None,
        rate_limiter: Optional[RiotRateLimiter] = None,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()
        self.rate_limiter = rate_limiter or default_rate_limiter

    def get(self, url: str, *, params: Optional[dict[str, Any]] = None, label: str = "Riot API") -> Any:
        """Execute a GET request and return decoded JSON, raising typed Riot exceptions on failure."""
        headers = {"X-Riot-Token": validate_api_key()}

        for attempt in range(self.max_retries + 1):
            self.rate_limiter.wait()
            logger.info("riot_request method=GET label=%s url=%s attempt=%s", label, url, attempt + 1)

            try:
                response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            except requests.Timeout as exc:
                if attempt >= self.max_retries:
                    logger.exception("riot_timeout label=%s error=%s", label, exc)
                    raise RiotTimeoutError("Timeout ao chamar a Riot API.") from exc
                self._sleep_before_retry(attempt)
                continue
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    logger.exception("riot_request_failed label=%s error=%s", label, exc)
                    raise RiotApiError(str(exc)) from exc
                self._sleep_before_retry(attempt)
                continue

            if response.status_code == 429:
                retry_after = self._retry_after(response)
                logger.warning("riot_rate_limited label=%s retry_after=%.2f", label, retry_after)
                if attempt >= self.max_retries:
                    raise RiotRateLimitError("Rate limit excedido pela Riot API.")
                time.sleep(retry_after)
                continue

            if response.status_code >= 500:
                logger.warning("riot_server_error label=%s status=%s", label, response.status_code)
                if attempt >= self.max_retries:
                    raise RiotServerError(f"Erro {response.status_code} na Riot API.")
                self._sleep_before_retry(attempt)
                continue

            self._raise_for_status(response, label)
            logger.info("riot_response label=%s status=%s", label, response.status_code)
            return response.json()

        raise RiotApiError("Falha inesperada na Riot API.")

    def _raise_for_status(self, response: requests.Response, label: str) -> None:
        if response.status_code == 401:
            logger.error("riot_authentication_failed label=%s status=401", label)
            raise RiotAuthenticationError("API key ausente ou inválida.")
        if response.status_code == 403:
            logger.warning("riot_forbidden label=%s status=403", label)
            raise RiotForbiddenError("Acesso negado pela Riot API.")
        if response.status_code == 404:
            logger.info("riot_not_found label=%s status=404", label)
            raise RiotNotFoundError("Recurso não encontrado na Riot API.")
        if response.status_code >= 400:
            logger.error("riot_http_error label=%s status=%s", label, response.status_code)
            raise RiotApiError(f"Erro {response.status_code} na Riot API.")

    def _sleep_before_retry(self, attempt: int) -> None:
        wait_for = min(2 ** attempt, 8)
        logger.info("riot_retry wait=%.2f attempt=%s", wait_for, attempt + 1)
        time.sleep(wait_for)

    def _retry_after(self, response: requests.Response) -> float:
        value = response.headers.get("Retry-After")
        if value is None:
            return 1.0
        try:
            return max(float(value), 0.0)
        except ValueError:
            return 1.0


default_client = RiotClient()
