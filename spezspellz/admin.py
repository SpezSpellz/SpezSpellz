"""Implement admin stuff."""
from django.contrib import admin
from .models import Spell, Tag, HasTag, Category, UserInfo, Bookmark


class SpellAdmin(admin.ModelAdmin):
    """For configuring spell."""

    fieldsets = [
        (
            None,
            {
                "fields": ["creator"]
            }
        ),
        (
            "Spell Information",
            {
                "fields":
                [
                    "title",
                    "data",
                    "category"
                ]
            }
        )
    ]

    list_display = ["title", "category", "creator"]


class UserInfoAdmin(admin.ModelAdmin):
    """For configuring user info."""

    fieldsets = [
        ("Settings", {"fields": ["timed_notification",
                                 "review_comment_notification",
                                 "spell_review_notification",
                                 "spell_comment_notification"]}),

        ("Information", {"fields": ["user_desc"]})
    ]

    list_display = ["user", "timed_notification", "review_comment_notification", "spell_review_notification", "spell_comment_notification"]


class HasTagAdmin(admin.ModelAdmin):
    """For configuring tags."""

    list_display = ["spell", "tag", "rating"]


class BookmarkAdmin(admin.ModelAdmin):
    """For configuring Bookmarks"""

    list_display = ["user", "spell"]


admin.site.register(Spell, SpellAdmin)
admin.site.register(Tag)
admin.site.register(HasTag, HasTagAdmin)
admin.site.register(Category)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
