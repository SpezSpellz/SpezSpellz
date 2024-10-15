"""Implements Review model."""
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from .spell import Spell


class Review(models.Model):
    """Collection of reviews for spells."""

    user: models.ForeignKey[User] = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE
    )
    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )
    desc: models.CharField = models.CharField(max_length=256, null=True)
    # Lowest 0 star highest 9 star
    star: models.SmallIntegerField = models.SmallIntegerField()

    @staticmethod
    def calc_avg_stars(spell: Spell) -> float:
        """Calculate average star."""
        spell_review = Review.objects.filter(spell=spell)
        avg_star = spell_review.aggregate(Avg('star'))['star__avg']
        if avg_star is None:
            avg_star = 9
        return round(avg_star * .5 + .5, 2)

    def __str__(self):
        """Return a review for a spell."""
        return f"Spell: {self.spell}/ User: {self.user}/ Rating: {self.star}"
