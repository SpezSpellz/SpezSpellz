"""Implement admin stuff."""
from django.contrib import admin
from .models import Spell, Tag, HasTag, Category, UserInfo


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
        ("Settings", {"fields": ["privacy", "notification"]}),
        ("Information", {"fields": ["user_desc"]})
    ]

    list_display = ["user", "privacy", "notification"]


class HasTagAdmin(admin.ModelAdmin):
    """For configuring tags."""

    list_display = ["spell", "tag", "rating"]


admin.site.register(Spell, SpellAdmin)
admin.site.register(Tag)
admin.site.register(HasTag, HasTagAdmin)
admin.site.register(Category)
admin.site.register(UserInfo, UserInfoAdmin)
