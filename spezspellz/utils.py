"""Implements utility functions, classes, and methods."""


def safe_cast(t, val, default=None):
    """Attempt to cast or else return default."""
    try:
        return t(val)
    except Exception:
        return default
