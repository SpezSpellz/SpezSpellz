"""Implement SuccessRate Model."""
from typing import cast
from django.contrib.auth.models import User
from django.db import models
from .spell import Spell


class SuccessRate(models.Model):
    """Model to store a user's success rating for a specific spell."""

    user: models.ForeignKey[User] = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, on_delete=models.CASCADE
    )
    rating: models.IntegerField = models.IntegerField(
        default=0
    )

    class Meta:
        """Describe the Model's properties."""

        unique_together = ('user', 'spell')

    def __str__(self) -> str:
        """Return the user's rating for the spell."""
        return f"User: {cast(User, self.user).username}, Spell: {cast(Spell, self.spell).title}, Rating: {self.rating}"
