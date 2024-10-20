"""Implements CommentComment model."""
from django.contrib.auth.models import User
from django.db import models
from .spell_comment import SpellComment


class CommentComment(models.Model):
    """A comment for a comment."""

    comment: models.ForeignKey[SpellComment] = models.ForeignKey(
        SpellComment, on_delete=models.CASCADE
    )
    commenter: models.ForeignKey[User] = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    text: models.CharField = models.CharField(max_length=500)
