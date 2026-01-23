"""Tests for user service business logic."""

import pytest
from sqlalchemy.orm import Session

from models.user import User
from schemas.users import UserCreateRequest
from services.user_service import create_user
from services.exceptions import DuplicateEmailError


class TestCreateUser:
    """Tests for create_user service function."""

    def test_create_user_success(self, db: Session):
        """Test successful user creation."""
        user_data = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )

        user = create_user(db, user_data)

        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.is_deleted is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_user_populates_timestamps(self, db: Session):
        """Test that created_at and updated_at are set."""
        user_data = UserCreateRequest(
            name="Jane Doe",
            email="jane@example.com",
        )

        user = create_user(db, user_data)

        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_user_with_default_is_deleted_false(self, db: Session):
        """Test that is_deleted defaults to False."""
        user_data = UserCreateRequest(
            name="Bob Smith",
            email="bob@example.com",
        )

        user = create_user(db, user_data)

        assert user.is_deleted is False

    def test_create_user_duplicate_email_raises_error(self, db: Session):
        """Test that creating user with duplicate email raises DuplicateEmailError."""
        # Create first user
        user_data1 = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )
        create_user(db, user_data1)

        # Try to create second user with same email
        user_data2 = UserCreateRequest(
            name="Jane Doe",
            email="john@example.com",
        )

        with pytest.raises(DuplicateEmailError) as exc_info:
            create_user(db, user_data2)

        assert "john@example.com" in str(exc_info.value)

    def test_create_user_with_deleted_user_same_email(self, db: Session):
        """Test that email uniqueness is enforced at database level.

        Even when a user is soft-deleted, the UNIQUE constraint on email
        prevents another user from using that same email. The IntegrityError
        from the database is caught and re-raised as DuplicateEmailError.
        """
        # Create and delete first user
        user_data1 = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )
        user1 = create_user(db, user_data1)
        user1.is_deleted = True
        db.commit()

        # Create second user with same email will fail due to UNIQUE constraint
        user_data2 = UserCreateRequest(
            name="Jane Doe",
            email="john@example.com",
        )

        # The database UNIQUE constraint is enforced regardless of soft delete
        try:
            create_user(db, user_data2)
            pytest.fail("Expected DuplicateEmailError")
        except DuplicateEmailError:
            pass  # This is expected

    def test_create_user_email_normalization(self, db: Session):
        """Test that email is normalized to lowercase."""
        user_data = UserCreateRequest(
            name="Test User",
            email="Test@EXAMPLE.COM",
        )

        user = create_user(db, user_data)

        assert user.email == "test@example.com"

    def test_create_user_persists_to_database(self, db: Session):
        """Test that created user is persisted to database."""
        user_data = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )
        user = create_user(db, user_data)

        # Query the database to verify persistence
        queried_user = db.query(User).filter(User.id == user.id).first()

        assert queried_user is not None
        assert queried_user.name == "John Doe"
        assert queried_user.email == "john@example.com"

    def test_create_multiple_users_with_different_emails(self, db: Session):
        """Test creating multiple users with different emails."""
        user_data1 = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )
        user1 = create_user(db, user_data1)

        user_data2 = UserCreateRequest(
            name="Jane Doe",
            email="jane@example.com",
        )
        user2 = create_user(db, user_data2)

        assert user1.id != user2.id
        assert user1.email != user2.email

        # Verify both exist in database
        assert db.query(User).count() == 2

    def test_create_user_with_whitespace_in_name(self, db: Session):
        """Test that whitespace is handled correctly in name."""
        user_data = UserCreateRequest(
            name="  John  Doe  ",
            email="john@example.com",
        )

        user = create_user(db, user_data)

        # Name should be stripped
        assert user.name == "John  Doe"

    def test_case_insensitive_email_uniqueness(self, db: Session):
        """Test that email uniqueness check is case-insensitive."""
        user_data1 = UserCreateRequest(
            name="John Doe",
            email="john@example.com",
        )
        create_user(db, user_data1)

        # Try with uppercase variant
        user_data2 = UserCreateRequest(
            name="Jane Doe",
            email="JOHN@EXAMPLE.COM",
        )

        with pytest.raises(DuplicateEmailError):
            create_user(db, user_data2)
