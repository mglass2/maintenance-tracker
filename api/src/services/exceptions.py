"""Custom exceptions for service layer."""


class DuplicateEmailError(Exception):
    """Raised when attempting to create a user with an email that already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email '{email}' already exists")


class ResourceNotFoundError(Exception):
    """Raised when a referenced resource (user, item_type, etc.) is not found."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class DuplicateNameError(Exception):
    """Raised when attempting to create an item type with a name that already exists."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidForecastDataError(Exception):
    """Raised when forecast data is missing or malformed."""

    pass


class MissingForecastKeyError(Exception):
    """Raised when required forecast key is missing."""

    pass
