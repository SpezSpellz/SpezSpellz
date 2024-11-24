"""Implement tag request."""
from typing import cast, Any
from django.db.models import Model, CharField
from .tag import TAG_COLORS


class TagRequest(Model):
    """The tag request model."""

    name: CharField = CharField(max_length=30)
    desc: CharField = CharField(max_length=512)

    @property
    def rating(self) -> int:
        """Calculate the rating."""
        return cast(Any, self).ratetagrequest_set.filter(positive=True).count(
        ) - cast(Any, self).ratetagrequest_set.filter(positive=False).count()

    @property
    def color(self):
        """Return the color of the tag."""
        h = 0
        for ch in str(self.name):
            h = (((h << 5) - h) + ord(ch))
        h &= 0xFFFFFFFF
        return TAG_COLORS[h % len(TAG_COLORS)]

    def __str__(self):
        return str(self.name)
