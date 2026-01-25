"""CLI shutdown handler for creating database backups."""

import click
import logging
from src.api_client.client import APIClient

logger = logging.getLogger(__name__)


def handle_shutdown():
    """
    Handle CLI shutdown by creating a database backup.

    This function is called when the user exits the CLI (via 'exit'/'quit'
    commands or Ctrl+C/Ctrl+D). It attempts to create a backup but always
    allows the CLI to exit, regardless of backup success or failure.

    The function:
    1. Creates an API client
    2. Calls POST /backups/create
    3. Displays status message to user
    4. Handles errors gracefully (warnings, not failures)
    5. Always returns (never blocks exit)
    """
    try:
        # Try to create a backup
        _create_backup()
    except Exception as e:
        # Log the error but don't fail exit
        logger.warning(f"Backup failed during shutdown: {str(e)}")
        click.echo(f"Warning: Database backup failed - {str(e)}", err=True)
        # Still allow exit to proceed


def _create_backup():
    """
    Create a backup via the API endpoint.

    Raises:
        Exception: If backup creation fails
    """
    try:
        client = APIClient()
        response = client.post("/backups/create")

        if response.status_code == 201:
            # Backup successful
            data = response.json().get("data", {})
            backup_file = data.get("backup_file", "unknown")
            size_mb = data.get("size_bytes", 0) / (1024 * 1024)
            click.echo(f"✓ Database backed up: {backup_file} ({size_mb:.2f} MB)")

            # Log management stats if available
            stats = data.get("management_stats", {})
            if stats:
                click.echo(
                    f"  Retention: {stats.get('retained', 0)} retained, "
                    f"{stats.get('archived', 0)} archived, "
                    f"{stats.get('deleted', 0)} deleted"
                )
        else:
            # Backup failed
            error_data = response.json()
            error_msg = error_data.get("message", "Unknown error")
            raise Exception(f"Backup API returned {response.status_code}: {error_msg}")

    except Exception as e:
        raise Exception(f"Failed to create backup: {str(e)}")
