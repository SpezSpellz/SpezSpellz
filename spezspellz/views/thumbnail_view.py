"""Implements the thumbnail view."""
from django.http import HttpRequest, FileResponse
from django.shortcuts import redirect
from spezspellz.models import Spell, get_or_none


def thumbnail_view(_: HttpRequest, spell_id: int):
    """Return the thumbnail for a spell."""
    spell = get_or_none(Spell, pk=spell_id)
    if spell is None or not spell.thumbnail:
        return redirect("/assets/default_thumbnail.jpg")
    return FileResponse(spell.thumbnail)
