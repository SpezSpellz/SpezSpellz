from django.http import JsonResponse, HttpRequest
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from spezspellz.models import Bookmark, SpellNotification


@login_required
def get_notifications(request: HttpRequest) -> JsonResponse:
    """Return notification data for notifying user."""
    user = request.user
    bookmark = Bookmark.objects.filter(user=user)
    all_notifications = []
    timed_notifications = SpellNotification.objects.filter(
        datetime__lte=timezone.now(),
        spell__in=bookmark
    )
    for n in timed_notifications:
        all_notifications.append(
            {
                "title": n.spell.title,
                "message": n.message,
                "icon": f'spell/thumbnail/{n.spell.id}/'
            }
        )
        n.update_datetime()
        n.save()
    return JsonResponse(all_notifications)
