"""Implements the filter page."""
from enum import Enum
from functools import partial
from django.shortcuts import render
from django.views import View
from django.db.models import Count, Avg, QuerySet
from spezspellz.models import Spell, Tag, Category
from spezspellz.utils import safe_cast


class SortOption(Enum):
    """All the sort options."""

    @partial
    # type: ignore
    def RECENT(spells: QuerySet[Spell]):
        """Most recent first."""
        return spells.order_by("-id")

    @partial
    # type: ignore
    def OLDEST(spells: QuerySet[Spell]):
        """Least recent first."""
        return spells.order_by("id")

    @partial
    # type: ignore
    def MOST_COMMENTED(spells: QuerySet[Spell]):
        """Most comments first."""
        return spells.annotate(
            comment_count=Count('spellcomment')
        ).order_by('-comment_count')

    @partial
    # type: ignore
    def LEAST_COMMENTED(spells: QuerySet[Spell]):
        """Least comments first."""
        return spells.annotate(
            comment_count=Count('spellcomment')
        ).order_by('comment_count')

    @partial
    # type: ignore
    def MOST_VIEWED(spells: QuerySet[Spell]):
        """Most view first."""
        return spells.annotate(
            view_count=Count('spellhistoryentry')
        ).order_by('-view_count')

    @partial
    # type: ignore
    def LEAST_VIEWED(spells: QuerySet[Spell]):
        """Least view first."""
        return spells.annotate(
            view_count=Count('spellhistoryentry')
        ).order_by('view_count')

    @partial
    # type: ignore
    def MOST_RATED(spells: QuerySet[Spell]):
        """Most rated first."""
        return spells.annotate(
            average_rating=Avg('review__star')
        ).order_by('-average_rating')

    @partial
    # type: ignore
    def LEAST_RATED(spells: QuerySet[Spell]):
        """Least rated first."""
        return spells.annotate(
            average_rating=Avg('review__star')
        ).order_by('average_rating')


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

        sort_option = str(request.GET.get("sort")).upper()
        sort_type = SortOption.__members__.get(sort_option)
        if sort_type is not None:
            spells = sort_type.value(spells)
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
