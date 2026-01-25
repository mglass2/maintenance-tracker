"""Integration tests for backup API endpoints."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestCreateBackupEndpoint:
    """Tests for POST /backups/create endpoint."""

    def test_create_backup_success(self, client: TestClient):
        """Test successful backup creation."""
        with patch("src.routes.backups.BackupManager.manage_backups") as mock_manage:
            with patch("src.routes.backups.BackupCreator.create_backup") as mock_create:
                mock_manage.return_value = {
                    "total_backups": 5,
                    "retained": 5,
                    "archived": 0,
                    "deleted": 0,
                }

                mock_create.return_value = {
                    "backup_file": "backup_2026-01-25_14-30-45.sql",
                    "backup_path": "/app/backups/backup_2026-01-25_14-30-45.sql",
                    "size_bytes": 524288,
                    "created_at": "2026-01-25T14:30:45Z",
                }

                response = client.post("/backups/create")

                assert response.status_code == 201
                data = response.json()

                assert "data" in data
                assert "message" in data
                assert data["message"] == "Database backup created successfully"

                backup_data = data["data"]
                assert backup_data["backup_file"] == "backup_2026-01-25_14-30-45.sql"
                assert backup_data["size_bytes"] == 524288
                assert backup_data["created_at"] == "2026-01-25T14:30:45Z"

    def test_create_backup_response_format(self, client: TestClient):
        """Test response format matches specification."""
        with patch("src.routes.backups.BackupManager.manage_backups") as mock_manage:
            with patch("src.routes.backups.BackupCreator.create_backup") as mock_create:
                mock_manage.return_value = {
                    "total_backups": 10,
                    "retained": 5,
                    "archived": 3,
                    "deleted": 2,
                }

                mock_create.return_value = {
                    "backup_file": "backup_2026-01-25_14-30-45.sql",
                    "backup_path": "/app/backups/backup_2026-01-25_14-30-45.sql",
                    "size_bytes": 1048576,
                    "created_at": "2026-01-25T14:30:45Z",
                }

                response = client.post("/backups/create")

                assert response.status_code == 201
                data = response.json()

                backup_data = data["data"]
                assert "backup_file" in backup_data
                assert "backup_path" in backup_data
                assert "size_bytes" in backup_data
                assert "created_at" in backup_data
                assert "management_stats" in backup_data

                stats = backup_data["management_stats"]
                assert stats["total_backups"] == 10
                assert stats["retained"] == 5
                assert stats["archived"] == 3
                assert stats["deleted"] == 2

    def test_create_backup_with_management_stats(self, client: TestClient):
        """Test backup creation with retention policy applied."""
        with patch("src.routes.backups.BackupManager.manage_backups") as mock_manage:
            with patch("src.routes.backups.BackupCreator.create_backup") as mock_create:
                mock_manage.return_value = {
                    "total_backups": 20,
                    "retained": 8,
                    "archived": 10,
                    "deleted": 2,
                }

                mock_create.return_value = {
                    "backup_file": "backup_2026-01-25_15-00-00.sql",
                    "backup_path": "/app/backups/backup_2026-01-25_15-00-00.sql",
                    "size_bytes": 2097152,
                    "created_at": "2026-01-25T15:00:00Z",
                }

                response = client.post("/backups/create")

                assert response.status_code == 201
                backup_data = response.json()["data"]
                stats = backup_data["management_stats"]

                assert stats["total_backups"] == 20
                assert stats["retained"] == 8
                assert stats["archived"] == 10
                assert stats["deleted"] == 2

    def test_create_backup_missing_database_url(self, client: TestClient):
        """Test backup creation fails without DATABASE_URL."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove DATABASE_URL from environment
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

            response = client.post("/backups/create")

            assert response.status_code == 500
            data = response.json()
            assert data["error"] == "CONFIGURATION_ERROR"

    def test_create_backup_handles_management_failure(self, client: TestClient):
        """Test backup creation continues if management fails."""
        with patch("src.routes.backups.BackupManager.manage_backups") as mock_manage:
            with patch("src.routes.backups.BackupCreator.create_backup") as mock_create:
                # Management fails
                from src.utils.backup_manager import BackupManagementError
                mock_manage.side_effect = BackupManagementError("Management failed")

                mock_create.return_value = {
                    "backup_file": "backup_2026-01-25_14-30-45.sql",
                    "backup_path": "/app/backups/backup_2026-01-25_14-30-45.sql",
                    "size_bytes": 524288,
                    "created_at": "2026-01-25T14:30:45Z",
                }

                response = client.post("/backups/create")

                # Should still succeed with default stats
                assert response.status_code == 201
                backup_data = response.json()["data"]
                stats = backup_data["management_stats"]
                assert stats["total_backups"] == 0

    def test_create_backup_creation_failure(self, client: TestClient):
        """Test backup creation fails with proper error."""
        with patch("src.routes.backups.BackupManager.manage_backups") as mock_manage:
            with patch("src.routes.backups.BackupCreator.create_backup") as mock_create:
                mock_manage.return_value = {
                    "total_backups": 5,
                    "retained": 5,
                    "archived": 0,
                    "deleted": 0,
                }

                from src.utils.backup_creator import BackupCreationError
                mock_create.side_effect = BackupCreationError("pg_dump failed: Connection refused")

                response = client.post("/backups/create")

                assert response.status_code == 500
                data = response.json()
                assert data["error"] == "BACKUP_CREATION_ERROR"
                assert "pg_dump failed" in data["message"]

    def test_create_backup_unexpected_error(self, client: TestClient):
        """Test backup creation handles unexpected errors."""
        with patch("src.routes.backups.BackupManager") as mock_manager_class:
            mock_manager_class.side_effect = Exception("Unexpected error")

            response = client.post("/backups/create")

            assert response.status_code == 500
            data = response.json()
            assert data["error"] == "INTERNAL_ERROR"

    def test_create_backup_returns_201_status(self, client: TestClient):
        """Test that successful backup creation returns 201 status code."""
        with patch("src.routes.backups.BackupManager.manage_backups") as mock_manage:
            with patch("src.routes.backups.BackupCreator.create_backup") as mock_create:
                mock_manage.return_value = {
                    "total_backups": 0,
                    "retained": 0,
                    "archived": 0,
                    "deleted": 0,
                }

                mock_create.return_value = {
                    "backup_file": "backup_2026-01-25_14-30-45.sql",
                    "backup_path": "/app/backups/backup_2026-01-25_14-30-45.sql",
                    "size_bytes": 1024,
                    "created_at": "2026-01-25T14:30:45Z",
                }

                response = client.post("/backups/create")

                assert response.status_code == 201
                assert response.headers["content-type"] == "application/json"
