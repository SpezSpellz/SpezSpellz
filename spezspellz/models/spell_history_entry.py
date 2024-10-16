"""Implements SpellHistoryEntry model."""
from django.contrib.auth.models import User
from django.db import models
from .spell import Spell


class SpellHistoryEntry(models.Model):
    """An entry in the spell history."""

    user: models.ForeignKey[User] = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE
    )
    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )
    time: models.DateTimeField = models.DateTimeField()
