"""Implements Category model."""
from django.db import models


class Category(models.Model):
    """The category."""

    name: models.CharField = models.CharField(max_length=50)

    def __str__(self):
        """Return the category name."""
        return str(self.name)
