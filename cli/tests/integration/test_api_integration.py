"""Integration tests for API client against real API service.

These tests require the API service to be running.
Run with: docker-compose up

Then run tests with: pytest tests/integration/ -v
"""

import pytest

from src.api_client import APIClient, APIConnectionError
from src.api_client.config import APIConfig


@pytest.mark.integration
class TestHealthEndpointIntegration:
    """Integration tests for health endpoint against real API."""

    def test_health_endpoint_request(self):
        """Test GET /health endpoint against real API service.

        Prerequisites:
            - API service running (docker-compose up)
            - API_URL environment variable set
        """
        client = APIClient()
        try:
            response = client._make_request("GET", "/health")
            assert response.status_code == 200
            assert response.is_success()
            assert response.data.get("status") == "healthy"
        finally:
            client.close()

    def test_health_endpoint_returns_api_response(self):
        """Test that _make_request returns proper APIResponse object."""
        client = APIClient()
        try:
            response = client._make_request("GET", "/health")
            assert hasattr(response, "status_code")
            assert hasattr(response, "data")
            assert hasattr(response, "headers")
            assert response.is_success()
        finally:
            client.close()


@pytest.mark.integration
class TestConnectionHandling:
    """Integration tests for connection error handling."""

    def test_api_unreachable_raises_connection_error(self):
        """Test that unreachable API raises APIConnectionError.

        This test uses an invalid port to simulate API being down.
        """
        config = APIConfig(base_url="http://localhost:9999")
        client = APIClient(config=config)
        try:
            with pytest.raises(APIConnectionError):
                client._make_request("GET", "/health")
        finally:
            client.close()

    def test_invalid_url_host_raises_connection_error(self):
        """Test that invalid host raises APIConnectionError."""
        config = APIConfig(base_url="http://invalid-host-12345:8000")
        client = APIClient(config=config)
        try:
            with pytest.raises(APIConnectionError):
                client._make_request("GET", "/health")
        finally:
            client.close()


@pytest.mark.integration
class TestContextManager:
    """Integration tests for context manager support."""

    def test_endpoint_request_with_context_manager(self):
        """Test endpoint request using context manager pattern."""
        with APIClient() as client:
            response = client._make_request("GET", "/health")
            assert response.is_success()
            assert response.data.get("status") == "healthy"
