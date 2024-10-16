"""Implements a way to get profile picture."""
from typing import cast, Any
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.http.response import HttpResponse, HttpResponseBase, FileResponse
from django.contrib.auth.models import User
from spezspellz.utils import get_or_none


def profile_picture_view(_: HttpRequest, user_id: int) -> HttpResponseBase:
    """Handle user profile picture requests."""
    user = get_or_none(User, pk=user_id)
    if user is None:
        return HttpResponse("User not found", status=404)
    if not hasattr(user, 'userinfo') or not user.userinfo.avatar:
        return redirect("/assets/profile.svg")
    return FileResponse(cast(Any, user).userinfo.avatar)
