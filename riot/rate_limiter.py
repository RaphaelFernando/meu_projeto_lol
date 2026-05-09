import logging
import time
from collections import deque
from threading import Lock

logger = logging.getLogger(__name__)


class RiotRateLimiter:
    """Simple local limiter for Riot development limits: 20 req/s and 100 req/2min."""

    def __init__(self, per_second: int = 20, per_two_minutes: int = 100) -> None:
        self.per_second = per_second
        self.per_two_minutes = per_two_minutes
        self._one_second_requests: deque[float] = deque()
        self._two_minute_requests: deque[float] = deque()
        self._lock = Lock()

    def wait(self) -> None:
        """Block until a request can be made according to local limits."""
        with self._lock:
            while True:
                now = time.monotonic()
                self._trim(now)

                waits = []
                if len(self._one_second_requests) >= self.per_second:
                    waits.append(1 - (now - self._one_second_requests[0]))
                if len(self._two_minute_requests) >= self.per_two_minutes:
                    waits.append(120 - (now - self._two_minute_requests[0]))

                wait_for = max([wait for wait in waits if wait > 0], default=0)
                if wait_for <= 0:
                    self._one_second_requests.append(now)
                    self._two_minute_requests.append(now)
                    return

                logger.info("Aguardando rate limit local por %.2fs", wait_for)
                time.sleep(wait_for)

    def _trim(self, now: float) -> None:
        while self._one_second_requests and now - self._one_second_requests[0] >= 1:
            self._one_second_requests.popleft()
        while self._two_minute_requests and now - self._two_minute_requests[0] >= 120:
            self._two_minute_requests.popleft()


default_rate_limiter = RiotRateLimiter()
