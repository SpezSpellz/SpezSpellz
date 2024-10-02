from django.contrib import admin

from .models import *


class SpellAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["creator"]}),
        ("Spell Information", {"fields": ["title", "data", "category"]})
    ]

    list_display = ["title", "category", "creator"]


class UserInfoAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Settings", {"fields": ["privacy", "notification"]}),
        ("Information", {"fields": ["user_desc"]})
    ]

    list_display = ["user", "privacy", "notification"]


class HasTagAdmin(admin.ModelAdmin):
    list_display = ["spell", "tag", "rating"]


admin.site.register(Spell, SpellAdmin)
admin.site.register(Tag)
admin.site.register(HasTag)
admin.site.register(Category)
admin.site.register(UserInfo, UserInfoAdmin)