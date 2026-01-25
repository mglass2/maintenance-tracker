"""Tests for BackupManager utility."""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.utils.backup_manager import BackupManager, BackupManagementError


@pytest.fixture
def temp_backup_dir():
    """Create temporary backup and archive directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = os.path.join(tmpdir, "backups")
        archive_dir = os.path.join(backup_dir, "archive")
        os.makedirs(backup_dir)
        os.makedirs(archive_dir)
        yield backup_dir, archive_dir


@pytest.fixture
def backup_manager(temp_backup_dir):
    """Create a BackupManager instance with temp directories."""
    backup_dir, archive_dir = temp_backup_dir
    return BackupManager(backup_dir, archive_dir)


class TestBackupManagerInit:
    """Tests for BackupManager initialization."""

    def test_init_creates_directories(self):
        """Test that initialization creates backup directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = os.path.join(tmpdir, "backups")
            archive_dir = os.path.join(backup_dir, "archive")

            manager = BackupManager(backup_dir, archive_dir)

            assert os.path.exists(backup_dir)
            assert os.path.exists(archive_dir)


class TestTimestampParsing:
    """Tests for backup filename timestamp parsing."""

    def test_parse_valid_timestamp(self, backup_manager):
        """Test parsing valid backup filename."""
        filename = "backup_2026-01-25_14-30-45.sql"
        dt = backup_manager._parse_backup_timestamp(filename)

        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 1
        assert dt.day == 25
        assert dt.hour == 14
        assert dt.minute == 30
        assert dt.second == 45

    def test_parse_invalid_filename(self, backup_manager):
        """Test parsing invalid filename returns None."""
        dt = backup_manager._parse_backup_timestamp("not_a_backup.sql")
        assert dt is None

    def test_parse_wrong_prefix(self, backup_manager):
        """Test parsing file without backup_ prefix."""
        dt = backup_manager._parse_backup_timestamp(
            "2026-01-25_14-30-45.sql"
        )
        assert dt is None

    def test_parse_wrong_extension(self, backup_manager):
        """Test parsing file without .sql extension."""
        dt = backup_manager._parse_backup_timestamp(
            "backup_2026-01-25_14-30-45.gz"
        )
        assert dt is None

    def test_parse_malformed_timestamp(self, backup_manager):
        """Test parsing file with malformed timestamp."""
        dt = backup_manager._parse_backup_timestamp(
            "backup_2026-13-45_25-70-80.sql"
        )
        assert dt is None


class TestBackupCategorization:
    """Tests for backup categorization and retention policy."""

    def test_categorize_latest_5(self, backup_manager, temp_backup_dir):
        """Test that latest 5 backups are retained."""
        backup_dir, _ = temp_backup_dir
        now = datetime.utcnow()

        # Create 10 backups over 10 days
        for i in range(10):
            timestamp = now - timedelta(days=i)
            filename = timestamp.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
            filepath = os.path.join(backup_dir, filename)
            Path(filepath).touch()

        # Get all files
        files = [f for f in os.listdir(backup_dir) if f.endswith(".sql")]

        # Categorize
        retained = backup_manager._categorize_backups(files)

        # Should have at least 5 files (latest 5)
        assert len(retained) >= 5

    def test_categorize_weekly(self, backup_manager, temp_backup_dir):
        """Test weekly backup retention."""
        backup_dir, _ = temp_backup_dir
        now = datetime.utcnow()

        # Create backups spanning 4+ weeks
        dates = []
        for week in range(5):
            # Create 3 backups per week
            for day in range(3):
                date = now - timedelta(weeks=week, days=day)
                dates.append(date)

        # Create files
        for date in dates:
            filename = date.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
            filepath = os.path.join(backup_dir, filename)
            Path(filepath).touch()

        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".sql")],
            key=lambda f: backup_manager._parse_backup_timestamp(f),
            reverse=True,
        )

        retained = backup_manager._categorize_backups(files)

        # Should keep at least one from each of the last 4 weeks
        # Plus latest 5, plus monthly backups
        assert len(retained) > len(files) / 3  # Sanity check

    def test_categorize_monthly(self, backup_manager, temp_backup_dir):
        """Test monthly backup retention."""
        backup_dir, _ = temp_backup_dir
        now = datetime.utcnow()

        # Create backups spanning 13+ months
        for month in range(13):
            date = now - timedelta(days=30 * month)
            filename = date.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
            filepath = os.path.join(backup_dir, filename)
            Path(filepath).touch()

        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".sql")],
            key=lambda f: backup_manager._parse_backup_timestamp(f),
            reverse=True,
        )

        retained = backup_manager._categorize_backups(files)

        # Should keep at least one from each of the last 12 months
        # Plus latest 5, plus weekly backups
        assert len(retained) > 5  # At least more than just latest 5


