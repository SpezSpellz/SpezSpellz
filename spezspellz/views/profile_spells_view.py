"""Implements the myspell page."""
from typing import cast, Any
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from spezspellz.utils import get_or_none


@login_required
def profile_spells_view(request: HttpRequest, user_id: int = None) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    if user_id is None:
        focus_user = user
    else:
        if user_id == user.pk:
            return redirect("spezspellz:profile_spell")
        focus_user = get_or_none(User, pk=user_id)
        if focus_user is None:
            messages.success(request, "That user does not exist.")
            return redirect('spezspell:home')
    spells = cast(Any, focus_user).spell_set.all()
    return render(request, "profile_spells.html", {
        "spells": spells,
        "focus_user": focus_user
    })
