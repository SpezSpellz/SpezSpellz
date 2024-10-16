"""Implements the profile page."""
from typing import Any, cast
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spezspellz.models import Spell, Bookmark
from django.contrib.auth.models import User


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


def other_profile_view(request: HttpRequest, user_id: int) -> HttpResponseBase:
    """Handle viewing other people profile page."""
    user = request.user
    other_user = User.objects.filter(id=user_id).first()
    spells = Spell.objects.filter(creator=other_user)
    bookmarks = Bookmark.objects.filter(user=other_user)
    history = cast(Any, other_user).spellhistoryentry_set.order_by("-time")
    context = {
        'user': user,
        'other_user': other_user,
        'spells': spells,
        'bookmarks': bookmarks,
        'history': history
    }

    if user.id == other_user.id:
        context = {
            'user': user,
            'spells': spells,
            'bookmarks': bookmarks,
            'history': history
        }

    return render(request, 'profile.html', context)