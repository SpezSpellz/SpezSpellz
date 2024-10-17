"""Implements SpellNotification model."""
from django.db import models
from enum import Enum
from dateutil.relativedelta import relativedelta
from .spell import Spell


class Repetition(Enum):
    """Enum used for updating datetime."""
    D = {"days": 1}
    W = {"weeks": 1}
    M = {"months": 1}
    Y = {"years": 1}
    S = {"days": 0}


class SpellNotification(models.Model):
    """Auto notification for spells."""

    class EveryType(models.TextChoices):
        """Period to show notification."""

        DAY = "Repetition.D"
        WEEK = "Repetition.W"
        MONTH = "Repetition.M"
        YEAR = "Repetition.Y"
        SINGLE = "Repetition.S"

    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, on_delete=models.CASCADE
    )
    datetime: models.DateTimeField = models.DateTimeField()
    every: models.CharField = models.CharField(
        max_length=12, choices=EveryType.choices, default=EveryType.SINGLE
    )
    message: models.CharField = models.CharField(max_length=256)

    @property
    def repetition(self):
        return eval(self.every).value

    def update_datetime(self):
        self.datetime += relativedelta(**self.repetition)
