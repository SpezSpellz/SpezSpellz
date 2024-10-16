"""Implements RateTag model."""
from django.db import models
from .has_tag import HasTag
from .rate import Rate


class RateTag(Rate):
    """When someone rates a tag."""

    subject: models.ForeignKey[HasTag] = models.ForeignKey(
        HasTag, null=False, on_delete=models.CASCADE
    )
