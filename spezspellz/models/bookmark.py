"""Implements Bookmark model."""
from django.contrib.auth.models import User
from django.db import models
from .spell import Spell


class Bookmark(models.Model):
    """Collection of spell that a user had saved as bookmark."""

    user: models.ForeignKey[User] = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE
    )
    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )

    def __str__(self):
        """Return bookmark as a string."""
        return f"Bookmark(spell={self.spell.pk}, user={self.user.pk})"
