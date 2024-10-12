"""This file contains models."""
from typing import Optional, cast, TypeVar
from django.contrib.auth.models import User
from django.db import models


ModelClass = TypeVar('ModelClass')


def get_or_none(model_class: type[ModelClass], **kwargs) -> Optional[ModelClass]:
    """Get a model, returns None if not found.

    Args:
        model_class (class): The model class to get.

    Returns:
        model_class | None: The obtained model class or None
    """
    try:
        return cast(ModelClass, cast(models.Model, model_class).objects.get(**kwargs))
    except cast(models.Model, model_class).DoesNotExist:
        return None


class Category(models.Model):
    """The category."""

    name: models.CharField = models.CharField(max_length=50)

    def __str__(self):
        """Return the category name."""
        return str(self.name)


class UserInfo(models.Model):
    """Store the user info."""

    user: models.OneToOneField[User] = models.OneToOneField(User, on_delete=models.CASCADE)
    private: models.BooleanField = models.BooleanField(default=False)
    timed_notification: models.BooleanField = models.BooleanField(default=True)
    review_comment_notification: models.BooleanField = models.BooleanField(default=True)
    spell_review_notification: models.BooleanField = models.BooleanField(default=True)
    spell_comment_notification: models.BooleanField = models.BooleanField(default=True)
    user_desc: models.CharField = models.CharField(default="", max_length=400)

    def __str__(self):
        """Return user info as string."""
        return f"UserInfo(username={self.user.username})"


class Spell(models.Model):
    """The model that stores spells."""

    creator: models.ForeignKey[User] = models.ForeignKey(User, on_delete=models.CASCADE)
    title: models.CharField = models.CharField(max_length=50)
    data: models.CharField = models.CharField(max_length=4096 * 10)
    thumbnail: models.FileField = models.FileField(
        upload_to="content",
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

    @property
    def summary(self):
        """Find a possible summary of the spell."""
        return self.data[(self.data.find("is") or 0):]


class Tag(models.Model):
    """The tag."""

    name: models.CharField = models.CharField(max_length=50)

    def __str__(self):
        """Return the tag name."""
        return str(self.name)


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


class SpellNotification(models.Model):
    """Auto notification for spells."""

    class EveryType(models.TextChoices):
        """Period to show notification."""

        DAY = "D"
        WEEK = "W"
        MONTH = "M"
        YEAR = "Y"
        SINGLE = "S"

    spell: models.ForeignKey[Spell] = models.ForeignKey(Spell, on_delete=models.CASCADE)
    datetime: models.DateTimeField = models.DateTimeField()
    every: models.CharField = models.CharField(max_length=1, choices=EveryType.choices, default=EveryType.SINGLE)
    message: models.CharField = models.CharField(max_length=256)


class Attachment(models.Model):
    """The attachment for spells."""

    spell: models.ForeignKey[Spell] = models.ForeignKey(Spell, on_delete=models.CASCADE)
    file: models.FileField = models.FileField(
        upload_to="content"
    )


class Bookmark(models.Model):
    """Collection of spell that a user had saved as bookmark."""

    user: models.ForeignKey[User] = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    spell: models.ForeignKey[Spell] = models.ForeignKey(Spell, null=False, on_delete=models.CASCADE)

    def __str__(self):
        """Return bookmark as a string."""
        return f"Bookmark(spell={self.spell.pk}, user={self.user.pk})"


class SpellHistoryEntry(models.Model):
    """An entry in the spell history."""

    user: models.ForeignKey[User] = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    spell: models.ForeignKey[Spell] = models.ForeignKey(Spell, null=False, on_delete=models.CASCADE)
    time: models.DateTimeField = models.DateTimeField()
