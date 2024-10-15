"""Implements the home page."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.views import View
from spezspellz.models import Spell
from spezspellz.utils import safe_cast


class HomePage(View):
    """Handle the home page."""

    SPELLS_PER_PAGE = 15

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        all_spells = Spell.objects.all()
        page = safe_cast(int, request.GET.get("page"), 1)
        spell_count = all_spells.count()
        max_page = spell_count//self.__class__.SPELLS_PER_PAGE + (1 if spell_count % self.__class__.SPELLS_PER_PAGE != 0 else 0)
        return render(
            request,
            "index.html",
            {
                "latest_spells": all_spells.order_by('-id')[:5],
                "cur_page": page,
                "max_page": max_page,
                "pages": range(max(1, page - 5), min(max_page, page + 5) + 1),
                "spells": all_spells[self.__class__.SPELLS_PER_PAGE * (page - 1):self.__class__.SPELLS_PER_PAGE * page]
            }
        )
