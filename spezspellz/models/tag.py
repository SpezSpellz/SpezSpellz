"""Implements Tag model."""
from django.db import models

TAG_COLORS = (
    '#e6194b', '#3cb44b', '#ffe119',
    '#4363d8', '#f58231', '#911eb4',
    '#46f0f0', '#f032e6', '#bcf60c',
    '#fabebe', '#008080', '#e6beff',
    '#9a6324', '#fffac8', '#800000',
    '#aaffc3', '#808000', '#ffd8b1',
    '#808080', '#ffffff'
)

class Tag(models.Model):
    """The tag."""

    name: models.CharField = models.CharField(max_length=50)

    def __str__(self):
        """Return the tag name."""
        return str(self.name)

    @property
    def color(self):
        """Return the color of the tag."""
        h = 0
        for ch in str(self.name):
            h = (((h << 5) - h) + ord(ch))
        h &= 0xFFFFFFFF
        return TAG_COLORS[h % len(TAG_COLORS)]

