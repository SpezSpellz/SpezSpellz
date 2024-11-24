"""Implements the profile page."""
from typing import Any, cast
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from spezspellz.models import Spell, Bookmark, Success
from spezspellz.utils import get_or_none


@login_required
def profile_view(request: HttpRequest) -> HttpResponseBase:
    """Handle the profile page."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    bookmarks = Bookmark.objects.filter(user=user)
    history = cast(Any, user).spellhistoryentry_set.order_by("-time")
    user_success_rate = Success.user_successrate(user)
    context = {
        'user': user,
        'user_success_rate': user_success_rate,
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
        return redirect('spezspellz:404')
    user_success_rate = Success.user_successrate(other_user)
    return render(request, 'profile.html', {
        'other_user': other_user,
        'user_success_rate': user_success_rate,
        'spells': cast(Any, other_user).spell_set.all(),
        'bookmarks': cast(Any, other_user).bookmark_set.all(),
        'history': cast(Any, other_user).spellhistoryentry_set.order_by("-time")
    })
