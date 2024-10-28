"""Implements UserInfo model."""
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    comment_reply_notifications: models.BooleanField = models.BooleanField(
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

    @property
    def unread_badge(self):
        """Return number of unread notification for badge."""
        return self.user.notification_set.filter(bell_clicked=False).count

    def __str__(self):
        """Return user info as string."""
        return f"UserInfo(username={self.user.username})"


@receiver(post_save, sender=get_user_model())
def create_user_info(sender, instance, created, raw, **__):
    """Automagically create user info model for every new user."""
    if created and not raw:
        UserInfo.objects.create(user=instance)
