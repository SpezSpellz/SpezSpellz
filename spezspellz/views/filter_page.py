"""Implements the filter page."""
from django.shortcuts import render
from django.views import View
from django.db.models import Count, Avg
from spezspellz.models import Spell, Tag, Category
from spezspellz.utils import safe_cast


class FilterPage(View):
    """Handle the filter page."""

    SPELLS_PER_PAGE = 15

    def get(self, request):
        """Handle GET requests for filter page."""
        selected_category = safe_cast(int, request.GET.get('category'), None)
        selected_tags = request.GET.getlist('tag')
        spells = Spell.objects.all()

        if selected_category:
            spells = spells.filter(category__pk=selected_category)
        if selected_tags:
            for selected_tag in selected_tags:
                spells = spells.filter(
                    hastag__tag__name=safe_cast(str, selected_tag, '')
                )

        query = request.GET.get("s")
        if query:
            spells = spells.filter(title__icontains=query.strip())

        creator = safe_cast(int, request.GET.get("creator"), None)
        if creator is not None:
            spells = spells.filter(creator__pk=creator)

        page = safe_cast(int, request.GET.get("page"), 1)
        spell_count = spells.count()
        max_page = spell_count // self.__class__.SPELLS_PER_PAGE + (
            1 if spell_count % self.__class__.SPELLS_PER_PAGE != 0 else 0
        )

        sort_option = request.GET.get("sort")
        if sort_option == "recent":
            spells = spells.order_by('-id')
        elif sort_option == "oldest":
            spells = spells.order_by('id')
        elif sort_option == "most_commented":
            spells = spells.annotate(
                comment_count=Count('spellcomment')
            ).order_by('-comment_count')
        elif sort_option == "least_commented":
            spells = spells.annotate(
                comment_count=Count('spellcomment')
            ).order_by('comment_count')
        elif sort_option == "most_viewed":
            spells = spells.annotate(
                view_count=Count('spellhistoryentry')
            ).order_by('-view_count')
        elif sort_option == "least_viewed":
            spells = spells.annotate(
                view_count=Count('spellhistoryentry')
            ).order_by('view_count')
        elif sort_option == "most_rated":
            spells = spells.annotate(
                average_rating=Avg('review__star')
            ).order_by('-average_rating')
        elif sort_option == "least_rated":
            spells = spells.annotate(
                average_rating=Avg('review__star')
            ).order_by('average_rating')
        spells = spells.distinct()

        return render(
            request, "filter.html", {
                "tags":
                Tag.objects.all(),
                "spell_categories":
                Category.objects.all(),
                "spells":
                spells[self.__class__.SPELLS_PER_PAGE *
                       (page - 1):self.__class__.SPELLS_PER_PAGE * page],
                "selected_tags":
                selected_tags,
                "cur_page":
                page,
                "max_page":
                max_page,
                "pages":
                range(max(1, page - 5),
                      min(max_page, page + 5) + 1)
            }
        )
