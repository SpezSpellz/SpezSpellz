from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count
from .spell import Spell


class Success(models.Model):
    """Model to store a user's success rating for a specific spell."""

    user: models.ForeignKey[User] = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, on_delete=models.CASCADE
    )
    rating: models.IntegerField = models.IntegerField(
        choices=[(i, str(i)) for i in range(5)],
        default=0
    )

    class Meta:
        unique_together = ('user', 'spell')

    def __str__(self) -> str:
        """Return the user's rating for the spell."""
        return f"User: {self.user.username}, Spell: {self.spell.title}, Rating: {self.rating}"

    @staticmethod
    def spell_successrate(spell: Spell) -> float:
        """
        Calculate the success rate of a spell based on the average rating of all users.
        """
        avg_rating = Success.objects.filter(spell=spell).aggregate(Avg('rating'))['rating__avg']
        if avg_rating is None:
            return 100.0

        success_rate = (avg_rating / 4) * 100
        return min(success_rate, 100.0)

    @staticmethod
    def user_successrate(creator: User) -> float:
        """
        Calculate the success rate for the creator based on the success rates of all their spells.
        """
        spells = Spell.objects.filter(creator=creator)

        if not spells.exists():
            return 0.0

        total_success_rate = 0.0
        spell_count = 0

        for spell in spells:
            success_rate = Success.spell_successrate(spell)
            total_success_rate += success_rate
            spell_count += 1

        return total_success_rate / spell_count