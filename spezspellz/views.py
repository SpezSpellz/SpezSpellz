"""Contains views for SpezSpellz."""
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
from .models import Spell, Tag, Category, get_or_none, HasTag, SpellNotification, Attachment, UserInfo, Bookmark, SpellHistoryEntry


def safe_cast(t, val, default=None):
    """Attempt to cast or else return default."""
    try:
        return t(val)
    except Exception:
        return default


class RPCView:
    """A base view that handles RPC request via POST method."""

    def post(self, request: HttpRequest) -> HttpResponseBase:
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
                for k, v in data.items() if k in params
            }
        )


class HomePage(View):
    """Handle the home page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(
            request, "index.html", {"latest_spells": Spell.objects.all()}
        )


class UploadPage(View):
    """Handle the upload page."""

    # 25MB attachment limit
    MAX_ATTACH_SIZE = 25e6
    # 2MB thumbnail limit
    MAX_THUMBNAIL_SIZE = 2e6

    def get(self, request: HttpRequest, spell_id: Optional[int] = None) -> HttpResponseBase:
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
            any_spell = cast(Any, spell)
            json_data = json.dumps({
                "title": spell.title,
                "body": spell.data,
                "category": any_spell.category.name,
                "notis": [{
                    "msg": noti.message,
                    "time": noti.datetime.isoformat(),
                    "every": noti.every
                } for noti in any_spell.spellnotification_set.all()],
                "tags": [tag.tag.name for tag in any_spell.hastag_set.all()],
                "thumbnail": {
                    "url": reverse("spezspellz:spell_thumbnail", args=(spell.pk,)),
                    "name": os.path.basename(spell.thumbnail.name)
                },
                "attachs": [
                    {
                        "id": attachment.pk,
                        "size": attachment.file.size,
                        "name": os.path.basename(attachment.file.name),
                        "url": reverse("spezspellz:attachments", args=(attachment.pk,))
                    } for attachment in any_spell.attachment_set.all()
                ]
            })
            context["spell"] = spell
            context["extra_data"] = json_data
        return render(
            request, "upload.html", context
        )

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

    def post(self, request: HttpRequest, spell_id: Optional[int] = None) -> HttpResponseBase:
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
            old_attach_len = min(50, safe_cast(int, request.POST.get("oattachs"), 0))
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
                        "spezspellz:attachments", args=(to_add.pk, )
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
    context = {'user': user, 'spells': spells, 'bookmarks': bookmarks, 'history': history}

    return render(request, 'profile.html', context)


class UserSettingsPage(View, RPCView):
    """Handle the user settings page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "user_settings.html")

    def rpc_delete_spell(self, request: HttpRequest, spell_id: Any = None) -> HttpResponseBase:
        """Delete a spell."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(spell_id, int):
            return HttpResponse("Parameter `spell_id` must be an integer", status=400)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        if spell.creator != request.user:
            return HttpResponse("Forbidden", status=403)
        spell.delete()
        return HttpResponse("Spell deleted")

    def rpc_bookmark(self, request: HttpRequest, spell_id: Any = None) -> HttpResponseBase:
        """Handle bookmarking."""
        if not request.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(spell_id, int):
            return HttpResponse("Parameter `spell_id` must be an integer", status=400)
        spell = get_or_none(Spell, pk=spell_id)
        if spell is None:
            return HttpResponse("Spell not found", status=404)
        bookmark = get_or_none(Bookmark, user=request.user, spell=spell)
        if bookmark is None:
            Bookmark.objects.create(user=request.user, spell=spell)
        else:
            bookmark.delete()
        return HttpResponse("Bookmarked" if bookmark is None else "Unbookmarked")

    def rpc_update(
        self,
        request: HttpRequest,
        timed_noti: bool = True,
        re_coms_noti: bool = True,
        sp_re_noti: bool = True,
        sp_coms_noti: bool = True,
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
            user_info.user_desc = str(desc)
            user_info.save()
        return HttpResponse("OK")


def spell_detail(request: HttpRequest, spell_id: int) -> HttpResponseBase:
    """Return the spell detail page."""
    spell = get_or_none(Spell, pk=spell_id)
    if spell is None:
        return redirect("spezspellz:home")
    bookmark = None
    if request.user.is_authenticated:
        bookmark = get_or_none(Bookmark, user=request.user, spell=spell)
        history = cast(Any, request.user).spellhistoryentry_set.filter(spell=spell).first()
        if history is None:
            SpellHistoryEntry.objects.create(user=request.user, spell=spell, time=timezone.now())
        else:
            history.time = timezone.now()
            history.save()

    return render(
        request, "spell.html", {
            "spell": spell,
            "bookmark": bookmark
        }
    )


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
