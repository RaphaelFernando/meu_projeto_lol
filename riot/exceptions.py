class RiotApiError(Exception):
    """Base exception for Riot API failures."""


class RiotAuthenticationError(RiotApiError):
    """Raised when the Riot API key is missing or invalid."""


class RiotForbiddenError(RiotApiError):
    """Raised when the Riot API rejects access to a resource."""


class RiotNotFoundError(RiotApiError):
    """Raised when a Riot API resource is not found."""


class RiotRateLimitError(RiotApiError):
    """Raised when Riot API rate limits are exceeded."""


class RiotServerError(RiotApiError):
    """Raised for Riot API 5xx failures."""


class RiotTimeoutError(RiotApiError):
    """Raised when a Riot API request times out."""
