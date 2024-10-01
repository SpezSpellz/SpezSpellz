"""This file contains models."""
from django.db import models

"""Assuming every model have an id element to it by default"""


class Spell(models.Model):
    userID = models.CharField(max_length=20)
    # TODO: Will connect this to user model later

    title = models.CharField(max_length=20)
    postDescription = models.CharField(max_length=400)
    category = models.CharField(max_length=20, null=True, blank=True)
    tag = models.CharField(max_length=20, null=True, blank=True)
    image_url = models.URLField(default="https://encrypted-tbn0.gstatic.com/images?q="
                                        "tbn:ANd9GcQrQaiqVBiGcaVKeGnRMx0Z7WSm5reolSrZPg&s",
                                blank=True)

    def __str__(self):
        """Return the spell title"""
        return self.title