"""Implements ReviewComment model."""
from django.contrib.auth.models import User
from django.db import models
from .review import Review


class ReviewComment(models.Model):
    """A comment for review."""

    review: models.ForeignKey[Review] = models.ForeignKey(
        Review, on_delete=models.CASCADE
    )
    commenter: models.ForeignKey[User] = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    text: models.CharField = models.CharField(max_length=500)
