"""This file contains urls of SpezSpellz."""
from django.urls import path
from .views import HomePage, UploadPage, TagsPage, ProfilePage, spell_detail, thumbnail


app_name = "spezspellz"
urlpatterns = [
    path("", HomePage.as_view(), name="home"),
    path("upload/", UploadPage.as_view(), name="upload"),
    path("tags/", TagsPage.as_view(), name="tags"),
    path("spell/<int:spell_id>/", spell_detail, name="spell"),
    path("spell/thumbnail/<int:spell_id>/", thumbnail, name="spell_thumbnail"),
    path("profile/<int:user_id>/", ProfilePage.as_view(), name="profile")
]
