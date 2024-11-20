"""Implements the spell detail page."""
from typing import Any, cast
from functools import wraps
from django.utils import timezone
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from spezspellz.models import Spell, Bookmark, \
    SpellHistoryEntry, Review, ReviewComment, SpellComment, CommentComment, Notification, Success
from spezspellz.utils import get_or_none
from .rpc_view import RPCView

MAX_NOTIFICATION_COUNT = 50


def validate_user_and_text(view_func):
    """
    Validate user and text before running the view.

    A Decorator
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        """
        Validate the user and text.

        Return: None if no issue
        """
        user = request.user
        text = kwargs.get('text') or kwargs.get('desc')  # In case of the "desc" of rpc_review
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(text, str):
            return HttpResponse(
                "Parameter `text` must be a string", status=400
            )
        return view_func(self, request, *args, **kwargs)
    return wrapper


def create_notification_object(
        sender: User,
        target: User,
        text: str,
        additional: str,
        ref: str,
        noti_type: str,
):
    """
    Create notification object.

    Created when sender is not the same as target.
    After created, if exceed the limit which is 50, then auto delete.
    """
    # If notification is not turned on do nothing.
    if sender == target or not getattr(cast(Any, target).userinfo, noti_type):
        return
    icon_url = reverse("spezspellz:avatar", args=(sender.pk,))
    noti_pk = Notification.objects.create(
        user=target,
        title=sender.username,
        icon=icon_url,
        body=text,
        additional=additional,
        ref=ref
    ).pk
    notifications = cast(Any, target).notification_set.all().order_by("-timestamp")
    if notifications.count() > MAX_NOTIFICATION_COUNT:
        notifications.filter(
            pk__in=notifications[MAX_NOTIFICATION_COUNT:]
        ).delete()
    channel = get_channel_layer()
    async_to_sync(channel.group_send)(
        f"user_{target.pk}",
        {
            "type": "realtime",
            "data": {
                "type": "noti",
                "pk": noti_pk,
                "title": sender.username,
                "icon": icon_url,
                "message": text,
                "additional": additional,
                "time": timezone.now().isoformat(),
                "ref": ref
            }
        }
    )


class SpellPage(View, RPCView):
    """Handle spell page."""

    MAX_HISTORY_COUNT = 30

    def get(self, request: HttpRequest, spell_id: int) -> HttpResponseBase:
        """Return the spell detail page."""
        user = request.user
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return redirect("spezspellz:home")

        context: dict = {"spell": spell, "star_range": range(0, 10, 2)}
        context["success_rate"] = Success.spell_successrate(spell)
        context["success_count"] = Success.objects.filter(spell=spell).count()
        context["reviews"] = Review.objects.filter(spell=spell).all()
        context["comments"] = cast(Any, spell).spellcomment_set.all()
        context["avg_star"] = spell.calc_avg_stars() or 5.0
        context["tags"] = (
            {
                "rating":
                has_tag.calc_rating(),
                "tag":
                has_tag.tag,
                "pk":
                has_tag.pk,
                "vote":
                has_tag.ratetag_set.filter(user=user).first()
                if user.is_authenticated else None
            } for has_tag in cast(Any, spell).hastag_set.all()
        )
        context["category_vote"] = cast(Any, spell).ratecategory_set.filter(
            user=user
        ).first() if user.is_authenticated else None
        context["success_vote"] = cast(Any, spell).ratesuccess_set.filter(
            user=user
        ).first() if user.is_authenticated else None

        if user.is_authenticated:
            context["user_rating"] = Success.objects.filter(user=user, spell=spell).first()
            context["review"] = get_or_none(Review, user=user, spell=spell)
            context["bookmark"] = get_or_none(Bookmark, user=user, spell=spell)
            with transaction.atomic():
                history = cast(
                    Any,
                    user
                ).spellhistoryentry_set.filter(
                    spell=spell
                ).first()
                if history is None:
                    SpellHistoryEntry.objects.create(
                        user=user, spell=spell, time=timezone.now()
                    )
                else:
                    history.time = timezone.now()
                    history.save()
                if cast(Any, user).spellhistoryentry_set.all().count(
                ) > self.__class__.MAX_HISTORY_COUNT:
                    SpellHistoryEntry.objects.filter(
                        pk__in=cast(Any, user).spellhistoryentry_set.all().
                        order_by("-time")[self.__class__.MAX_HISTORY_COUNT:]
                    ).delete()

        return render(request, "spell.html", context)

    def post(self, request: HttpRequest, spell_id: int) -> HttpResponseBase:
        """Handle the user's rating submission or deletion."""
        if not request.user.is_authenticated:
            return redirect('/login/')

        user = request.user
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return redirect("spezspellz:home")

        if 'rating' in request.POST:
            rating = int(request.POST.get('rating'))
            user_rating = Success.objects.filter(user=user, spell=spell).first()

            if user_rating:
                user_rating.rating = rating
                user_rating.save()
            else:
                Success.objects.create(user=user, spell=spell, rating=rating)

            return redirect('spezspellz:spell', spell_id=spell.id)

        if 'delete_rating' in request.POST:
            user_rating = Success.objects.filter(user=user, spell=spell).first()
            if user_rating:
                user_rating.delete()
            return redirect('spezspellz:spell', spell_id=spell.id)

        return redirect('spezspellz:spell', spell_id=spell.id)

    @validate_user_and_text
    def rpc_comment(
        self,
        request: HttpRequest,
        spell_id: int,
        text: str = "",
    ) -> HttpResponseBase:
        """Handle review comment requests."""
        _ = spell_id
        user = cast(User, request.user)

        if len(text) > int(SpellComment.text.field.max_length or 0):
            return HttpResponse("Text too long", status=400)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        comment_pk = SpellComment.objects.create(
            spell=spell, commenter=user, text=text
        ).pk
        create_notification_object(
            sender=cast(Any, user),
            target=cast(Any, spell.creator),
            text=text,
            additional=f"Commented on your {spell.title}",
            ref=f"/spell/{spell.pk}/#comment-{comment_pk}",
            noti_type="spell_comment_notification"
        )
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            f"spell_{spell.pk}",
            {
                "type": "realtime",
                "except": user.pk,
                "data": {
                    "type": "spell_comment",
                    "comment": comment_pk,
                    "username": user.username,
                    "avatar": reverse('spezspellz:avatar', args=(user.pk, )),
                    "link": reverse('spezspellz:other_profile', args=(user.pk, )),
                    "text": text
                }
            }
        )
        return HttpResponse("Comment posted", status=200)

    @validate_user_and_text
    def rpc_comment_comment(
        self,
        request: HttpRequest,
        spell_id: int,
        comment_id: int,
        text: str = "",
    ) -> HttpResponseBase:
        """Handle review comment requests."""
        user = cast(User, request.user)

        if not isinstance(comment_id, int):
            return HttpResponse(
                "Parameter `comment_id` must be an int", status=400
            )
        if len(text) > int(CommentComment.text.field.max_length or 0):
            return HttpResponse("Text too long", status=400)
        comment = get_or_none(SpellComment, pk=comment_id)
        if comment is None:
            return HttpResponse("Review not found", status=404)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        comment_reply_pk = CommentComment.objects.create(
            comment=comment, commenter=user, text=text
        ).pk
        create_notification_object(
            sender=cast(Any, user),
            target=cast(Any, comment.commenter),
            text=text,
            additional="Replied your comment",
            ref=f"/spell/{spell.pk}/#commentcomment-{comment_reply_pk}",
            noti_type="comment_reply_notifications"
        )
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            f"spell_{spell.pk}",
            {
                "type": "realtime",
                "except": user.pk,
                "data": {
                    "type": "comment_comment",
                    "comment": comment.pk,
                    "comment_comment": comment_reply_pk,
                    "user_id": user.pk,
                    "username": user.username,
                    "avatar": reverse('spezspellz:avatar', args=(user.pk, )),
                    "link": reverse('spezspellz:other_profile', args=(user.pk, )),
                    "text": text
                }
            }
        )
        return HttpResponse("Comment posted", status=200)

    @validate_user_and_text
    def rpc_review_comment(
        self,
        request: HttpRequest,
        spell_id: int,
        review_id: int,
        text: str = "",
    ) -> HttpResponseBase:
        """Handle review comment requests."""
        user = cast(User, request.user)

        if not isinstance(review_id, int):
            return HttpResponse(
                "Parameter `review_id` must be an int", status=400
            )
        if len(text) > int(ReviewComment.text.field.max_length or 0):
            return HttpResponse("Text too long", status=400)
        review = get_or_none(Review, pk=review_id)
        if review is None:
            return HttpResponse("Review not found", status=404)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        review_comment_pk = ReviewComment.objects.create(
            review=review, commenter=user, text=text
        ).pk
        create_notification_object(
            sender=cast(Any, user),
            target=cast(Any, review.user),
            text=text,
            additional="Commented on your review",
            ref=f"/spell/{spell.pk}/#reviewcomment-{review_comment_pk}",
            noti_type="review_comment_notification"
        )
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            f"spell_{spell.pk}",
            {
                "type": "realtime",
                "except": user.pk,
                "data": {
                    "type": "review_comment",
                    "review": review.pk,
                    "comment": review_comment_pk,
                    "username": user.username,
                    "avatar": reverse('spezspellz:avatar', args=(user.pk, )),
                    "link": reverse('spezspellz:other_profile', args=(user.pk, )),
                    "text": text
                }
            }
        )
        return HttpResponse("Comment posted", status=200)

    @validate_user_and_text
    def rpc_review(
        self,
        request: HttpRequest,
        spell_id: int,
        desc: str = "",
        stars: int = 19
    ) -> HttpResponseBase:
        """Handle review requests."""
        user = cast(User, request.user)

        if not isinstance(stars, int):
            return HttpResponse(
                "Parameter `stars` must be an integer", status=400
            )
        if len(desc) > int(Review.desc.field.max_length or 0):
            return HttpResponse("Description too long", status=400)
        if stars < 0 or stars > 19:
            return HttpResponse("Bad star parameter", status=400)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        if spell.creator == user:
            return HttpResponse("You cannot review your own spell", status=403)
        review = get_or_none(Review, user=user, spell=spell)
        if review is not None:
            review.desc = desc
            review.star = stars
            review.save()
            return HttpResponse("Updated", status=200)
        review_pk = Review.objects.create(
            user=user, spell=spell, star=stars, desc=desc
        ).pk
        create_notification_object(
            sender=cast(Any, user),
            target=cast(Any, spell.creator),
            text=desc,
            additional=f"Review your {spell.title}",
            ref=f"/spell/{spell.pk}/#review-{review_pk}",
            noti_type="spell_review_notification"
        )
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            f"spell_{spell.pk}",
            {
                "type": "realtime",
                "except": user.pk,
                "data": {
                    "type": "review",
                    "review": review_pk,
                    "username": user.username,
                    "avatar": reverse('spezspellz:avatar', args=(user.pk, )),
                    "link": reverse('spezspellz:other_profile', args=(user.pk, )),
                    "stars": stars,
                    "desc": desc
                }
            }
        )
        return HttpResponse("Review posted", status=200)
