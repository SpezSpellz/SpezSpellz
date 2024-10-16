"""Implements the myspell page."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spezspellz.models import Spell
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def myspell_view(request: HttpRequest) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    return render(request, "myspell.html", {"spells": spells})


def other_spell_view(request: HttpRequest, user_id: int) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    other_user = User.objects.filter(id=user_id).first()

    if not other_user:
        messages.success(request, "That user does not exist.")
        return redirect('spezspell:home')

    if user.id == user_id:
        spells = Spell.objects.filter(creator=user)
        context = {"spells": spells}
    else:
        spells = Spell.objects.filter(creator=other_user)
        context = {"spells": spells,
                   "other_user": other_user}

    return render(request, "myspell.html", context)