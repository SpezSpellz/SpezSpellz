"""This file contains models."""
from django.db import models


class Category(models.Model):
    """The category."""

    name: models.CharField = models.CharField(max_length=50)


class Spell(models.Model):
    """The model that stores spells."""

    title: models.CharField = models.CharField(max_length=50)
    data: models.CharField = models.CharField(max_length=4096 * 10)
    thumbnail: models.BinaryField = models.BinaryField(
        max_length=4096 * 1221,
        null=True
    )
    category: models.ForeignKey[Category] = models.ForeignKey(
        Category, null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self) -> str:
        """Return the spell title."""
        return str(self.title)

    @property
    def sorted_tags(self):
        """Return HasTag objects sorted by rating descending."""
        return self.hastag_set.order_by("-rating")


class Tag(models.Model):
    """The tag."""

    name: models.CharField = models.CharField(max_length=50)


class HasTag(models.Model):
    """Whether a spell has a tag and the rating of the tag for that spell."""

    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell,
        null=False,
        on_delete=models.CASCADE
    )
    tag: models.ForeignKey[Tag] = models.ForeignKey(
        Tag,
        null=False,
        on_delete=models.CASCADE
    )
    rating: models.IntegerField = models.IntegerField()
