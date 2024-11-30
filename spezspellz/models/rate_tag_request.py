"""Implements RateTagRequest model."""
from django.db import models
from .tag_request import TagRequest
from .rate import Rate


class RateTagRequest(Rate):
    """When someone rates a tag."""

    subject: models.ForeignKey[TagRequest] = models.ForeignKey(
        TagRequest, null=False, on_delete=models.CASCADE
    )
