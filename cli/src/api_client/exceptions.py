"""Custom exception hierarchy for API client errors."""


class APIClientError(Exception):
    """Base exception for all API client errors."""

    def __init__(self, message: str, url: str = None, status_code: int = None):
        """Initialize API client exception.

        Args:
            message: Human-readable error message
            url: URL that caused the error (optional)
            status_code: HTTP status code (optional)
        """
        self.message = message
        self.url = url
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return formatted error message."""
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.status_code is not None:
            parts.append(f"Status: {self.status_code}")
        return " | ".join(parts)


class APIConnectionError(APIClientError):
    """Raised when connection to API fails."""

    pass


class APITimeoutError(APIClientError):
    """Raised when API request times out."""

    pass


class APIResponseError(APIClientError):
    """Base exception for HTTP response errors."""

    def __init__(
        self,
        message: str,
        url: str = None,
        status_code: int = None,
        response_body: str = None,
    ):
        """Initialize response error with optional response body.

        Args:
            message: Human-readable error message
            url: URL that caused the error
            status_code: HTTP status code
            response_body: HTTP response body (optional)
        """
        super().__init__(message, url, status_code)
        self.response_body = response_body


class APIClientError4xx(APIResponseError):
    """Raised for 4xx HTTP response codes (client errors)."""

    pass


class APIServerError5xx(APIResponseError):
    """Raised for 5xx HTTP response codes (server errors)."""

    pass


class APIInvalidResponseError(APIClientError):
    """Raised when API response cannot be parsed or is malformed."""

    def __init__(self, message: str, url: str = None, response_text: str = None):
        """Initialize invalid response error.

        Args:
            message: Human-readable error message
            url: URL that caused the error
            response_text: The invalid response text
        """
        super().__init__(message, url)
        self.response_text = response_text


class APIConfigurationError(APIClientError):
    """Raised when API configuration is invalid."""

    pass
