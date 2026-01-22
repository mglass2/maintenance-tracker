"""Tests for API client exception hierarchy."""

import pytest

from src.api_client.exceptions import (
    APIClientError,
    APIClientError4xx,
    APIConnectionError,
    APIConfigurationError,
    APIInvalidResponseError,
    APIResponseError,
    APIServerError5xx,
    APITimeoutError,
)


class TestAPIClientError:
    """Test base APIClientError exception."""

    def test_basic_error_message(self):
        """Test basic error creation with message."""
        error = APIClientError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_error_with_url(self):
        """Test error with URL context."""
        error = APIClientError("Failed", url="http://api:8000/health")
        assert "http://api:8000/health" in str(error)

    def test_error_with_status_code(self):
        """Test error with HTTP status code."""
        error = APIClientError("Failed", status_code=500)
        assert "Status: 500" in str(error)

    def test_error_with_all_context(self):
        """Test error with all context fields."""
        error = APIClientError(
            "Server error",
            url="http://api:8000/health",
            status_code=500,
        )
        error_str = str(error)
        assert "Server error" in error_str
        assert "http://api:8000/health" in error_str
        assert "500" in error_str

    def test_error_attributes(self):
        """Test that error attributes are accessible."""
        error = APIClientError(
            "Test error",
            url="http://test:8000",
            status_code=404,
        )
        assert error.message == "Test error"
        assert error.url == "http://test:8000"
        assert error.status_code == 404


class TestConnectionError:
    """Test APIConnectionError."""

    def test_connection_error_inheritance(self):
        """Test that APIConnectionError inherits from APIClientError."""
        error = APIConnectionError("Connection failed")
        assert isinstance(error, APIClientError)

    def test_connection_error_message(self):
        """Test connection error message."""
        error = APIConnectionError("Failed to connect")
        assert "Failed to connect" in str(error)


class TestTimeoutError:
    """Test APITimeoutError."""

    def test_timeout_error_inheritance(self):
        """Test that APITimeoutError inherits from APIClientError."""
        error = APITimeoutError("Request timed out")
        assert isinstance(error, APIClientError)

    def test_timeout_error_message(self):
        """Test timeout error message."""
        error = APITimeoutError("30s timeout exceeded")
        assert "30s timeout exceeded" in str(error)


class TestResponseError:
    """Test APIResponseError."""

    def test_response_error_with_body(self):
        """Test response error stores response body."""
        error = APIResponseError(
            "Bad request",
            status_code=400,
            response_body='{"error": "Invalid input"}',
        )
        assert error.response_body == '{"error": "Invalid input"}'

    def test_response_error_without_body(self):
        """Test response error without response body."""
        error = APIResponseError("Error", status_code=500)
        assert error.response_body is None

    def test_response_error_inheritance(self):
        """Test that APIResponseError inherits from APIClientError."""
        error = APIResponseError("Error", status_code=500)
        assert isinstance(error, APIClientError)


class TestClient4xxError:
    """Test APIClientError4xx."""

    def test_4xx_error_inheritance(self):
        """Test that 4xx error inherits from APIResponseError."""
        error = APIClientError4xx("Not found", status_code=404)
        assert isinstance(error, APIResponseError)
        assert isinstance(error, APIClientError)

    def test_4xx_error_message(self):
        """Test 4xx error message."""
        error = APIClientError4xx("Not found", status_code=404)
        assert "Status: 404" in str(error)


class TestServer5xxError:
    """Test APIServerError5xx."""

    def test_5xx_error_inheritance(self):
        """Test that 5xx error inherits from APIResponseError."""
        error = APIServerError5xx("Server error", status_code=500)
        assert isinstance(error, APIResponseError)
        assert isinstance(error, APIClientError)

    def test_5xx_error_message(self):
        """Test 5xx error message."""
        error = APIServerError5xx("Server error", status_code=500)
        assert "Status: 500" in str(error)


class TestInvalidResponseError:
    """Test APIInvalidResponseError."""

    def test_invalid_response_error(self):
        """Test invalid response error."""
        error = APIInvalidResponseError(
            "Invalid JSON",
            url="http://api:8000/data",
            response_text="{not valid json}",
        )
        assert error.response_text == "{not valid json}"
        assert "http://api:8000/data" in str(error)

    def test_invalid_response_error_inheritance(self):
        """Test that invalid response error inherits from APIClientError."""
        error = APIInvalidResponseError("Invalid JSON")
        assert isinstance(error, APIClientError)


class TestConfigurationError:
    """Test APIConfigurationError."""

    def test_configuration_error_inheritance(self):
        """Test that config error inherits from APIClientError."""
        error = APIConfigurationError("Invalid config")
        assert isinstance(error, APIClientError)

    def test_configuration_error_message(self):
        """Test configuration error message."""
        error = APIConfigurationError("API_URL not set")
        assert "API_URL not set" in str(error)


class TestErrorHierarchy:
    """Test the complete exception hierarchy."""

    def test_all_errors_inherit_from_base(self):
        """Test that all custom errors inherit from APIClientError."""
        errors = [
            APIConnectionError("test"),
            APITimeoutError("test"),
            APIResponseError("test"),
            APIClientError4xx("test"),
            APIServerError5xx("test"),
            APIInvalidResponseError("test"),
            APIConfigurationError("test"),
        ]
        for error in errors:
            assert isinstance(error, APIClientError)

    def test_error_catching_by_type(self):
        """Test that errors can be caught by specific type."""
        errors = [
            APIConnectionError("Connection failed"),
            APITimeoutError("Timeout"),
            APIClientError4xx("Not found", status_code=404),
            APIServerError5xx("Server error", status_code=500),
        ]

        for error in errors:
            with pytest.raises(APIClientError):
                raise error

        with pytest.raises(APIConnectionError):
            raise APIConnectionError("test")

        with pytest.raises(APITimeoutError):
            raise APITimeoutError("test")

        with pytest.raises(APIClientError4xx):
            raise APIClientError4xx("test", status_code=400)

        with pytest.raises(APIServerError5xx):
            raise APIServerError5xx("test", status_code=500)
