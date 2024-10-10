"""This file contains urls of SpezSpellz."""
from django.urls import path
from django.shortcuts import redirect
import spezspellz.views as views


app_name = "spezspellz"
urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("login/", lambda _: redirect("login")),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("upload/", views.UploadPage.as_view(), name="upload"),
    path("edit/<int:spell_id>/", views.UploadPage.as_view(), name="edit"),
    path("settings/", views.UserSettingsPage.as_view(), name="usersettings"),
    path("tags/", views.TagsPage.as_view(), name="tags"),
    path("attachment/<int:attachment_id>/", views.attachment_view, name="attachments"),
    path("spell/<int:spell_id>/", views.spell_detail, name="spell"),
    path("spell/thumbnail/<int:spell_id>/", views.thumbnail_view, name="spell_thumbnail"),
    path("profile/", views.profile_view, name="profile"),
    path("review/<int:spell_id>/", views.review_view, name="review"),
    path("profile/myspell", views.myspell_view, name="myspell"),
]
