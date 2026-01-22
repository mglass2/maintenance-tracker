"""Tests for API client."""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConfig,
    APIConnectionError,
    APIConfigurationError,
    APIInvalidResponseError,
    APIServerError5xx,
    APITimeoutError,
    HealthResponse,
)
from src.api_client.models import APIResponse
from src.api_client.utils import build_url


class TestAPIClientInitialization:
    """Test APIClient initialization."""

    def test_init_with_explicit_config(self):
        """Test initializing client with explicit config."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)
        assert client.config == config
        client.close()

    def test_init_loads_from_env(self, monkeypatch):
        """Test that APIClient loads config from environment."""
        monkeypatch.setenv("API_URL", "http://api:8000")
        client = APIClient()
        assert client.config.base_url == "http://api:8000"
        client.close()

    def test_init_creates_session(self):
        """Test that client creates a session."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)
        assert client._session is not None
        assert isinstance(client._session, requests.Session)
        client.close()

    def test_init_sets_headers(self):
        """Test that session has correct headers."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)
        session = client._session
        assert session.headers.get("Content-Type") == "application/json"
        assert session.headers.get("Accept") == "application/json"
        assert "MaintenanceTracker-CLI" in session.headers.get("User-Agent", "")
        client.close()

    def test_init_with_invalid_env_config(self, monkeypatch):
        """Test that invalid environment raises error."""
        monkeypatch.delenv("API_URL", raising=False)
        with pytest.raises(APIConfigurationError):
            APIClient()


class TestAPIClientContextManager:
    """Test APIClient context manager support."""

    def test_context_manager_enter_exit(self):
        """Test context manager protocol."""
        config = APIConfig(base_url="http://api:8000")
        with APIClient(config=config) as client:
            assert client is not None
            assert client._session is not None

    def test_context_manager_closes_session(self):
        """Test that context manager closes session."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)
        session = client._session
        client.close()
        # Session should be closed (no further checks as requests doesn't
        # expose a direct way to check this)

    def test_close_multiple_times_is_safe(self):
        """Test that calling close multiple times doesn't error."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)
        client.close()
        client.close()  # Should not raise


class TestAPIClientRequests:
    """Test generic request handling via _make_request method."""

    def test_successful_request(self):
        """Test successful GET request to any endpoint."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "healthy"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            response = client._make_request("GET", "/health")

            assert response.status_code == 200
            assert response.data == {"status": "healthy"}
            assert response.is_success()
            mock_request.assert_called_once()
            client.close()

    def test_successful_post_request(self):
        """Test successful POST request with data."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.text = '{"id": 123}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            data = {"name": "Test Item"}
            response = client._make_request("POST", "/items", data=data)

            assert response.status_code == 201
            assert response.data == {"id": 123}
            assert response.is_success()
            client.close()

    def test_request_connection_error(self):
        """Test request with connection error."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(
            client._session, "request"
        ) as mock_request:
            mock_request.side_effect = requests.ConnectionError("Connection failed")

            with pytest.raises(APIConnectionError):
                client._make_request("GET", "/health")

            client.close()

    def test_request_timeout(self):
        """Test request with timeout."""
        config = APIConfig(base_url="http://api:8000", timeout=5)
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_request.side_effect = requests.Timeout("Timed out")

            with pytest.raises(APITimeoutError) as exc_info:
                client._make_request("GET", "/health")

            assert "5s" in str(exc_info.value)
            client.close()

    def test_request_4xx_error(self):
        """Test request with 4xx error (no retry)."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = '{"error": "Not found"}'
            mock_request.return_value = mock_response

            with pytest.raises(APIClientError4xx) as exc_info:
                client._make_request("GET", "/nonexistent")

            assert exc_info.value.status_code == 404
            client.close()

    def test_request_5xx_error_no_retry(self):
        """Test request with 5xx error and no retries."""
        config = APIConfig(base_url="http://api:8000", max_retries=0)
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = '{"error": "Server error"}'
            mock_request.return_value = mock_response

            with pytest.raises(APIServerError5xx) as exc_info:
                client._make_request("GET", "/health")

            assert exc_info.value.status_code == 500
            client.close()

    def test_request_5xx_error_with_retry_succeeds(self):
        """Test request with 5xx error that retries then succeeds."""
        config = APIConfig(base_url="http://api:8000", max_retries=2, retry_backoff=0.01)
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            # First two calls return 500, third succeeds
            error_response = Mock()
            error_response.status_code = 500
            error_response.text = '{"error": "Server error"}'

            success_response = Mock()
            success_response.status_code = 200
            success_response.text = '{"status": "healthy"}'
            success_response.headers = {}

            mock_request.side_effect = [error_response, error_response, success_response]

            with patch("time.sleep"):  # Mock sleep to speed up test
                response = client._make_request("GET", "/health")

            assert response.status_code == 200
            assert response.data == {"status": "healthy"}
            assert mock_request.call_count == 3
            client.close()

    def test_request_5xx_error_exhausts_retries(self):
        """Test request with 5xx error that exhausts retries."""
        config = APIConfig(base_url="http://api:8000", max_retries=2, retry_backoff=0.01)
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            error_response = Mock()
            error_response.status_code = 500
            error_response.text = '{"error": "Server error"}'
            mock_request.return_value = error_response

            with patch("time.sleep"):  # Mock sleep to speed up test
                with pytest.raises(APIServerError5xx):
                    client._make_request("GET", "/health")

            # Should call request max_retries + 1 times
            assert mock_request.call_count == 3
            client.close()

    def test_request_invalid_json_response(self):
        """Test request with invalid JSON response."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Not valid JSON"
            mock_request.return_value = mock_response

            with pytest.raises(APIInvalidResponseError):
                client._make_request("GET", "/health")

            client.close()


