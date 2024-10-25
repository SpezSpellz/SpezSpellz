"""Contain notification related method."""
from typing import Optional, Any, cast
from django.views import View
from django.urls import reverse
from django.http import HttpRequest, HttpResponseBase, HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import User
from spezspellz.models import Notification, Spell, UserInfo
from spezspellz.utils import get_or_none
from .rpc_view import RPCView


class NotificationView(View, RPCView):
    """Get and create Notification objects."""

    MAX_NOTIFICATION_COUNT = 50
    MAX_BODY = 256
    MAX_ADDITIONAL = 50

    def rpc_get_notifications(
            self,
            request: HttpRequest,
    ) -> HttpResponseBase:
        """Get all notifications."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        notifications = cast(Any, user).notification_set.all().order_by("-timestamp")
        if notifications.count() > self.MAX_NOTIFICATION_COUNT:
            notifications.filter(
                pk__in=notifications[self.MAX_NOTIFICATION_COUNT:]
            ).delete()
        data = {
            "notifications": [
                {
                    "time": notification.timestamp.isoformat(),
                    "title": notification.title,
                    "additional": notification.additional,
                    "message": notification.body,
                    "icon": notification.icon,
                    "ref": notification.ref
                } for notification in notifications
            ],
            "count": notifications.count()
        }
        return JsonResponse(data)

    def rpc_create_notification(
            self,
            request: HttpRequest,
            target_user_id: str,
            sender_obj_id: str,
            sender_obj_type: str,
            body: str,
            additional: str,
            ref: str
    ) -> HttpResponseBase:
        """Create Notification objects."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        try:
            user_id = int(target_user_id)
        except ValueError:
            return HttpResponse("`target_user_id` must be an integer", status=400)
        try:
            sender_id = int(sender_obj_id)
        except ValueError:
            return HttpResponse("`sender_obj_id` must be an integer", status=400)
        if sender_obj_type not in ["spell", "user"]:
            return HttpResponse("`sender_obj_type` must be 'spell' or 'user'", status=400)
        sender: dict = {}
        if sender_obj_type == "spell":
            sender["spell"] = get_or_none(Spell, id=sender_id)
            if sender["spell"] is None:
                return HttpResponse(f"No such {sender_obj_type} id", status=400)
            title = sender["spell"].title
            icon = reverse("spezspellz:spell_thumbnail", args=(sender["spell"].pk,))
        else:
            sender["user"] = get_or_none(User, id=sender_id)
            if sender["user"] is None:
                return HttpResponse(f"No such {sender_obj_type} id", status=400)
            title = sender["user"].username
            icon = reverse("spezspellz:avatar", args=(sender["user"].pk,))
        user = get_or_none(User, id=user_id)
        if user is None:
            return HttpResponse("No such user id", status=400)
        if len(body) > self.MAX_BODY:
            return HttpResponse(f"Maximum characters for body is {self.MAX_BODY}")
        if len(additional) > self.MAX_ADDITIONAL:
            return HttpResponse(f"Maximum characters for additional is {self.MAX_ADDITIONAL}")
        notification = Notification.objects.create(
            user=user,
            title=title,
            icon=icon,
            body=body,
            additional=additional,
            ref=ref
        )
        notification.save()
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
                    "noti_id": notification.id,
                    "spell_id": notification.spell.id
                }
                bookmark_info["notifications"].append(notification_info)
            bookmarks.append(bookmark_info)
        return JsonResponse(data)
