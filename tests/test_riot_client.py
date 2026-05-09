import unittest
from unittest.mock import patch

from riot.exceptions import RiotAuthenticationError, RiotNotFoundError, RiotRateLimitError, RiotServerError
from riot.rate_limiter import RiotRateLimiter
from riot.riot_client import RiotClient


class FakeResponse:
    def __init__(self, status_code, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "params": params, "timeout": timeout})
        return self.responses.pop(0)


class RiotClientTest(unittest.TestCase):
    def test_get_envia_header_de_autenticacao(self):
        session = FakeSession([FakeResponse(200, {"ok": True})])
        client = RiotClient(session=session, rate_limiter=RiotRateLimiter())

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            self.assertEqual(client.get("https://example.test", label="Teste"), {"ok": True})

        self.assertEqual(session.calls[0]["headers"], {"X-Riot-Token": "valor_de_teste"})

    def test_get_exige_api_key(self):
        client = RiotClient(session=FakeSession([]), rate_limiter=RiotRateLimiter())

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RiotAuthenticationError):
                client.get("https://example.test", label="Teste")

    def test_get_trata_404(self):
        client = RiotClient(session=FakeSession([FakeResponse(404)]), rate_limiter=RiotRateLimiter())

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            with self.assertRaises(RiotNotFoundError):
                client.get("https://example.test", label="Teste")

    def test_get_retry_em_429(self):
        session = FakeSession([
            FakeResponse(429, headers={"Retry-After": "0"}),
            FakeResponse(200, {"ok": True}),
        ])
        client = RiotClient(session=session, rate_limiter=RiotRateLimiter())

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            with patch("riot.riot_client.time.sleep"):
                self.assertEqual(client.get("https://example.test", label="Teste"), {"ok": True})

        self.assertEqual(len(session.calls), 2)

    def test_get_levanta_rate_limit_apos_retries(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(429, headers={"Retry-After": "0"})]),
            max_retries=0,
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            with self.assertRaises(RiotRateLimitError):
                client.get("https://example.test", label="Teste")

    def test_get_levanta_server_error_apos_retries(self):
        client = RiotClient(
            session=FakeSession([FakeResponse(500)]),
            max_retries=0,
            rate_limiter=RiotRateLimiter(),
        )

        with patch.dict("os.environ", {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            with self.assertRaises(RiotServerError):
                client.get("https://example.test", label="Teste")


if __name__ == "__main__":
    unittest.main()
