"""Imports all views."""
from .rpc_view import RPCView
from .home_page import HomePage
from .filter_page import FilterPage
from .tags_page import TagsPage
from .upload_page import UploadPage
from .profile_view import profile_view, other_profile_view
from .attachment_view import attachment_view
from .myspell_view import myspell_view, other_spell_view
from .spell_page import SpellPage
from .thumbnail_view import thumbnail_view
from .user_settings_page import UserSettingsPage
from .register_view import RegisterView
from .profile_picture_view import profile_picture_view
from .notification_view import NotificationView
from .realtime import RealtimeConsumer
from .login_view import CustomLoginView
from .adapters import CustomSocialAccountAdapter


__all__ = (
    "RPCView",
    "HomePage",
    "FilterPage",
    "TagsPage",
    "UploadPage",
    "profile_view",
    "attachment_view",
    "myspell_view",
    "SpellPage",
    "thumbnail_view",
    "UserSettingsPage",
    "RegisterView",
    "profile_picture_view",
    "other_profile_view",
    "other_spell_view",
    "NotificationView",
    "RealtimeConsumer",
    "CustomLoginView",
    "CustomSocialAccountAdapter",
)
