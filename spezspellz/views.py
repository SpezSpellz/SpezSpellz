"""Contains views for SpezSpellz."""
from django.http import HttpRequest, HttpResponseBase, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from .models import Spell, User


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


class ProfilePage(View):
    """Handle the profile page."""

    def get(self, request: HttpRequest, user_name: str) -> HttpResponseBase:
        """Handle GET requests for this view."""
        user = User.objects.get(username=user_name)
        return render(request, "profile.html", {"user_info": user})


def spell_detail(request: HttpRequest, spell_id: int) -> HttpResponse | HttpResponseRedirect:
    try:
        spell = Spell.objects.get(id=spell_id)
    except Spell.DoesNotExist:
        return redirect("spezspellz:home")
    return render(request, "spell.html", {"spell": spell})
