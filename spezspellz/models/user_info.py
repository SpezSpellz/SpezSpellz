"""Implements UserInfo model."""
from django.contrib.auth.models import User
from django.db import models


class UserInfo(models.Model):
    """Store the user info."""

    user: models.OneToOneField[User] = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    private: models.BooleanField = models.BooleanField(default=False)
    timed_notification: models.BooleanField = models.BooleanField(default=True)
    review_comment_notification: models.BooleanField = models.BooleanField(
        default=True
    )
    spell_review_notification: models.BooleanField = models.BooleanField(
        default=True
    )
    spell_comment_notification: models.BooleanField = models.BooleanField(
        default=True
    )
    user_desc: models.CharField = models.CharField(default="", max_length=400)
    avatar: models.FileField = models.FileField(
        upload_to="content", null=True
    )
    last_notified: models.DateTimeField = models.DateTimeField(auto_now=True)

    @property
    def is_private(self):
        """Checks whether user is private."""
        return self.private

    def __str__(self):
        """Return user info as string."""
        return f"UserInfo(username={self.user.username})"
