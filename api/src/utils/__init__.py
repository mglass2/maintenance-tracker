"""Utils module for response formatting and helpers."""

from .responses import success_response, error_response

__all__ = ["success_response", "error_response", "IntervalPredictor"]


def __getattr__(name):
    """Lazy import of IntervalPredictor to avoid circular imports."""
    if name == "IntervalPredictor":
        from .interval_predictor import IntervalPredictor
        return IntervalPredictor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
