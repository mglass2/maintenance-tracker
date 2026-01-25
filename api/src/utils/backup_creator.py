"""Database backup creation utility."""

import os
import subprocess
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BackupCreationError(Exception):
    """Raised when backup creation fails."""
    pass


class PGDumpNotFoundError(BackupCreationError):
    """Raised when pg_dump is not available."""
    pass


class BackupCreator:
    """Creates SQL backups of the database using pg_dump."""

    def __init__(self, database_url: str, backup_dir: str = "/app/backups"):
        """Initialize the backup creator.

        Args:
            database_url: PostgreSQL connection string (DATABASE_URL environment variable)
            backup_dir: Directory to store backups

        Raises:
            ValueError: If database_url is invalid
            InvalidBackupDirectoryError: If backup_dir doesn't exist
        """
        if not database_url:
            raise ValueError("database_url cannot be empty")

        self.database_url = database_url
        self.backup_dir = backup_dir

        # Verify backup directory exists
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)

        # Verify pg_dump is available
        try:
            subprocess.run(["which", "pg_dump"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise PGDumpNotFoundError("pg_dump not found. Install postgresql-client package.")

    def create_backup(self) -> dict:
        """Create a SQL backup of the database.

        Returns:
            Dictionary with backup file info:
            {
                'backup_file': 'backup_2026-01-25_14-30-45.sql',
                'backup_path': '/app/backups/backup_2026-01-25_14-30-45.sql',
                'size_bytes': 524288,
                'created_at': '2026-01-25T14:30:45Z'
            }

        Raises:
            BackupCreationError: If pg_dump fails
        """
        # Generate backup filename
        backup_filename = self._generate_backup_filename()
        backup_path = os.path.join(self.backup_dir, backup_filename)

        # Parse database connection details
        db_params = self._parse_database_url()

        # Prepare environment with password
        env = os.environ.copy()
        if db_params.get("password"):
            env["PGPASSWORD"] = db_params["password"]

        # Build pg_dump command
        command = [
            "pg_dump",
            "-h", db_params["host"],
            "-p", str(db_params["port"]),
            "-U", db_params["user"],
            "-d", db_params["database"],
            "--clean",
            "--if-exists",
            "--create",
            "--inserts",
        ]

        try:
            # Execute pg_dump
            with open(backup_path, "w") as backup_file:
                result = subprocess.run(
                    command,
                    stdout=backup_file,
                    stderr=subprocess.PIPE,
                    timeout=300,
                    env=env,
                    text=True,
                )

            if result.returncode != 0:
                # Clean up failed backup file
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                raise BackupCreationError(
                    f"pg_dump failed with code {result.returncode}: {result.stderr}"
                )

            # Get file info
            file_size = os.path.getsize(backup_path)
            created_at = datetime.utcnow().isoformat() + "Z"

            logger.info(f"Backup created: {backup_filename} ({file_size} bytes)")

            return {
                "backup_file": backup_filename,
                "backup_path": backup_path,
                "size_bytes": file_size,
                "created_at": created_at,
            }

        except subprocess.TimeoutExpired:
            # Clean up timed out backup file
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise BackupCreationError("pg_dump timed out (exceeded 5 minutes)")
        except Exception as e:
            # Clean up any failed backup file
            if os.path.exists(backup_path):
                os.remove(backup_path)
            if isinstance(e, BackupCreationError):
                raise
            raise BackupCreationError(f"Unexpected error during backup: {str(e)}")

    def _parse_database_url(self) -> dict:
        """Parse PostgreSQL connection string.

        Expected format: postgresql://user:password@host:port/database

        Returns:
            Dictionary with connection parameters

        Raises:
            ValueError: If URL format is invalid
        """
        url = self.database_url

        # Remove the postgresql:// prefix
        if url.startswith("postgresql://"):
            url = url[13:]
        elif url.startswith("postgres://"):
            url = url[11:]
        else:
            raise ValueError(f"Invalid database URL format: {self.database_url}")

        # Split user/password from host/database
        if "@" not in url:
            raise ValueError(f"Invalid database URL format: {self.database_url}")

        credentials, host_db = url.split("@", 1)

        # Parse credentials
        if ":" in credentials:
            user, password = credentials.split(":", 1)
        else:
            user = credentials
            password = None

        # Parse host and database
        if "/" not in host_db:
            raise ValueError(f"Invalid database URL format: {self.database_url}")

        host_port, database = host_db.rsplit("/", 1)

        # Parse host and port
        if ":" in host_port:
            host, port = host_port.rsplit(":", 1)
            try:
                port = int(port)
            except ValueError:
                raise ValueError(f"Invalid port in database URL: {self.database_url}")
        else:
            host = host_port
            port = 5432  # Default PostgreSQL port

        return {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "database": database,
        }

    def _generate_backup_filename(self) -> str:
        """Generate backup filename with timestamp.

        Format: backup_YYYY-MM-DD_HH-MM-SS.sql

        Returns:
            Backup filename
        """
        now = datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        return f"backup_{timestamp}.sql"
