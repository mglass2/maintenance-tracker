"""Backup management routes."""

import os
import logging
from fastapi import APIRouter, status

try:
    from ..utils.backup_creator import BackupCreator, BackupCreationError
    from ..utils.backup_manager import BackupManager, BackupManagementError
    from ..utils.responses import success_response, error_response
except ImportError:
    from utils.backup_creator import BackupCreator, BackupCreationError
    from utils.backup_manager import BackupManager, BackupManagementError
    from utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backups", tags=["backups"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_backup_endpoint():
    """
    Create a database backup and apply retention policy.

    Process:
    1. Apply retention policy to existing backups
    2. Create new backup via pg_dump
    3. Return backup information and statistics

    Returns:
        201 Created with backup file info and management statistics

    Error responses:
        - 500 Internal Server Error: Backup creation or management failed
    """
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return error_response(
                error="CONFIGURATION_ERROR",
                message="DATABASE_URL environment variable not set",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Initialize backup manager and apply retention policy
        backup_manager = BackupManager()
        try:
            management_stats = backup_manager.manage_backups()
            logger.info(f"Backup management completed: {management_stats}")
        except BackupManagementError as e:
            logger.error(f"Backup management failed: {str(e)}")
            # Don't fail the whole operation if management fails
            management_stats = {
                "total_backups": 0,
                "retained": 0,
                "archived": 0,
                "deleted": 0,
            }

        # Initialize backup creator and create new backup
        try:
            backup_creator = BackupCreator(database_url)
            backup_info = backup_creator.create_backup()
        except BackupCreationError as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return error_response(
                error="BACKUP_CREATION_ERROR",
                message=f"Database backup failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Combine backup info with management statistics
        response_data = {
            "backup_file": backup_info["backup_file"],
            "backup_path": backup_info["backup_path"],
            "size_bytes": backup_info["size_bytes"],
            "created_at": backup_info["created_at"],
            "management_stats": management_stats,
        }

        return success_response(
            data=response_data,
            message="Database backup created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Unexpected error during backup: {str(e)}", exc_info=True)
        return error_response(
            error="INTERNAL_ERROR",
            message=f"An unexpected error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
