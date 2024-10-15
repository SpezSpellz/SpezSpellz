"""Implements RateCategory model."""
from django.db import models
from .spell import Spell
from .rate import Rate


class RateCategory(Rate):
    """When someone rates a category."""

    subject: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )
