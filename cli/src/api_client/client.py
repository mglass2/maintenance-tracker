"""Core API client for communicating with the Maintenance Tracker API."""

import time
from typing import Optional

import requests

from .config import APIConfig
from .exceptions import (
    APIClientError4xx,
    APIConnectionError,
    APIInvalidResponseError,
    APIServerError5xx,
    APITimeoutError,
)
from .models import APIResponse
from .utils import build_url, parse_json_response


class APIClient:
    """HTTP client for Maintenance Tracker API.

    This client handles all communication with the backend API,
    including request/response handling, error handling, and retries.

    Example:
        >>> from src.api_client import APIClient
        >>> client = APIClient()
        >>> response = client._make_request("GET", "/health")
        >>> print(response.data)
        {'status': 'healthy'}
        >>> client.close()
    """

    def __init__(self, config: Optional[APIConfig] = None):
        """Initialize API client.

        Args:
            config: API configuration. If None, loads from environment.

        Raises:
            APIConfigurationError: If configuration is invalid
        """
        self.config = config or APIConfig.from_env()
        self.config.validate()
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure HTTP session.

        Returns:
            Configured requests.Session instance
        """
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MaintenanceTracker-CLI/0.1.0",
        })
        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        retry_count: int = 0,
    ) -> APIResponse:
        """Make HTTP request to API with error handling and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., /health)
            data: Request body data (optional)
            retry_count: Current retry attempt (internal)

        Returns:
            APIResponse with status code, data, and headers

        Raises:
            APIConnectionError: On network/connection failures
            APITimeoutError: On request timeout
            APIClientError4xx: On 4xx HTTP response (no retry)
            APIServerError5xx: On 5xx HTTP response (with retry)
            APIInvalidResponseError: On malformed response
        """
        url = build_url(self.config.base_url, endpoint)

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.config.timeout,
            )
        except requests.Timeout as e:
            raise APITimeoutError(
                f"Request timed out after {self.config.timeout}s",
                url=url,
            ) from e
        except requests.ConnectionError as e:
            raise APIConnectionError(
                f"Failed to connect to API: {str(e)}",
                url=url,
            ) from e
        except requests.RequestException as e:
            raise APIConnectionError(
                f"Request failed: {str(e)}",
                url=url,
            ) from e

        # Handle 4xx errors (no retry)
        if 400 <= response.status_code < 500:
            try:
                response_body = response.text
            except Exception:
                response_body = "<unable to read response body>"

            raise APIClientError4xx(
                f"Client error: {response.status_code}",
                url=url,
                status_code=response.status_code,
                response_body=response_body,
            )

        # Handle 5xx errors (retry with backoff)
        if 500 <= response.status_code < 600:
            if retry_count < self.config.max_retries:
                # Exponential backoff
                backoff = self.config.retry_backoff * (2 ** retry_count)
                time.sleep(backoff)
                return self._make_request(
                    method=method,
                    endpoint=endpoint,
                    data=data,
                    retry_count=retry_count + 1,
                )

            try:
                response_body = response.text
            except Exception:
                response_body = "<unable to read response body>"

            raise APIServerError5xx(
                f"Server error after {retry_count} retries: "
                f"{response.status_code}",
                url=url,
                status_code=response.status_code,
                response_body=response_body,
            )

        # Handle successful responses
        try:
            response_data = parse_json_response(response.text, url=url)
        except APIInvalidResponseError:
            raise

        return APIResponse(
            status_code=response.status_code,
            data=response_data,
            headers=dict(response.headers),
        )

    def close(self) -> None:
        """Close session and cleanup resources."""
        if self._session:
            self._session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
