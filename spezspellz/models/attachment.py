"""Implements Attachment model."""
from django.db import models
from .spell import Spell


class Attachment(models.Model):
    """The attachment for spells."""

    spell: models.ForeignKey[Spell] = models.ForeignKey(
        Spell, on_delete=models.CASCADE
    )
    file: models.FileField = models.FileField(upload_to="content")
