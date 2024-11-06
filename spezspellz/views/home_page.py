"""Implements the home page."""
from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import render
from django.views import View
from django.db.models import Avg, Sum, Case, When, IntegerField, FloatField
from spezspellz.models import Spell, RateTag, HasTag
from spezspellz.utils import safe_cast


class HomePage(View):
    """Handle the home page."""

    SPELLS_PER_STRIP = 13
    SPELLS_PER_PAGE = 15

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        all_spells = Spell.objects.all()
        page = safe_cast(int, request.GET.get("page"), 1)
        spell_count = all_spells.count()
        max_page = spell_count//self.__class__.SPELLS_PER_PAGE + (1 if spell_count % self.__class__.SPELLS_PER_PAGE != 0 else 0)
        user = request.user
        recommended_spells = None
        if user.is_authenticated:
            num_rated = RateTag.objects.filter(subject__spell__spellhistoryentry__user=user).count()
            liked_tags = HasTag.objects.filter(spell__spellhistoryentry__user=user) \
                .values("tag").annotate(
                    weight=(Sum(
                        Case(
                            When(ratetag__positive=True, then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    ) + 1.0)/(num_rated + 1.0)
                )
            cases = []
            for v in liked_tags:
                cases.append(When(hastag__tag__pk=v["tag"], then=v["weight"]))
            # TODO: Make this not shit
            # Rn it doesn't consider the weight from above and the tag rating from the spell
            # Does not consider category
            # Does not consider rating
            # Does not consider creator
            # Does not consider "views"
            # Does not filter out visited spells
            recommended_spells = all_spells \
                .annotate(weight=Sum(
                    Case(
                        *cases,
                        default=0,
                        output_field=FloatField()
                    )
                )).order_by("-weight")

        return render(
            request,
            "index.html",
            {
                "latest_spells": all_spells.order_by('-id')[:self.__class__.SPELLS_PER_STRIP],
                "top_rated_spells": all_spells.annotate(rating=Avg('review__star')).order_by('-rating')[:self.__class__.SPELLS_PER_STRIP],
                "recommended_spells": recommended_spells[:self.__class__.SPELLS_PER_STRIP] if recommended_spells is not None else None,
                "cur_page": page,
                "max_page": max_page,
                "pages": range(max(1, page - 5), min(max_page, page + 5) + 1),
                "spells": all_spells[self.__class__.SPELLS_PER_PAGE * (page - 1):self.__class__.SPELLS_PER_PAGE * page]
            }
        )
