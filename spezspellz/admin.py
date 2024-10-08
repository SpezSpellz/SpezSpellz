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

    # stackoverflow.com/a/37676970/2848256
    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     if db_field.name == 'colour':
    #         kwargs['widget'] = ColourChooserWidget
    #     return super(VehicleAdmin, self).formfield_for_dbfield(db_field,
    #                                                            **kwargs)

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


class CategoryAdmin(admin.ModelAdmin):
    """For configuring list of category"""

    list_display = ["name"]


admin.site.register(Spell, SpellAdmin)
admin.site.register(Tag)
admin.site.register(HasTag, HasTagAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
