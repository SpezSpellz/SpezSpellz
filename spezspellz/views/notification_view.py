from django.http import JsonResponse, HttpRequest
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from spezspellz.models import Bookmark, SpellNotification


@login_required
def get_notifications(request: HttpRequest) -> JsonResponse:
    user = request.user
    bookmark = Bookmark.objects.filter(user=user)
    notifications = SpellNotification.objects.filter(
        datetime__lte=timezone.now(),
        spell__in=bookmark
    )
    return JsonResponse(
        [
            {
                "title": notification.spell.title,
                "message": notification.message,
                "icon": f'spell/thumbnail/{notifications.spell.id}/'
            }
            for notification in notifications
        ],
        safe=False
    )
