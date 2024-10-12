"""Contains views for SpezSpellz."""
from itertools import chain
from typing import Optional, Generator, TypeVar, Any, cast
import json
import os
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, HttpResponseBase, FileResponse
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.views.generic import CreateView
from django.db import transaction
from .models import Spell, Tag, Category, get_or_none, HasTag, SpellNotification, Attachment, UserInfo, Bookmark, \
    SpellHistoryEntry, Review, ReviewComment, SpellComment, CommentComment, RateTag, RateCategory


def safe_cast(t, val, default=None):
    """Attempt to cast or else return default."""
    try:
        return t(val)
    except Exception:
        return default


class RPCView:
    """A base view that handles RPC request via POST method."""

    def post(self, request: HttpRequest, **kwargs) -> HttpResponseBase:
        """Handle queries and maybe tags creation."""
        data = None
        try:
            data = json.loads(request.body)
        except Exception as error:
            return HttpResponse(str(error), status=500)
        method_name = data.get("method")
        if method_name is None:
            return HttpResponse("Missing `method` parameter", status=400)
        method_name = f"rpc_{method_name}"
        if not hasattr(self, method_name):
            return HttpResponse("Unknown method", status=404)
        method = getattr(self, method_name)
        params = set(
            filter(
                lambda k: k not in ("request", "return"),
                method.__annotations__
            )
        )
        return getattr(self, method_name)(
            request, **{
                k: v
                for k, v in chain(data.items(), kwargs.items()) if k in params
            }
        )


