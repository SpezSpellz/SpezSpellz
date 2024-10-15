"""Implements HasTag model."""
from typing import cast, Any
from django.db import models
from .spell import Spell
from .tag import Tag


class HasTag(models.Model):
    """Whether a spell has a tag and the rating of the tag for that spell."""

    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, null=False, on_delete=models.CASCADE
    )
    tag: models.ForeignKey[Tag] = models.ForeignKey(
        Tag, null=False, on_delete=models.CASCADE
    )

    def calc_rating(self) -> int:
        """Calculate the rating."""
        return cast(Any, self).ratetag_set.filter(
            positive=True
        ).count() - cast(Any, self).ratetag_set.filter(positive=False).count()
