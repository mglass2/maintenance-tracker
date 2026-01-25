"""Database backup management and retention policy."""

import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class BackupManagementError(Exception):
    """Raised when backup management fails."""
    pass


class BackupManager:
    """Manages backup files according to retention policy."""

    def __init__(
        self,
        backup_dir: str = "/app/backups",
        archive_dir: str = "/app/backups/archive",
    ):
        """Initialize the backup manager.

        Args:
            backup_dir: Directory containing active backups
            archive_dir: Directory for archived backups
        """
        self.backup_dir = backup_dir
        self.archive_dir = archive_dir

        # Create directories if they don't exist
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        Path(self.archive_dir).mkdir(parents=True, exist_ok=True)

    def manage_backups(self) -> dict:
        """Apply retention policy to existing backups.

        Retention policy:
        - Keep latest 5 backups (always)
        - Keep latest backup per week (ISO week) for last 4 weeks
        - Keep latest backup per month for last 12 months
        - Archive all other backups to archive/ directory
        - Delete archived backups older than 12 months

        Returns:
            Statistics dictionary:
            {
                'total_backups': 10,
                'retained': 5,
                'archived': 3,
                'deleted': 2
            }

        Raises:
            BackupManagementError: If management fails
        """
        try:
            # Get all backup files
            backup_files = self._get_backup_files()

            if not backup_files:
                logger.info("No backups to manage")
                return {
                    "total_backups": 0,
                    "retained": 0,
                    "archived": 0,
                    "deleted": 0,
                }

            # Categorize backups into retention buckets
            retained_files = self._categorize_backups(backup_files)

            # Track statistics
            stats = {
                "total_backups": len(backup_files),
                "retained": 0,
                "archived": 0,
                "deleted": 0,
            }

            # Process each backup file
            for backup_file in backup_files:
                if backup_file in retained_files:
                    # Keep this file in active backups
                    stats["retained"] += 1
                else:
                    # Archive or delete this file
                    # Determine current location of file
                    backup_path = os.path.join(self.backup_dir, backup_file)
                    archive_path = os.path.join(self.archive_dir, backup_file)

                    if os.path.exists(backup_path):
                        # File is in active backups directory
                        if self._should_archive(backup_file):
                            # Move to archive
                            shutil.move(backup_path, archive_path)
                            stats["archived"] += 1
                            logger.info(f"Archived backup: {backup_file}")
                        else:
                            # Delete old backup from active
                            os.remove(backup_path)
                            stats["deleted"] += 1
                            logger.info(f"Deleted old backup: {backup_file}")
                    elif os.path.exists(archive_path):
                        # File is in archive directory
                        if not self._should_archive(backup_file):
                            # Delete old archived backup
                            os.remove(archive_path)
                            stats["deleted"] += 1
                            logger.info(f"Deleted old archived backup: {backup_file}")

            # Clean up old archived backups (>12 months)
            deleted_count = self._clean_old_archives()
            stats["deleted"] += deleted_count

            logger.info(f"Backup management complete: {stats}")
            return stats

        except Exception as e:
            if isinstance(e, BackupManagementError):
                raise
            raise BackupManagementError(f"Failed to manage backups: {str(e)}")

    def _get_backup_files(self) -> list:
        """Get all backup files from both backup and archive directories.

        Returns:
            List of backup filenames, sorted by timestamp (newest first)
        """
        files = []

        # Get files from active backups directory
        if os.path.exists(self.backup_dir):
            files.extend(
                [f for f in os.listdir(self.backup_dir) if f.endswith(".sql")]
            )

        # Get files from archive directory
        if os.path.exists(self.archive_dir):
            files.extend(
                [f for f in os.listdir(self.archive_dir) if f.endswith(".sql")]
            )

        # Sort by timestamp (newest first)
        files.sort(
            key=lambda f: self._parse_backup_timestamp(f), reverse=True
        )

        return files

    def _categorize_backups(self, backup_files: list) -> set:
        """Categorize backups into retention buckets.

        Retention buckets:
        1. Latest 5 backups (most recent)
        2. Latest backup per ISO week for last 4 weeks
        3. Latest backup per month for last 12 months

        Args:
            backup_files: List of backup filenames, sorted by timestamp (newest)

        Returns:
            Set of filenames to retain
        """
        retained = set()
        now = datetime.utcnow()

        # Bucket 1: Latest 5 backups
        latest_count = min(5, len(backup_files))
        for i in range(latest_count):
            retained.add(backup_files[i])

        # Bucket 2: Latest per week (last 4 weeks)
        weeks_seen = set()
        for backup_file in backup_files:
            timestamp = self._parse_backup_timestamp(backup_file)
            if not timestamp:
                continue

            # Check if within last 4 weeks
            age = now - timestamp
            if age > timedelta(weeks=4):
                break

            # Get ISO calendar week
            iso_year, iso_week, _ = timestamp.isocalendar()
            week_key = (iso_year, iso_week)

            if week_key not in weeks_seen:
                retained.add(backup_file)
                weeks_seen.add(week_key)

        # Bucket 3: Latest per month (last 12 months)
        months_seen = set()
        for backup_file in backup_files:
            timestamp = self._parse_backup_timestamp(backup_file)
            if not timestamp:
                continue

            # Check if within last 12 months
            age = now - timestamp
            if age > timedelta(days=365):
                break

            # Get month key
            month_key = (timestamp.year, timestamp.month)

            if month_key not in months_seen:
                retained.add(backup_file)
                months_seen.add(month_key)

        return retained

    def _should_archive(self, backup_file: str) -> bool:
        """Determine if a backup should be archived (not deleted).

        Args:
            backup_file: Backup filename

        Returns:
            True if backup should be archived, False if it should be deleted
        """
        timestamp = self._parse_backup_timestamp(backup_file)
        if not timestamp:
            # If we can't parse the timestamp, archive it to be safe
            return True

        age = datetime.utcnow() - timestamp

        # Archive if less than 12 months old, delete if older
        return age <= timedelta(days=365)

    def _clean_old_archives(self) -> int:
        """Delete archived backups older than 12 months.

        Returns:
            Number of archived backups deleted
        """
        deleted_count = 0
        now = datetime.utcnow()

        if not os.path.exists(self.archive_dir):
            return 0

        for backup_file in os.listdir(self.archive_dir):
            if not backup_file.endswith(".sql"):
                continue

            backup_path = os.path.join(self.archive_dir, backup_file)
            timestamp = self._parse_backup_timestamp(backup_file)

            if timestamp:
                age = now - timestamp
                if age > timedelta(days=365):
                    try:
                        os.remove(backup_path)
                        deleted_count += 1
                        logger.info(f"Deleted old archived backup: {backup_file}")
                    except Exception as e:
                        logger.error(f"Failed to delete {backup_file}: {str(e)}")

        return deleted_count

    def _parse_backup_timestamp(self, backup_file: str) -> datetime:
        """Parse timestamp from backup filename.

        Expected format: backup_YYYY-MM-DD_HH-MM-SS.sql

        Args:
            backup_file: Backup filename

        Returns:
            datetime object or None if parsing fails
        """
        if not backup_file.startswith("backup_") or not backup_file.endswith(".sql"):
            return None

        try:
            # Remove 'backup_' prefix and '.sql' suffix
            timestamp_str = backup_file[7:-4]  # Remove 'backup_' (7 chars) and '.sql' (4 chars)

            # Parse timestamp: YYYY-MM-DD_HH-MM-SS
            return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        except (ValueError, IndexError):
            logger.warning(f"Could not parse timestamp from backup file: {backup_file}")
            return None