class HomePage(View):
    """Handle the home page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        all_spells = Spell.objects.all()
        return render(
            request,
            "index.html",
            {
                "latest_spells": all_spells.order_by('-id')[:5],
                "spells": all_spells
            }
        )


class FilterPage(View):
    """Handle the filter page."""

    def get(self, request):
        """Handle GET requests for filter page."""
        selected_category = safe_cast(int, request.GET.get('category'), None)
        selected_tags = request.GET.getlist('tag')
        spells = Spell.objects
        if selected_category:
            spells = spells.filter(category__pk=selected_category)
        if selected_tags:
            spells = spells.filter(hastag__tag__name__in=[safe_cast(str, selected_tag, '') for selected_tag in selected_tags])
        query = request.GET.get("s")
        if query:
            spells = spells.filter(title__icontains=query.strip())
        return render(request, "filter.html", {
            "tags": Tag.objects.all(),
            "spell_categories": Category.objects.all(),
            "spells": spells.all(),
            "selected_tags": selected_tags
        })


class UploadPage(View):
    """Handle the upload page."""

    # 25MB attachment limit
    MAX_ATTACH_SIZE = 25e6
    # 2MB thumbnail limit
    MAX_THUMBNAIL_SIZE = 2e6

    def get(
        self,
        request: HttpRequest,
        spell_id: Optional[int] = None
    ) -> HttpResponseBase:
        """Handle GET requests for this view."""
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(), settings.LOGIN_URL,
                REDIRECT_FIELD_NAME
            )
        context: dict = {"categories": Category.objects.all()}
        if spell_id is not None:
            spell = get_or_none(Spell, pk=spell_id)
            if spell is None:
                return HttpResponse("No such spell", status=404)
            if spell.creator != request.user:
                return HttpResponse("Forbidden", status=403)
            any_spell = cast(Any, spell)
            json_data = json.dumps(
                {
                    "title":
                    spell.title,
                    "body":
                    spell.data,
                    "category":
                    any_spell.category.name,
                    "notis": [
                        {
                            "msg": noti.message,
                            "time": noti.datetime.isoformat(),
                            "every": noti.every
                        } for noti in any_spell.spellnotification_set.all()
                    ],
                    "tags":
                    [tag.tag.name for tag in any_spell.hastag_set.all()],
                    "thumbnail": {
                        "url":
                        reverse(
                            "spezspellz:spell_thumbnail", args=(spell.pk, )
                        ),
                        "name":
                        os.path.basename(spell.thumbnail.name)
                    },
                    "attachs": [
                        {
                            "id":
                            attachment.pk,
                            "size":
                            attachment.file.size,
                            "name":
                            os.path.basename(attachment.file.name),
                            "url":
                            reverse(
                                "spezspellz:attachments",
                                args=(attachment.pk, )
                            )
                        } for attachment in any_spell.attachment_set.all()
                    ]
                }
            )
            context["spell"] = spell
            context["extra_data"] = json_data
        return render(request, "upload.html", context)

    @staticmethod
    def validate_tag_info(tag_name: Optional[str]) -> Optional[dict[str, Any]]:
        """Check if tag_name is valid or not."""
        if tag_name is None:
            return None
        tag = get_or_none(Tag, name=tag_name)
        if tag is None:
            return None
        return {"tag": tag}

    @staticmethod
    def validate_spellnotification_info(
            message: Optional[str], period: Optional[str], datetime: Optional[str]
    ) -> Optional[dict[str, Any]]:
        """Attempt to parse, validate, and convert the provided arguments to values fit for SpellNotification constructor."""
        if message is None or datetime is None or period is None \
                or period not in SpellNotification.EveryType.choices:
            return None
        try:
            parsed_date = parse_datetime(datetime)
            if parsed_date is not None:
                return {
                    "message": message,
                    "every": period,
                    "datetime": parsed_date
                }
        except ValueError:
            pass
        return None

    MakeNewObjectsObjectType = TypeVar("MakeNewObjectsObjectType")

    @staticmethod
    def make_new_objects(
            object_type: type[MakeNewObjectsObjectType],
            infos: Generator[Optional[dict[str, Any]], None, None], **kwargs
    ) -> list[MakeNewObjectsObjectType]:
        """Construct new objects.

        Arguments:
            object_type -- The type of object to create.
            infos -- A generator that generate parameters for objects.
            **kwargs -- Other static parameters.

        Returns:
            The list that contains all the new objects.
        """
        new_objects: list[UploadPage.MakeNewObjectsObjectType] = []
        for info in infos:
            if info is None:
                continue
            new_objects.append(object_type(**info, **kwargs))
        return new_objects

    def post(
        self,
        request: HttpRequest,
        spell_id: Optional[int] = None
    ) -> HttpResponseBase:
        """Handle POST requests for this view."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        data = request.POST.get("data")
        if data is None:
            return HttpResponse("Missing parameter `data`", status=400)
        category_name = request.POST.get("category")
        if category_name is None:
            return HttpResponse("Missing parameter `category`", status=400)
        thumbnail = request.FILES.get("thumbnail")
        if thumbnail is not None and thumbnail.size is not None and thumbnail.size > self.__class__.MAX_THUMBNAIL_SIZE:
            return HttpResponse("Thumbnail too large.", status=400)
        tags_len = min(30, safe_cast(int, request.POST.get("tags"), 0))
        noti_len = min(50, safe_cast(int, request.POST.get("notis"), 0))
        attach_len = min(50, safe_cast(int, request.POST.get("attachs"), 0))
        title = request.POST.get("title", "No Title")
        if not title.strip():
            return HttpResponse("Title must not be empty", status=400)
        category = get_or_none(Category, name=category_name)
        if category is None:
            return HttpResponse("Unknown category", status=404)
        spell = None
        if spell_id is not None:
            old_spell = get_or_none(Spell, pk=spell_id)
            if old_spell is None:
                return HttpResponse("Spell not found", status=404)
            if old_spell.creator != request.user:
                return HttpResponse("Forbidden", status=403)
            spell = old_spell
            old_attach_len = min(
                50, safe_cast(int, request.POST.get("oattachs"), 0)
            )
            old_attachs = []
            for i in range(old_attach_len):
                old_attach = safe_cast(int, request.POST.get(f"oattach{i}"))
                if old_attach is not None:
                    old_attachs.append(old_attach)
            any_spell = cast(Any, spell)
            any_spell.attachment_set.all().exclude(pk__in=old_attachs).delete()
            any_spell.hastag_set.all().delete()
            any_spell.spellnotification_set.all().delete()
            spell.title = title
            spell.data = request.POST.get("data", "")
            spell.category = category
            if thumbnail is not None:
                spell.thumbnail = thumbnail
        else:
            spell = Spell(
                creator=request.user,
                title=title,
                data=request.POST.get("data", ""),
                category=category,
                thumbnail=thumbnail
            )
        new_hastags = self.__class__.make_new_objects(
            HasTag, (
                self.__class__.validate_tag_info(request.POST.get(f"tag{i}"))
                for i in range(tags_len)
            ),
            rating=0,
            spell=spell
        )
        new_spellnotifications = self.__class__.make_new_objects(
            SpellNotification, (
                self.__class__.validate_spellnotification_info(
                    message=request.POST.get(f"notimsg{i}"),
                    period=request.POST.get(f"notiev{i}"),
                    datetime=request.POST.get(f"notidate{i}")
                ) for i in range(noti_len)
            ),
            spell=spell
        )
        total_attach_size = 0
        attach_names = []
        attach_to_add = []
        for i in range(attach_len):
            attach_name = request.POST.get(f"attachn{i}")
            if attach_name is None:
                continue
            attach = request.FILES.get(f"attach{i}")
            if attach is None or attach.size is None:
                continue
            if total_attach_size + attach.size > self.__class__.MAX_ATTACH_SIZE:
                break
            total_attach_size += attach.size
            attachment = Attachment(spell=spell, file=attach)
            attach_to_add.append(attachment)
            attach_names.append(attach_name)
        with transaction.atomic():
            spell.save()
            HasTag.objects.bulk_create(new_hastags)
            SpellNotification.objects.bulk_create(new_spellnotifications)
            Attachment.objects.bulk_create(attach_to_add)
            for i, to_add in enumerate(attach_to_add):
                data = data.replace(
                    attach_names[i],
                    reverse(
                        "spezspellz:attachments", args=(to_add.pk,)
                    )
                )
            spell.data = data
            spell.save()
        return HttpResponse("OK", status=200)


