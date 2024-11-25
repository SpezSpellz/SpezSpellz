"""Implements the myspell page."""
from typing import cast, Any, Optional
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from spezspellz.utils import get_or_none


def profile_spells_view(request: HttpRequest, user_id: Optional[int] = None) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    if user_id is None:
        if not user.is_authenticated:
            return redirect_to_login(request.get_full_path(), "login")
        focus_user = user
    else:
        if user_id == user.pk:
            return redirect("spezspellz:profile_spells")
        other_user = get_or_none(User, pk=user_id)
        if other_user is None:
            return redirect('spezspell:404')
        focus_user = other_user
    spells = cast(Any, focus_user).spell_set.all()
    return render(request, "profile_spells.html", {
        "spells": spells,
        "focus_user": focus_user
    })
