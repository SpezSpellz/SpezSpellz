"""Implements the myspell page."""
from typing import cast, Any
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from spezspellz.models import Spell
from spezspellz.utils import get_or_none


@login_required
def myspell_view(request: HttpRequest) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    return render(request, "myspell.html", {"spells": spells})


def other_spell_view(request: HttpRequest, user_id: int) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    if user.pk == user_id:
        return redirect("spezspellz:myspell")
    other_user = get_or_none(User, pk=user_id)
    if not other_user:
        messages.success(request, "That user does not exist.")
        return redirect('spezspell:home')
    return render(
        request, "myspell.html", {
            "spells": cast(Any, other_user).spell_set.all(),
            "other_user": other_user
        }
    )
