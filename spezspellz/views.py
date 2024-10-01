"""Contains views for SpezSpellz."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render, redirect
from django.views import View
from .models import Spell


class HomePage(View):
    """Handle the home page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "index.html", {"latest_spells": Spell.objects.all()})


class UploadPage(View):
    """Handle the upload page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "upload.html")


def spell_detail(request, spell_id):
    try:
        spell = Spell.objects.get(id=spell_id)
    except Spell.DoesNotExist:
        return redirect("spezspellz:home")
    return render(request, "spell.html", {"spell": spell})
