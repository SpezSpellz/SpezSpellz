"""Implements the profile page."""
from typing import Any, cast
from django.http import HttpRequest, HttpResponseBase, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from spezspellz.models import Spell, Bookmark
from spezspellz.utils import get_or_none


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
    if user.pk == user_id:
        return redirect("spezspellz:profile")
    other_user = get_or_none(User, pk=user_id)
    if other_user is None:
        raise Http404
    return render(request, 'profile.html', {
        'other_user': other_user,
        'spells': cast(Any, other_user).spell_set.all(),
        'bookmarks': cast(Any, other_user).bookmark_set.all(),
        'history': cast(Any, other_user).spellhistoryentry_set.order_by("-time")
    })
