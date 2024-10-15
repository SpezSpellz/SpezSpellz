"""Implements utility functions, classes, and methods."""
from typing import TypeVar, Optional, cast
from django.db import models


def safe_cast(t, val, default=None):
    """Attempt to cast or else return default."""
    try:
        return t(val)
    except Exception:
        return default


ModelClass = TypeVar('ModelClass')


def get_or_none(model_class: type[ModelClass],
                **kwargs) -> Optional[ModelClass]:
    """Get a model, returns None if not found.

    Args:
        model_class (class): The model class to get.

    Returns:
        model_class | None: The obtained model class or None
    """
    try:
        return cast(
            ModelClass,
            cast(models.Model, model_class).objects.get(**kwargs)
        )
    except cast(models.Model, model_class).DoesNotExist:
        return None
