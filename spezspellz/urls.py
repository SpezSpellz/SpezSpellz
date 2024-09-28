"""This file contains urls of SpezSpellz."""
from django.urls import path
from .views import HomePage


app_name = "spezspellz"
urlpatterns = [
    path("", HomePage.as_view(), name="home")
]
