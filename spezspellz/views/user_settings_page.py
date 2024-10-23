"""Implements the user settings page."""
from typing import Optional, Any, cast
from django.http import HttpRequest, HttpResponse, HttpResponseBase, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.utils.dateparse import parse_datetime
from django.db import transaction
from spezspellz.models import Spell, HasTag, UserInfo, Bookmark, \
    Review, ReviewComment, SpellComment, CommentComment, RateTag, RateCategory, SpellNotification
from spezspellz.utils import get_or_none
from .rpc_view import RPCView


class UserSettingsPage(View, RPCView):
    """Handle the user settings page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "user_settings.html")

    def post(self, request: HttpRequest, **kwargs) -> HttpResponseBase:
        """Handle POST requests for this view."""
        profile_picture = request.FILES.get("pp")
        if profile_picture is not None:
            if not request.user.is_authenticated:
                return HttpResponse("Unauthenticated", status=401)
            user_info = request.user.userinfo if hasattr(
                request.user, "userinfo"
            ) else UserInfo(user=request.user)
            user_info.avatar = profile_picture
            user_info.save()
            return HttpResponse("Avatar updated")
        return super().post(request, **kwargs)

    def rpc_rate(
        self,
        request: HttpRequest,
        obj_type: str = "tag",
        obj_id: int = 0,
        vote: Optional[bool] = None
    ) -> HttpResponseBase:
        """Handle upvotes requests."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(obj_type, str):
            return HttpResponse(
                "Parameter `obj_type` must be a string", status=400
            )
        if not isinstance(obj_id, int):
            return HttpResponse("Parameter `id` must be a string", status=400)
        obj_types = {
            "tag": (HasTag, RateTag),
            "category": (Spell, RateCategory),
        }
        obj_class, rate_class = obj_types.get(obj_type, (None, None))
        if obj_class is None or rate_class is None:
            return HttpResponse("Parameter `obj_type` is invalid", status=400)
        obj = get_or_none(obj_class, pk=obj_id)
        if obj is None:
            return HttpResponse("Object not found", status=404)
        rate = get_or_none(rate_class, subject=obj, user=user)
        if rate is None:
            if vote is None:
                return HttpResponse(
                    rate_class.calc_rating(subject=obj), status=200
                )
            rate = rate_class(user=user, subject=obj)
        elif vote is None:
            rate.delete()
            return HttpResponse(
                rate_class.calc_rating(subject=obj), status=200
            )
        cast(Any, rate).positive = vote
        rate.save()
        return HttpResponse(rate_class.calc_rating(subject=obj), status=200)

    def rpc_delete(
        self,
        request: HttpRequest,
        obj_type: str = "review",
        obj_id: int = 0,
    ) -> HttpResponseBase:
        """Handle object deletion requests."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(obj_type, str):
            return HttpResponse(
                "Parameter `obj_type` must be a string", status=400
            )
        if not isinstance(obj_id, int):
            return HttpResponse("Parameter `id` must be a string", status=400)
        obj_types = {
            "spell": (Spell, "creator"),
            "review": (Review, "user"),
            "comment": (SpellComment, "commenter"),
            "review_comment": (ReviewComment, "commenter"),
            "comment_comment": (CommentComment, "commenter")
        }
        obj_class, user_attr = obj_types.get(obj_type, (None, None))
        if obj_class is None:
            return HttpResponse("Parameter `obj_type` is invalid", status=400)
        obj = get_or_none(obj_class, pk=obj_id, **{cast(str, user_attr): user})
        if obj is None:
            return HttpResponse("Object not found", status=404)
        obj.delete()
        return HttpResponse("Object deleted", status=200)

    def rpc_bookmark(
        self, request: HttpRequest, spell_id: Any = None
    ) -> HttpResponseBase:
        """Handle bookmarking."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(spell_id, int):
            return HttpResponse(
                "Parameter `spell_id` must be an integer", status=400
            )
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        bookmark = get_or_none(Bookmark, user=request.user, spell=spell)
        if bookmark is None:
            Bookmark.objects.create(user=request.user, spell=spell)
        else:
            bookmark.delete()
        return HttpResponse(
            "Bookmarked" if bookmark is None else "Unbookmarked"
        )

    def rpc_update(
        self,
        request: HttpRequest,
        timed_noti: bool = True,
        re_coms_noti: bool = True,
        sp_re_noti: bool = True,
        sp_coms_noti: bool = True,
        private: bool = False,
        desc: str = ""
    ) -> HttpResponse:
        """Handle settings update."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        with transaction.atomic():
            user_info = request.user.userinfo if hasattr(
                request.user, "userinfo"
            ) else UserInfo(user=request.user)
            user_info.timed_notification = bool(timed_noti)
            user_info.review_comment_notification = bool(re_coms_noti)
            user_info.spell_review_notification = bool(sp_re_noti)
            user_info.spell_comment_notification = bool(sp_coms_noti)
            user_info.private = bool(private)
            user_info.user_desc = str(desc)
            user_info.save()
        return HttpResponse("OK")

    def rpc_get_noti(
        self,
        request: HttpRequest,
        time: Optional[str] = None
    ) -> HttpResponseBase:
        """Return notification data for notifying user."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(time, str):
            return HttpResponse(
                "Parameter `time` must be a string", status=400
            )
        try:
            new_datetime = parse_datetime(time)
            if new_datetime is None:
                raise ValueError
        except ValueError:
            return HttpResponse("Bad parameter `time`", status=400)
        user_info = user.userinfo if hasattr(user, "userinfo") else UserInfo(
            user=user
        )
        bookmarks: list = []
        data: dict = {
            "last_notified":
            None if user_info.last_notified is None else
            user_info.last_notified.isoformat(),
            "bookmarks":
            bookmarks
        }
        user_info.last_notified = new_datetime
        user_info.save()
        for bookmark in cast(Any, user).bookmark_set.filter(
            spell__spellnotification__isnull=False
        ).all():
            bookmark_info: dict = {
                "title":
                bookmark.spell.title,
                "icon":
                reverse(
                    "spezspellz:spell_thumbnail", args=(bookmark.spell.pk, )
                ),
                "notifications": []
            }
            for notification in bookmark.spell.spellnotification_set.all():
                notification_info: dict = {
                    "message": notification.message,
                    "time": notification.datetime.isoformat(),
                    "every": notification.every,
                    "noti_id": notification.id
                }
                bookmark_info["notifications"].append(notification_info)
            bookmarks.append(bookmark_info)
        return JsonResponse(data)

    def rpc_update_unread(
            self,
            request: HttpRequest,
            noti_id: str,
            mode: str,
    ) -> HttpResponseBase:
        """Update unread_notification attribute of UserInfo."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        try:
            noti_id = int(noti_id)
        except ValueError:
            return HttpResponse("Parameter `spell_id` must be an integer", status=400)
        if mode not in ["A", "R"]:
            return HttpResponse(
                "Parameter `mode` accept only 'A' for append or 'R' for remove",
                status=400
            )
        noti = get_or_none(SpellNotification, id=noti_id)
        if noti is None:
            return HttpResponse(f"Notification not found", status=404)
        unread = user.userinfo.unread_notifications
        if mode == "A":
            unread.append(noti_id)
        elif mode == "R":
            unread.remove(noti_id)
        unread = unread
        user.userinfo.save()
        return HttpResponse("UserInfo updated")

    def rpc_unread_count(
            self,
            request: HttpRequest
    ) -> HttpResponseBase:
        """Return unread_count property of UserInfo."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        data = {
            "unread_count":
                user.userinfo.unread_count
        }
        return JsonResponse(data)
