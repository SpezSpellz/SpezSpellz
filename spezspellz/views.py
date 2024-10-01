"""Contains views for SpezSpellz."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.views import View


class HomePage(View):
    """Handle the home page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(
            request, "index.html", {
                "latest_spells": [{
                    "title":
                    "Spell 1",
                    "image_url":
                    "https://encrypted-tbn0.gstatic.com/images?q="
                    "tbn:ANd9GcQrQaiqVBiGcaVKeGnRMx0Z7WSm5reolSrZPg&s"
                }, {
                    "title":
                    "Spell 2",
                    "image_url":
                    "https://encrypted-tbn0.gstatic.com/images?q="
                    "tbn:ANd9GcQrQaiqVBiGcaVKeGnRMx0Z7WSm5reolSrZPg&s"
                }]
            })


class UploadPage(View):
    """Handle the upload page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "upload.html")


class ProfilePage(View):
    """Handle the upload page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        user = User.objects.get(username=user_name)
        return render(request, "profile.html", {"user_info": user})
