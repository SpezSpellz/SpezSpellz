"""Implements the user settings page."""
from typing import Optional, Any, cast
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from spezspellz.models import Spell, HasTag, UserInfo, Bookmark, \
    Review, ReviewComment, SpellComment, CommentComment, RateTag, \
    RateCategory, TagRequest, RateTagRequest
from spezspellz.utils import get_or_none
from .rpc_view import RPCView


class UserSettingsPage(View, RPCView):
    """Handle the user settings page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(
            request,
            "user_settings.html",
            {
                "max_desc": UserInfo.user_desc.field.max_length
            }
        )

    def post(self, request: HttpRequest, **kwargs) -> HttpResponseBase:
        """
        Handle POST requests for this view.

        Will call RPCView post method if not profile picture update.
        """
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

    def rpc_delete_account(self, request: HttpRequest) -> HttpResponseBase:
        """Handle account deletion."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        user.delete()
        return HttpResponse("OK")

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
            "tag_req": (TagRequest, RateTagRequest),
        }
        obj_class, rate_class = obj_types.get(obj_type, (None, None))
        if obj_class is None or rate_class is None:
            return HttpResponse("Parameter `obj_type` is invalid", status=400)
        obj = get_or_none(obj_class, pk=obj_id)
        if obj is None:
            return HttpResponse("Object not found", status=404)
        with transaction.atomic():
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

    @staticmethod
    def send_deleted(channel_name: str, obj_type: str, obj_id: int, exclude: Optional[User]):
        """Send signal to client that the object is deleted."""
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            channel_name,
            {
                "type": "realtime",
                "except": exclude,
                "data": {
                    "type": "deleted",
                    "obj": obj_type,
                    "id": obj_id
                }
            }
        )

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
            "spell": (Spell, "creator", None),
            "review": (Review, "user", lambda obj, usr: self.send_deleted(f"spell_{obj.spell.pk}", "review", obj.pk, usr)),
            "comment": (SpellComment, "commenter", lambda obj, usr: self.send_deleted(f"spell_{obj.spell.pk}", "comment", obj.pk, usr)),
            "review_comment": (ReviewComment, "commenter", lambda obj, usr: self.send_deleted(f"spell_{obj.review.spell.pk}", "reviewcomment", obj.pk, usr)),
            "comment_comment": (CommentComment, "commenter", lambda obj, usr: self.send_deleted(f"spell_{obj.comment.spell.pk}", "commentcomment", obj.pk, usr))
        }
        obj_class, user_attr, callback = obj_types.get(obj_type, (None, None, None))
        if obj_class is None:
            return HttpResponse("Parameter `obj_type` is invalid", status=400)
        obj = get_or_none(obj_class, pk=obj_id, **{cast(str, user_attr): user})
        if obj is None:
            return HttpResponse("Object not found", status=404)
        if callback is not None:
            callback(obj, user)
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
        with transaction.atomic():
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
        coms_rep_noti: bool = True,
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
            user_info.comment_reply_notifications = bool(coms_rep_noti)
            user_info.private = bool(private)
            user_info.user_desc = str(desc)[:UserInfo.user_desc.field.max_length]
            user_info.save()
        return HttpResponse("OK")

    def rpc_up_uname(
        self,
        request: HttpRequest,
        name: str = ""
    ) -> HttpResponse:
        """Handle settings update."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        user = cast(User, request.user)
        if not isinstance(name, str):
            return HttpResponse("Parameter `name` must be a string", status=400)
        if not name:
            return HttpResponse("Username must not be empty", status=400)
        with transaction.atomic():
            if get_or_none(User, username=name) is not None:
                return HttpResponse("A user with that username already exists", status=403)
            user.username = name
            user.save()
        return HttpResponse("Username updated")

    def rpc_up_passwd(
        self,
        request: HttpRequest,
        opasswd: str = "",
        npasswd: str = ""
    ) -> HttpResponse:
        """Handle settings update."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(opasswd, str):
            return HttpResponse("Parameter `opasswd` must be a string", status=400)
        if not isinstance(npasswd, str):
            return HttpResponse("Parameter `npasswd` must be a string", status=400)
        if not opasswd or not npasswd:
            return HttpResponse("Passwords must not be empty", status=400)
        if not request.user.check_password(opasswd):
            return HttpResponse("Old password is incorrect", status=400)
        request.user.set_password(npasswd)
        request.user.save()
        return HttpResponse("Password changed")
