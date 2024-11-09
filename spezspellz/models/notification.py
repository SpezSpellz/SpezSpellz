"""Implement Notification model."""
from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """Model for storing notification info."""

    user: models.ForeignKey[User] = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    title: models.CharField = models.CharField(max_length=50)
    additional: models.CharField = models.CharField(max_length=50)
    body: models.CharField = models.CharField(max_length=256)
    icon: models.URLField = models.URLField(null=True)
    is_read: models.BooleanField = models.BooleanField(default=False)
    bell_clicked: models.BooleanField = models.BooleanField(default=False)
    ref: models.URLField = models.URLField(null=True)

    def __str__(self):
        """Return notification time and user received."""
        return f"{self.user.username} on {self.timestamp}"
