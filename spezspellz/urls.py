"""This file contains urls of SpezSpellz."""
from django.urls import path
from django.shortcuts import redirect, render
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
    path("tags/reqs/", views.TagsPage.as_view(), name="tags_reqs"),
    path("attachment/<int:attachment_id>/", views.attachment_view, name="attachments"),
    path("spell/<int:spell_id>/", views.SpellPage.as_view(), name="spell"),
    path("spell/thumbnail/<int:spell_id>/", views.thumbnail_view, name="spell_thumbnail"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/<int:user_id>", views.other_profile_view, name="other_profile"),
    path("profile/spells/", views.profile_spells_view, name="profile_spells"),
    path("profile/spells/<int:user_id>/", views.profile_spells_view, name="profile_spells"),
    path("filter/", views.FilterPage.as_view(), name="filter"),
    path("avatar/<int:user_id>/", views.profile_picture_view, name="avatar"),
    path("notifications/", views.NotificationView.as_view(), name="notifications"),
    path("404/", lambda request: render(request, "404.html"), name="404")
]

websocket_urlpatterns = [
    path("<str:channels>/", views.RealtimeConsumer.as_asgi(), name="ws"),
    path("", views.RealtimeConsumer.as_asgi(), name="ws")
]
