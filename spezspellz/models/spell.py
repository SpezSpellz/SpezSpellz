"""Implements Spell model."""
from typing import cast, Any
from django.contrib.auth.models import User
from django.db import models
from .category import Category


class Spell(models.Model):
    """The model that stores spells."""

    creator: models.ForeignKey[User] = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    title: models.CharField = models.CharField(max_length=50)
    data: models.CharField = models.CharField(max_length=4096 * 10)
    thumbnail: models.FileField = models.FileField(
        upload_to="content", null=True
    )
    category: models.ForeignKey[Category] = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self) -> str:
        """Return the spell title."""
        return str(self.title)

    @property
    def sorted_tags(self):
        """Return HasTag objects sorted by rating descending."""
        return self.hastag_set.order_by("-rating")

    def calc_avg_stars(self) -> float:
        """Calculate average stars for a spell."""
        from .review import Review
        return Review.calc_avg_stars(self)

    def calc_category_rating(self) -> int:
        """Calculate the category rating."""
        return cast(Any, self).ratecategory_set.filter(positive=True).count(
        ) - cast(Any, self).ratecategory_set.filter(positive=False).count()

    @property
    def summary(self):
        """Find a possible summary of the spell."""
        start = self.data.find("is ") or 0
        end = start + (self.data[start:].find(".") or (len(self.data) - start))
        return self.data[start:end].replace("#", "")