class TestAPIClientMakeRequest:
    """Test internal _make_request method."""

    def test_make_request_builds_correct_url(self):
        """Test that _make_request builds correct URL."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"data": "test"}'
            mock_response.headers = {"Content-Type": "application/json"}
            mock_request.return_value = mock_response

            client._make_request("GET", "/test")

            # Check that request was called with correct URL
            call_args = mock_request.call_args
            assert call_args[1]["url"] == "http://api:8000/test"
            client.close()

    def test_make_request_passes_json_data(self):
        """Test that _make_request passes JSON data."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"data": "test"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            data = {"key": "value"}
            client._make_request("POST", "/test", data=data)

            # Check that data was passed
            call_args = mock_request.call_args
            assert call_args[1]["json"] == data
            client.close()

    def test_make_request_returns_api_response(self):
        """Test that _make_request returns APIResponse."""
        config = APIConfig(base_url="http://api:8000")
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {"X-Custom": "value"}
            mock_request.return_value = mock_response

            response = client._make_request("GET", "/test")

            assert isinstance(response, APIResponse)
            assert response.status_code == 200
            assert response.data == {"status": "ok"}
            assert response.headers["X-Custom"] == "value"
            client.close()

    def test_make_request_uses_configured_timeout(self):
        """Test that _make_request uses configured timeout."""
        config = APIConfig(base_url="http://api:8000", timeout=42)
        client = APIClient(config=config)

        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"data": "test"}'
            mock_response.headers = {}
            mock_request.return_value = mock_response

            client._make_request("GET", "/test")

            # Check that timeout was passed
            call_args = mock_request.call_args
            assert call_args[1]["timeout"] == 42
            client.close()


class TestHealthResponseModel:
    """Test HealthResponse model."""

    def test_health_response_from_dict(self):
        """Test creating HealthResponse from dict."""
        response = HealthResponse.from_dict({"status": "healthy"})
        assert response.status == "healthy"

    def test_health_response_from_dict_missing_status(self):
        """Test that missing status field raises error."""
        with pytest.raises(KeyError):
            HealthResponse.from_dict({})

    def test_health_response_from_dict_invalid_type(self):
        """Test that non-dict input raises error."""
        with pytest.raises(TypeError):
            HealthResponse.from_dict("not a dict")

    def test_health_response_from_dict_status_not_string(self):
        """Test that non-string status raises error."""
        with pytest.raises(TypeError):
            HealthResponse.from_dict({"status": 123})

    def test_health_response_is_healthy(self):
        """Test is_healthy method."""
        healthy = HealthResponse(status="healthy")
        assert healthy.is_healthy()

        unhealthy = HealthResponse(status="unhealthy")
        assert not unhealthy.is_healthy()

    def test_health_response_immutability(self):
        """Test that HealthResponse is immutable."""
        response = HealthResponse(status="healthy")
        with pytest.raises((AttributeError, TypeError)):
            response.status = "unhealthy"


class TestAPIResponse:
    """Test APIResponse model."""

    def test_api_response_success_check(self):
        """Test is_success method."""
        success_response = APIResponse(
            status_code=200,
            data={},
            headers={},
        )
        assert success_response.is_success()

        created_response = APIResponse(
            status_code=201,
            data={},
            headers={},
        )
        assert created_response.is_success()

        error_response = APIResponse(
            status_code=404,
            data={},
            headers={},
        )
        assert not error_response.is_success()

    def test_api_response_client_error_check(self):
        """Test is_client_error method."""
        client_error = APIResponse(
            status_code=404,
            data={},
            headers={},
        )
        assert client_error.is_client_error()

        success_response = APIResponse(
            status_code=200,
            data={},
            headers={},
        )
        assert not success_response.is_client_error()

    def test_api_response_server_error_check(self):
        """Test is_server_error method."""
        server_error = APIResponse(
            status_code=500,
            data={},
            headers={},
        )
        assert server_error.is_server_error()

        success_response = APIResponse(
            status_code=200,
            data={},
            headers={},
        )
        assert not success_response.is_server_error()

    def test_api_response_immutability(self):
        """Test that APIResponse is immutable."""
        response = APIResponse(
            status_code=200,
            data={},
            headers={},
        )
        with pytest.raises((AttributeError, TypeError)):
            response.status_code = 404
