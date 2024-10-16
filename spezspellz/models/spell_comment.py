"""Implements SpellComment model."""
from django.contrib.auth.models import User
from django.db import models
from .spell import Spell


class SpellComment(models.Model):
    """A comment for spell."""

    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )
    commenter: models.ForeignKey[User] = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    text: models.CharField = models.CharField(max_length=500)
