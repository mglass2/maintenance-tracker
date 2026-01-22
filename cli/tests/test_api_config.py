"""Tests for API client configuration."""

import os

import pytest

from src.api_client.config import APIConfig
from src.api_client.exceptions import APIConfigurationError


class TestAPIConfigBasics:
    """Test basic APIConfig functionality."""

    def test_config_creation_with_defaults(self):
        """Test creating config with default values."""
        config = APIConfig(base_url="http://api:8000")
        assert config.base_url == "http://api:8000"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_backoff == 0.5

    def test_config_creation_with_custom_values(self):
        """Test creating config with custom values."""
        config = APIConfig(
            base_url="http://localhost:8000",
            timeout=60,
            max_retries=5,
            retry_backoff=1.0,
        )
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.retry_backoff == 1.0

    def test_config_is_frozen(self):
        """Test that config is immutable (frozen dataclass)."""
        config = APIConfig(base_url="http://api:8000")
        with pytest.raises((AttributeError, TypeError)):
            config.base_url = "http://other:8000"

        with pytest.raises((AttributeError, TypeError)):
            config.timeout = 60


class TestAPIConfigValidation:
    """Test APIConfig validation."""

    def test_validate_valid_config(self):
        """Test that valid config passes validation."""
        config = APIConfig(base_url="http://api:8000")
        config.validate()  # Should not raise

    def test_validate_https_url(self):
        """Test that HTTPS URLs are valid."""
        config = APIConfig(base_url="https://api.example.com")
        config.validate()  # Should not raise

    def test_validate_empty_base_url(self):
        """Test that empty base_url raises error."""
        config = APIConfig(base_url="")
        with pytest.raises(APIConfigurationError) as exc_info:
            config.validate()
        assert "base_url cannot be empty" in str(exc_info.value)

    def test_validate_invalid_url_scheme(self):
        """Test that URLs without http/https raise error."""
        config = APIConfig(base_url="ftp://api:8000")
        with pytest.raises(APIConfigurationError) as exc_info:
            config.validate()
        assert "http://" in str(exc_info.value) or "https://" in str(exc_info.value)

    def test_validate_url_without_scheme(self):
        """Test that URLs without scheme raise error."""
        config = APIConfig(base_url="api:8000")
        with pytest.raises(APIConfigurationError):
            config.validate()

    def test_validate_zero_timeout(self):
        """Test that zero timeout raises error."""
        config = APIConfig(base_url="http://api:8000", timeout=0)
        with pytest.raises(APIConfigurationError) as exc_info:
            config.validate()
        assert "timeout must be greater than 0" in str(exc_info.value)

    def test_validate_negative_timeout(self):
        """Test that negative timeout raises error."""
        config = APIConfig(base_url="http://api:8000", timeout=-1)
        with pytest.raises(APIConfigurationError):
            config.validate()

    def test_validate_negative_max_retries(self):
        """Test that negative max_retries raises error."""
        config = APIConfig(base_url="http://api:8000", max_retries=-1)
        with pytest.raises(APIConfigurationError) as exc_info:
            config.validate()
        assert "max_retries must be non-negative" in str(exc_info.value)

    def test_validate_negative_retry_backoff(self):
        """Test that negative retry_backoff raises error."""
        config = APIConfig(base_url="http://api:8000", retry_backoff=-0.5)
        with pytest.raises(APIConfigurationError) as exc_info:
            config.validate()
        assert "retry_backoff must be non-negative" in str(exc_info.value)

    def test_validate_zero_max_retries_is_valid(self):
        """Test that zero max_retries is valid (means no retries)."""
        config = APIConfig(base_url="http://api:8000", max_retries=0)
        config.validate()  # Should not raise

    def test_validate_zero_retry_backoff_is_valid(self):
        """Test that zero retry_backoff is valid."""
        config = APIConfig(base_url="http://api:8000", retry_backoff=0)
        config.validate()  # Should not raise


class TestAPIConfigFromEnv:
    """Test APIConfig.from_env() class method."""

    def test_from_env_with_valid_url(self, monkeypatch):
        """Test loading config from environment with valid URL."""
        monkeypatch.setenv("API_URL", "http://api:8000")
        config = APIConfig.from_env()
        assert config.base_url == "http://api:8000"

    def test_from_env_with_https_url(self, monkeypatch):
        """Test loading config from environment with HTTPS URL."""
        monkeypatch.setenv("API_URL", "https://api.example.com")
        config = APIConfig.from_env()
        assert config.base_url == "https://api.example.com"

    def test_from_env_missing_api_url(self, monkeypatch):
        """Test that missing API_URL raises error."""
        monkeypatch.delenv("API_URL", raising=False)
        with pytest.raises(APIConfigurationError) as exc_info:
            APIConfig.from_env()
        assert "API_URL" in str(exc_info.value)

    def test_from_env_empty_api_url(self, monkeypatch):
        """Test that empty API_URL raises error."""
        monkeypatch.setenv("API_URL", "")
        with pytest.raises(APIConfigurationError):
            APIConfig.from_env()

    def test_from_env_invalid_url_scheme(self, monkeypatch):
        """Test that invalid URL scheme raises error."""
        monkeypatch.setenv("API_URL", "ftp://api:8000")
        with pytest.raises(APIConfigurationError):
            APIConfig.from_env()

    def test_from_env_uses_defaults(self, monkeypatch):
        """Test that from_env uses default timeout, retries, etc."""
        monkeypatch.setenv("API_URL", "http://api:8000")
        config = APIConfig.from_env()
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_backoff == 0.5

    def test_from_env_calls_validate(self, monkeypatch):
        """Test that from_env calls validate() on the config."""
        monkeypatch.setenv("API_URL", "invalid-url")
        with pytest.raises(APIConfigurationError):
            APIConfig.from_env()


class TestAPIConfigEquality:
    """Test APIConfig equality and comparison."""

    def test_equal_configs(self):
        """Test that identical configs are equal."""
        config1 = APIConfig(base_url="http://api:8000")
        config2 = APIConfig(base_url="http://api:8000")
        assert config1 == config2

    def test_different_configs_not_equal(self):
        """Test that different configs are not equal."""
        config1 = APIConfig(base_url="http://api:8000")
        config2 = APIConfig(base_url="http://api:9000")
        assert config1 != config2

    def test_different_timeout_not_equal(self):
        """Test that configs with different timeouts are not equal."""
        config1 = APIConfig(base_url="http://api:8000", timeout=30)
        config2 = APIConfig(base_url="http://api:8000", timeout=60)
        assert config1 != config2
