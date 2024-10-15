"""Implements Rate model."""
from django.contrib.auth.models import User
from django.db import models


class Rate(models.Model):
    """When someone rates something."""

    class Meta:
        """Tell that Rate is abstract."""

        abstract = True

    user: models.ForeignKey[User] = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE
    )
    positive: models.BooleanField = models.BooleanField(default=False)

    @classmethod
    def calc_rating(cls, **filters) -> int:
        """Calculate rating."""
        return cls.objects.filter(
            positive=True,
            **filters
        ).count() - cls.objects.filter(positive=False, **filters).count()
