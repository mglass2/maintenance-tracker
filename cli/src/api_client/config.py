"""Configuration management for API client."""

import os
from dataclasses import dataclass
from typing import Optional

from .exceptions import APIConfigurationError


@dataclass(frozen=True)
class APIConfig:
    """Immutable configuration for API client.

    Attributes:
        base_url: The base URL of the API (e.g., http://api:8000)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 3)
        retry_backoff: Initial backoff multiplier for exponential backoff (default: 0.5)
    """

    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 0.5

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load configuration from environment variables.

        Environment Variables:
            API_URL: Base URL of the API (required)

        Returns:
            APIConfig instance with values from environment

        Raises:
            APIConfigurationError: If required environment variables are missing
        """
        api_url = os.getenv("API_URL")
        if not api_url:
            raise APIConfigurationError(
                "API_URL environment variable not set. "
                "Set it to the base URL of the API (e.g., http://api:8000)"
            )

        config = cls(base_url=api_url)
        config.validate()
        return config

    def validate(self) -> None:
        """Validate configuration values.

        Raises:
            APIConfigurationError: If configuration is invalid
        """
        if not self.base_url:
            raise APIConfigurationError("base_url cannot be empty")

        if not self.base_url.startswith(("http://", "https://")):
            raise APIConfigurationError(
                f"base_url must start with http:// or https:// "
                f"(got: {self.base_url})"
            )

        if self.timeout <= 0:
            raise APIConfigurationError(
                f"timeout must be greater than 0 (got: {self.timeout})"
            )

        if self.max_retries < 0:
            raise APIConfigurationError(
                f"max_retries must be non-negative (got: {self.max_retries})"
            )

        if self.retry_backoff < 0:
            raise APIConfigurationError(
                f"retry_backoff must be non-negative "
                f"(got: {self.retry_backoff})"
            )
