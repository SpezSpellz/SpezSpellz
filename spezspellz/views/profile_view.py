"""Implements the profile page."""
from typing import Any, cast
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spezspellz.models import Spell, Bookmark


@login_required
def profile_view(request: HttpRequest) -> HttpResponseBase:
    """Handle the profile page."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    bookmarks = Bookmark.objects.filter(user=user)
    history = cast(Any, user).spellhistoryentry_set.order_by("-time")
    context = {
        'user': user,
        'spells': spells,
        'bookmarks': bookmarks,
        'history': history
    }

    return render(request, 'profile.html', context)
