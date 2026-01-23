"""Session management for CLI user identity.

Stores the active user for the current CLI session.
Session state is not persisted between CLI restarts.
"""

from typing import Optional

# Global session state (cleared on CLI restart)
_active_user_id: Optional[int] = None
_active_user_data: Optional[dict] = None


def set_active_user(user_id: int, user_data: dict) -> None:
    """Set the active user for this session."""
    global _active_user_id, _active_user_data
    _active_user_id = user_id
    _active_user_data = user_data


def get_active_user_id() -> Optional[int]:
    """Get the active user ID, or None if no user is selected."""
    return _active_user_id


def get_active_user_data() -> Optional[dict]:
    """Get the active user data, or None if no user is selected."""
    return _active_user_data


def clear_session() -> None:
    """Clear the session state."""
    global _active_user_id, _active_user_data
    _active_user_id = None
    _active_user_data = None


def is_authenticated() -> bool:
    """Check if a user is currently selected."""
    return _active_user_id is not None
