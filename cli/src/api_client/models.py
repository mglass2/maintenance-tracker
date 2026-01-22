"""Response data models for API client."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class HealthResponse:
    """Immutable response model for health check endpoint.

    Attributes:
        status: Health status (typically "healthy" or "unhealthy")
    """

    status: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthResponse":
        """Create HealthResponse from API response dictionary.

        Args:
            data: Dictionary with 'status' key

        Returns:
            HealthResponse instance

        Raises:
            KeyError: If required 'status' field is missing
            TypeError: If 'status' is not a string
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        if "status" not in data:
            raise KeyError("Missing required field: 'status'")

        status = data["status"]
        if not isinstance(status, str):
            raise TypeError(
                f"'status' must be a string, got {type(status).__name__}"
            )

        return cls(status=status)

    def is_healthy(self) -> bool:
        """Check if the API is healthy.

        Returns:
            True if status is "healthy", False otherwise
        """
        return self.status == "healthy"


@dataclass(frozen=True)
class APIResponse:
    """Immutable response model for generic API responses.

    Attributes:
        status_code: HTTP status code (e.g., 200, 404, 500)
        data: Parsed JSON response body as dictionary
        headers: HTTP response headers
    """

    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]

    def is_success(self) -> bool:
        """Check if response indicates success.

        Returns:
            True if status code is 2xx, False otherwise
        """
        return 200 <= self.status_code < 300

    def is_client_error(self) -> bool:
        """Check if response indicates client error.

        Returns:
            True if status code is 4xx, False otherwise
        """
        return 400 <= self.status_code < 500

    def is_server_error(self) -> bool:
        """Check if response indicates server error.

        Returns:
            True if status code is 5xx, False otherwise
        """
        return 500 <= self.status_code < 600
