"""This file contains urls of SpezSpellz."""
from django.urls import path
from django.shortcuts import redirect
from .views import HomePage, UploadPage, TagsPage, profile_view, spell_detail, thumbnail_view, RegisterView, attachment_view, UserSettingsPage


app_name = "spezspellz"
urlpatterns = [
    path("", HomePage.as_view(), name="home"),
    path("login/", lambda _: redirect("login")),
    path("register/", RegisterView.as_view(), name="register"),
    path("upload/", UploadPage.as_view(), name="upload"),
    path("edit/<int:spell_id>/", UploadPage.as_view(), name="edit"),
    path("settings/", UserSettingsPage.as_view(), name="usersettings"),
    path("tags/", TagsPage.as_view(), name="tags"),
    path("attachment/<int:attachment_id>/", attachment_view, name="attachments"),
    path("spell/<int:spell_id>/", spell_detail, name="spell"),
    path("spell/thumbnail/<int:spell_id>/", thumbnail_view, name="spell_thumbnail"),
    path("profile/", profile_view, name="profile")
]
