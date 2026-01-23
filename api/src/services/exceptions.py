"""Custom exceptions for service layer."""


class DuplicateEmailError(Exception):
    """Raised when attempting to create a user with an email that already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email '{email}' already exists")
