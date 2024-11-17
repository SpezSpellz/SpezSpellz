"""Implement own custom social adapter."""
import requests
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.files.base import ContentFile
from spezspellz.models import UserInfo


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Override save_user to get info Google account."""

    def save_user(self, request, social_login, form=None):
        """Get actual username and profile picture from Google account."""
        user = super().save_user(request, social_login, form)
        extra_data = social_login.account.extra_data
        user.username = extra_data.get('name', user.username)
        user.save()
        avatar_url = extra_data.get('picture', None)
        if avatar_url:
            # Fetch profile picture from url
            response = requests.get(avatar_url)
            if response.status_code == 200:
                user_info = user.userinfo if hasattr(user, "userinfo") else UserInfo(user=user)
                user_info.avatar = ContentFile(response.content, f"{user.username}.png")
                user_info.save()
        return user
