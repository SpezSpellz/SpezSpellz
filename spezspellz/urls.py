"""This file contains urls of SpezSpellz."""
from django.urls import path
from .views import HomePage, UploadPage, ProfilePage, spell_detail


app_name = "spezspellz"
urlpatterns = [
    path("", HomePage.as_view(), name="home"),
    path("upload/", UploadPage.as_view(), name="upload"),
    path("<int:spell_id>/", spell_detail, name="spell"),
    path("<str:user_name>/", ProfilePage.as_view(), name="profile"),
]
