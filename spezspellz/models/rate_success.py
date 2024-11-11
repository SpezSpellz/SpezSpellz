"""Implements RateSuccess model."""
from django.db import models
from .spell import Spell
from .rate import Rate


class RateSuccess(Rate):
    """When someone rates that the spell succeed."""

    subject: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )
