"""This file contains models."""
from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    """The category."""

    name: models.CharField = models.CharField(max_length=50)


class UserInfo(models.Model):
    """Store the user info."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    privacy = models.BooleanField(default=False)
    notification = models.BooleanField(default=True)
    user_desc = models.CharField(max_length=400)

    def __str__(self):
        return self.user.username + " Info"


class Spell(models.Model):
    """The model that stores spells."""

    creator: models.ForeignKey[User] = models.ForeignKey(User, on_delete=models.CASCADE)
    title: models.CharField = models.CharField(max_length=50)
    data: models.CharField = models.CharField(max_length=4096 * 10)
    thumbnail: models.BinaryField = models.BinaryField(
        max_length=4096 * 1221,
        null=True
    )
    category: models.ForeignKey[Category] = models.ForeignKey(
        Category, null=True, blank=True,
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
    # +1 for YES -1 for NO