class TestShouldArchive:
    """Tests for archive decision logic."""

    def test_archive_recent_backup(self, backup_manager):
        """Test that recent backup is marked for archiving."""
        filename = "backup_2026-01-24_10-00-00.sql"
        should_archive = backup_manager._should_archive(filename)
        assert should_archive

    def test_archive_old_backup(self, backup_manager):
        """Test that very old backup is marked for deletion."""
        # Create filename for a date 13 months ago
        date = datetime.utcnow() - timedelta(days=400)
        filename = date.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
        should_archive = backup_manager._should_archive(filename)
        assert not should_archive

    def test_archive_unparseable_filename(self, backup_manager):
        """Test that unparseable filename is archived (safe option)."""
        should_archive = backup_manager._should_archive("unknown_file.sql")
        assert should_archive


class TestManageBackups:
    """Tests for full backup management."""

    def test_manage_no_backups(self, backup_manager):
        """Test managing empty backup directory."""
        stats = backup_manager.manage_backups()

        assert stats["total_backups"] == 0
        assert stats["retained"] == 0
        assert stats["archived"] == 0
        assert stats["deleted"] == 0

    def test_manage_creates_archive_dir(self, temp_backup_dir):
        """Test that manage_backups creates archive directory if missing."""
        backup_dir, _ = temp_backup_dir
        archive_dir = os.path.join(backup_dir, "archive")

        # Remove archive dir
        import shutil
        if os.path.exists(archive_dir):
            shutil.rmtree(archive_dir)

        manager = BackupManager(backup_dir, archive_dir)
        manager.manage_backups()

        assert os.path.exists(archive_dir)

    def test_manage_keeps_latest_5(self, backup_manager, temp_backup_dir):
        """Test that manage_backups keeps latest 5 backups."""
        backup_dir, _ = temp_backup_dir
        now = datetime.utcnow()

        # Create 10 backups
        for i in range(10):
            timestamp = now - timedelta(days=i)
            filename = timestamp.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
            filepath = os.path.join(backup_dir, filename)
            Path(filepath).touch()

        stats = backup_manager.manage_backups()

        # Should retain at least 5
        assert stats["retained"] >= 5

        # Total should equal retained + archived + deleted
        assert (
            stats["total_backups"]
            == stats["retained"] + stats["archived"] + stats["deleted"]
        )

    def test_manage_archives_old_backups(self, backup_manager, temp_backup_dir):
        """Test that old backups are archived."""
        backup_dir, archive_dir = temp_backup_dir
        now = datetime.utcnow()

        # Create 15 backups over 15 days
        for i in range(15):
            timestamp = now - timedelta(days=i)
            filename = timestamp.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
            filepath = os.path.join(backup_dir, filename)
            Path(filepath).touch()

        stats = backup_manager.manage_backups()

        # Should have archived some backups
        assert stats["archived"] > 0

        # Archive directory should have files
        archived_files = os.listdir(archive_dir)
        assert len(archived_files) > 0

    def test_manage_deletes_old_archives(self, backup_manager, temp_backup_dir):
        """Test that very old archived backups are deleted."""
        backup_dir, archive_dir = temp_backup_dir
        now = datetime.utcnow()

        # Create a backup in archive that's 13 months old
        old_date = now - timedelta(days=400)
        old_filename = old_date.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
        old_filepath = os.path.join(archive_dir, old_filename)
        Path(old_filepath).touch()

        # Create a recent backup in archive
        recent_date = now - timedelta(days=10)
        recent_filename = recent_date.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
        recent_filepath = os.path.join(archive_dir, recent_filename)
        Path(recent_filepath).touch()

        # Run management
        stats = backup_manager.manage_backups()

        # Old archive should be deleted
        assert not os.path.exists(old_filepath)

        # Recent archive should exist
        assert os.path.exists(recent_filepath)

        # Stats should show deletion
        assert stats["deleted"] > 0

    def test_manage_statistics_correct(self, backup_manager, temp_backup_dir):
        """Test that statistics are correct."""
        backup_dir, _ = temp_backup_dir
        now = datetime.utcnow()

        initial_count = 20

        # Create 20 backups over 20 days
        for i in range(initial_count):
            timestamp = now - timedelta(days=i)
            filename = timestamp.strftime("backup_%Y-%m-%d_%H-%M-%S.sql")
            filepath = os.path.join(backup_dir, filename)
            Path(filepath).touch()

        stats = backup_manager.manage_backups()

        # Total should match input count
        assert stats["total_backups"] == initial_count

        # All backups should be accounted for
        assert (
            stats["retained"]
            + stats["archived"]
            + stats["deleted"]
            == initial_count
        )
