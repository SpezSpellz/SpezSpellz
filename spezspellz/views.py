"""Contains views for SpezSpellz."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.views import View


class HomePage(View):
    """Handle the home page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "index.html")
