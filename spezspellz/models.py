"""This file contains models."""
from django.db import models
from django.contrib.auth.models import User
"""Assuming every model have an id element to it by default"""


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    privacy = models.BooleanField(default=False)
    notification = models.BooleanField(default=True)
    userDescription = models.CharField(max_length=400)

    def __str__(self):
        return self.user.username + " Info"

class Spell(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    """If user is deleted his spells are also gone"""

    title = models.CharField(max_length=20)
    postDescription = models.CharField(max_length=400)
    category = models.CharField(max_length=20, null=True, blank=True)
    tag = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        """Return the spell title"""
        return self.title

