"""Implements SpellNotification model."""
from django.db import models
from .spell import Spell


class SpellNotification(models.Model):
    """Auto notification for spells."""

    class EveryType(models.TextChoices):
        """Period to show notification."""

        DAY = "D"
        WEEK = "W"
        MONTH = "M"
        YEAR = "Y"
        SINGLE = "S"

    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, on_delete=models.CASCADE
    )
    datetime: models.DateTimeField = models.DateTimeField()
    every: models.CharField = models.CharField(
        max_length=1, choices=EveryType.choices, default=EveryType.SINGLE
    )
    message: models.CharField = models.CharField(max_length=256)
