"""Implements Tag model."""
from django.db import models


class Tag(models.Model):
    """The tag."""

    name: models.CharField = models.CharField(max_length=50)

    def __str__(self):
        """Return the tag name."""
        return str(self.name)
