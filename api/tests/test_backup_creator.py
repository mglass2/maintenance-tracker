"""Tests for BackupCreator utility."""

import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.utils.backup_creator import (
    BackupCreator,
    BackupCreationError,
    PGDumpNotFoundError,
)


@pytest.fixture
def temp_backup_dir():
    """Create a temporary backup directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def valid_database_url():
    """Provide a valid PostgreSQL database URL."""
    return "postgresql://user:password@localhost:5432/testdb"


class TestBackupCreatorInit:
    """Tests for BackupCreator initialization."""

    def test_init_with_valid_url(self, valid_database_url, temp_backup_dir):
        """Test initialization with valid database URL."""
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(valid_database_url, temp_backup_dir)
            assert creator.database_url == valid_database_url
            assert creator.backup_dir == temp_backup_dir

    def test_init_creates_backup_dir(self, valid_database_url):
        """Test that initialization creates backup directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = os.path.join(tmpdir, "backups")
            with patch("src.utils.backup_creator.subprocess.run"):
                BackupCreator(valid_database_url, backup_dir)
                assert os.path.exists(backup_dir)

    def test_init_with_empty_url(self, temp_backup_dir):
        """Test initialization with empty database URL."""
        with pytest.raises(ValueError, match="database_url cannot be empty"):
            BackupCreator("", temp_backup_dir)

    def test_init_checks_pg_dump_availability(self, valid_database_url, temp_backup_dir):
        """Test that initialization checks for pg_dump."""
        with patch("src.utils.backup_creator.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Command failed")
            with pytest.raises(PGDumpNotFoundError):
                BackupCreator(valid_database_url, temp_backup_dir)


class TestDatabaseURLParsing:
    """Tests for database URL parsing."""

    def test_parse_complete_url(self, valid_database_url, temp_backup_dir):
        """Test parsing a complete PostgreSQL URL."""
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(valid_database_url, temp_backup_dir)
            params = creator._parse_database_url()

            assert params["user"] == "user"
            assert params["password"] == "password"
            assert params["host"] == "localhost"
            assert params["port"] == 5432
            assert params["database"] == "testdb"

    def test_parse_url_without_password(self, temp_backup_dir):
        """Test parsing URL without password."""
        url = "postgresql://user@localhost:5432/testdb"
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(url, temp_backup_dir)
            params = creator._parse_database_url()

            assert params["user"] == "user"
            assert params["password"] is None
            assert params["host"] == "localhost"
            assert params["port"] == 5432
            assert params["database"] == "testdb"

    def test_parse_url_with_default_port(self, temp_backup_dir):
        """Test parsing URL with default port."""
        url = "postgresql://user:password@localhost/testdb"
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(url, temp_backup_dir)
            params = creator._parse_database_url()

            assert params["port"] == 5432

    def test_parse_postgres_prefix(self, temp_backup_dir):
        """Test parsing URL with postgres:// prefix."""
        url = "postgres://user:password@localhost:5432/testdb"
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(url, temp_backup_dir)
            params = creator._parse_database_url()

            assert params["database"] == "testdb"

    def test_parse_invalid_url_no_at_sign(self, temp_backup_dir):
        """Test parsing invalid URL without @ sign."""
        url = "postgresql://user_password_localhost_5432_testdb"
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(url, temp_backup_dir)
            with pytest.raises(ValueError, match="Invalid database URL format"):
                creator._parse_database_url()

    def test_parse_invalid_url_no_slash(self, temp_backup_dir):
        """Test parsing invalid URL without database slash."""
        url = "postgresql://user:password@localhost:5432"
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(url, temp_backup_dir)
            with pytest.raises(ValueError, match="Invalid database URL format"):
                creator._parse_database_url()

    def test_parse_invalid_port(self, temp_backup_dir):
        """Test parsing URL with invalid port."""
        url = "postgresql://user:password@localhost:notaport/testdb"
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(url, temp_backup_dir)
            with pytest.raises(ValueError, match="Invalid port"):
                creator._parse_database_url()


class TestBackupFilenameGeneration:
    """Tests for backup filename generation."""

    def test_filename_format(self, valid_database_url, temp_backup_dir):
        """Test that generated filename has correct format."""
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(valid_database_url, temp_backup_dir)
            filename = creator._generate_backup_filename()

            assert filename.startswith("backup_")
            assert filename.endswith(".sql")
            assert len(filename) == 27  # backup_ (7) + YYYY-MM-DD_HH-MM-SS (19) + .sql (4)

    def test_filename_is_parseable(self, valid_database_url, temp_backup_dir):
        """Test that generated filename can be parsed back to datetime."""
        with patch("src.utils.backup_creator.subprocess.run"):
            creator = BackupCreator(valid_database_url, temp_backup_dir)
            filename = creator._generate_backup_filename()

            # Remove prefix and suffix
            timestamp_str = filename[7:-4]

            # Should be able to parse it
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
            assert isinstance(dt, datetime)


class TestBackupCreation:
    """Tests for actual backup creation."""

    def test_create_backup_success(self, valid_database_url, temp_backup_dir):
        """Test successful backup creation."""
        with patch("src.utils.backup_creator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            # Create a real backup file for testing
            creator = BackupCreator(valid_database_url, temp_backup_dir)

            # Mock the subprocess to write some data
            def side_effect(*args, **kwargs):
                stdout = kwargs.get("stdout")
                if stdout:
                    stdout.write("CREATE TABLE test (id INT);")
                return MagicMock(returncode=0, stderr="")

            mock_run.side_effect = side_effect

            result = creator.create_backup()

            assert "backup_file" in result
            assert "backup_path" in result
            assert "size_bytes" in result
            assert "created_at" in result
            assert result["backup_file"].startswith("backup_")
            assert result["backup_file"].endswith(".sql")

    def test_create_backup_pg_dump_failure(self, valid_database_url, temp_backup_dir):
        """Test backup creation when pg_dump fails."""
        with patch("src.utils.backup_creator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stderr="Connection refused"
            )

            creator = BackupCreator(valid_database_url, temp_backup_dir)

            with pytest.raises(BackupCreationError, match="pg_dump failed"):
                creator.create_backup()

    def test_create_backup_timeout(self, valid_database_url, temp_backup_dir):
        """Test backup creation when pg_dump times out."""
        import subprocess

        with patch("src.utils.backup_creator.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("pg_dump", 300)

            creator = BackupCreator(valid_database_url, temp_backup_dir)

            with pytest.raises(BackupCreationError, match="timed out"):
                creator.create_backup()

    def test_create_backup_cleans_up_on_failure(
        self, valid_database_url, temp_backup_dir
    ):
        """Test that failed backup files are cleaned up."""
        with patch("src.utils.backup_creator.subprocess.run") as mock_run:
            # First call (which check) succeeds
            # Second call (actual dump) fails
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which pg_dump
                MagicMock(returncode=1, stderr="Error"),  # actual dump
            ]

            creator = BackupCreator(valid_database_url, temp_backup_dir)

            # Manually set up for the second call
            mock_run.side_effect = None
            mock_run.return_value = MagicMock(
                returncode=1, stderr="Connection error"
            )

            with pytest.raises(BackupCreationError):
                creator.create_backup()

            # Verify no backup files were left behind
            sql_files = [f for f in os.listdir(temp_backup_dir) if f.endswith(".sql")]
            assert len(sql_files) == 0