class TagsPage(View, RPCView):
    """Shows all tags and query tags."""

    def get(self, _: HttpRequest) -> HttpResponseBase:
        """Show the tags page."""
        return HttpResponse("Not Implemented", status=404)

    def rpc_search(
            self,
            _: HttpRequest,
            query: Optional[str] = None,
            max_len: int = 50
    ) -> HttpResponseBase:
        """Search for tags that contain the query."""
        if query is None:
            return HttpResponse("Missing `query` parameter", status=400)
        if not isinstance(query, str):
            return HttpResponse(
                "Parameter `query` must be a string", status=400
            )
        if not isinstance(max_len, int):
            return HttpResponse(
                "Parameter `max_len` must be an integer", status=400
            )
        if max_len > 100 or max_len < 1:
            return HttpResponse(
                "Parameter `max_len` must be more than 0 but less than 100",
                status=400
            )
        return HttpResponse(
            json.dumps(
                [
                    tag.name for tag in
                    Tag.objects.filter(name__icontains=query)[0:max_len]
                ]
            ),
            status=200
        )


@login_required
def profile_view(request: HttpRequest) -> HttpResponseBase:
    """Handle the profile page."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    bookmarks = Bookmark.objects.filter(user=user)
    history = cast(Any, user).spellhistoryentry_set.order_by("-time")
    context = {
        'user': user,
        'spells': spells,
        'bookmarks': bookmarks,
        'history': history
    }

    return render(request, 'profile.html', context)


class UserSettingsPage(View, RPCView):
    """Handle the user settings page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "user_settings.html")

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
                return HttpResponse(rate_class.calc_rating(subject=obj), status=200)
            rate = rate_class(user=user, subject=obj)
        elif vote is None:
            rate.delete()
            return HttpResponse(rate_class.calc_rating(subject=obj), status=200)
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
        context["reviews"] = Review.objects.filter(spell=spell).all()
        context["comments"] = cast(Any, spell).spellcomment_set.all()
        context["avg_star"] = spell.calc_avg_stars() or 5.0
        context["tags"] = ({
            "rating": has_tag.calc_rating(),
            "tag": has_tag.tag,
            "pk": has_tag.pk,
            "vote": has_tag.ratetag_set.filter(user=user).first() if user.is_authenticated else None
        } for has_tag in cast(Any, spell).hastag_set.all())
        context["category_vote"] = cast(Any, spell).ratecategory_set.filter(user=user).first() if user.is_authenticated else None
        if user.is_authenticated:
            context["review"] = get_or_none(Review, user=user, spell=spell)
            context["bookmark"] = get_or_none(Bookmark, user=user, spell=spell)
            with transaction.atomic():
                history = cast(Any,
                               user).spellhistoryentry_set.filter(spell=spell
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

    def rpc_comment(
        self,
        request: HttpRequest,
        spell_id: int,
        text: str = "",
    ) -> HttpResponseBase:
        """Handle review comment requests."""
        _ = spell_id
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(text, str):
            return HttpResponse(
                "Parameter `text` must be a string", status=400
            )
        if len(text) > 500:
            return HttpResponse("Text too long", status=400)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        SpellComment.objects.create(spell=spell, commenter=user, text=text)
        return HttpResponse("Comment posted", status=200)

    def rpc_comment_comment(
        self,
        request: HttpRequest,
        spell_id: int,
        comment_id: int,
        text: str = "",
    ) -> HttpResponseBase:
        """Handle review comment requests."""
        _ = spell_id
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(text, str):
            return HttpResponse(
                "Parameter `text` must be a string", status=400
            )
        if not isinstance(comment_id, int):
            return HttpResponse(
                "Parameter `review_id` must be a string", status=400
            )
        if len(text) > 500:
            return HttpResponse("Text too long", status=400)
        comment = get_or_none(SpellComment, pk=comment_id)
        if comment is None:
            return HttpResponse("Review not found", status=404)
        CommentComment.objects.create(
            comment=comment, commenter=user, text=text
        )
        return HttpResponse("Comment posted", status=200)

    def rpc_review_comment(
        self,
        request: HttpRequest,
        spell_id: int,
        review_id: int,
        text: str = "",
    ) -> HttpResponseBase:
        """Handle review comment requests."""
        _ = spell_id
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(text, str):
            return HttpResponse(
                "Parameter `text` must be a string", status=400
            )
        if not isinstance(review_id, int):
            return HttpResponse(
                "Parameter `review_id` must be a string", status=400
            )
        if len(text) > 500:
            return HttpResponse("Text too long", status=400)
        review = get_or_none(Review, pk=review_id)
        if review is None:
            return HttpResponse("Review not found", status=404)
        ReviewComment.objects.create(review=review, commenter=user, text=text)
        return HttpResponse("Comment posted", status=200)

    def rpc_review(
        self,
        request: HttpRequest,
        spell_id: int,
        desc: str = "",
        stars: int = 19
    ) -> HttpResponseBase:
        """Handle review requests."""
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(desc, str):
            return HttpResponse(
                "Parameter `desc` must be a string", status=400
            )
        if not isinstance(stars, int):
            return HttpResponse(
                "Parameter `stars` must be an integer", status=400
            )
        if len(desc) > 256:
            return HttpResponse("Description too long", status=400)
        if stars < 0 or stars > 19:
            return HttpResponse("Bad star parameter", status=400)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        review = get_or_none(Review, user=user, spell=spell)
        if review is not None:
            review.desc = desc
            review.star = stars
            review.save()
            return HttpResponse("Updated", status=200)
        Review.objects.create(user=user, spell=spell, star=stars, desc=desc)
        return HttpResponse("Review posted", status=200)


def thumbnail_view(_: HttpRequest, spell_id: int):
    """Return the thumbnail for a spell."""
    spell = get_or_none(Spell, pk=spell_id)
    if spell is None or not spell.thumbnail:
        return redirect("/assets/default_thumbnail.jpg")
    return FileResponse(spell.thumbnail)


def attachment_view(_: HttpRequest, attachment_id: int):
    """Return the attachment."""
    attachment = get_or_none(Attachment, pk=attachment_id)
    if attachment is None:
        return HttpResponse("Not Found", status=404)
    return FileResponse(attachment.file)


class RegisterView(CreateView):
    """View for registration/signup."""

    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


@login_required
def myspell_view(request: HttpRequest) -> HttpResponseBase:
    """View for all created spell by current user."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    return render(request, "myspell.html", {"spells": spells})
