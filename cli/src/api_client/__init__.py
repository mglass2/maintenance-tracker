"""API client package for Maintenance Tracker CLI."""

from .client import APIClient
from .config import APIConfig
from .exceptions import (
    APIClientError,
    APIClientError4xx,
    APIConfigurationError,
    APIConnectionError,
    APIInvalidResponseError,
    APIResponseError,
    APIServerError5xx,
    APITimeoutError,
)
from .models import APIResponse, HealthResponse

__version__ = "0.1.0"

__all__ = [
    "APIClient",
    "APIConfig",
    "APIClientError",
    "APIClientError4xx",
    "APIConfigurationError",
    "APIConnectionError",
    "APIInvalidResponseError",
    "APIResponseError",
    "APIServerError5xx",
    "APITimeoutError",
    "APIResponse",
    "HealthResponse",
]
