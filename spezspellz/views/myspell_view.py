"""Implements the myspell page."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spezspellz.models import Spell


@login_required
def myspell_view(request: HttpRequest) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    return render(request, "myspell.html", {"spells": spells})
