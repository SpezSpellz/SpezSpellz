"""Contains views for SpezSpellz."""
from typing import Optional
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBase, FileResponse
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.views.generic import CreateView
from django.db import transaction
from .models import Spell, Tag, Category, get_or_none, HasTag, SpellNotification, Attachment, UserInfo, Bookmark


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
        params = set(filter(lambda k: k not in ("request", "return"), method.__annotations__))
        return getattr(self, method_name)(request, **{k: v for k, v in data.items() if k in params})


class HomePage(View):
    """Handle the home page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "index.html", {"latest_spells": Spell.objects.all()})


class UploadPage(View):
    """Handle the upload page."""

    # 25MB attachment limit
    MAX_ATTACH_SIZE = 25e6
    # 2MB thumbnail limit
    MAX_THUMBNAIL_SIZE = 2e6

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "upload.html", {
            "categories": Category.objects.all()
        })

    def post(self, request: HttpRequest) -> HttpResponseBase:
        """Handle POST requests for this view."""
        data = request.POST.get("data")
        if data is None:
            return HttpResponse("Missing parameter `data`.", status=400)
        category_name = request.POST.get("category")
        if category_name is None:
            return HttpResponse("Missing parameter `category`.", status=400)
        thumbnail = request.FILES.get("thumbnail")
        if thumbnail is not None and thumbnail.size is not None and thumbnail.size > self.__class__.MAX_THUMBNAIL_SIZE:
            return HttpResponse("Thumbnail too large.", status=400)
        tags_len = min(30, safe_cast(int, request.POST.get("tags"), 0))
        noti_len = min(50, safe_cast(int, request.POST.get("notis"), 0))
        attach_len = min(50, safe_cast(int, request.POST.get("attachs"), 0))
        title = request.POST.get("title", "No Title")
        category = get_or_none(Category, name=category_name)
        if category is None:
            return HttpResponse("Unknown category.", status=404)
        spell = Spell(
            creator=request.user,
            title=title,
            data=request.POST.get("data", ""),
            category=category,
            thumbnail=thumbnail
        )
        tags_to_add = []
        for i in range(tags_len):
            tag_entry_name = request.POST.get(f"tag{i}")
            if tag_entry_name is None:
                continue
            tag = get_or_none(Tag, name=tag_entry_name)
            if tag is None:
                continue
            has_tag = HasTag(spell=spell, tag=tag, rating=0)
            tags_to_add.append(has_tag)
        notis_to_add = []
        for i in range(noti_len):
            noti_msg = request.POST.get(f"notimsg{i}")
            noti_every = request.POST.get(f"notiev{i}")
            if noti_msg is None or noti_every is None or noti_every not in SpellNotification.EveryType.choices:
                continue
            noti_date_str = request.POST.get(f"notidate{i}")
            if noti_date_str is None:
                continue
            noti_date = None
            try:
                noti_date = parse_datetime(noti_date_str)
                if noti_date is None:
                    continue
            except ValueError:
                continue
            noti = SpellNotification(spell=spell, datetime=noti_date, every=noti_every, message=noti_msg, data=data)
            notis_to_add.append(noti)
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
            HasTag.objects.bulk_create(tags_to_add)
            SpellNotification.objects.bulk_create(notis_to_add)
            Attachment.objects.bulk_create(attach_to_add)
            for i in range(len(attach_to_add)):
                data = data.replace(attach_names[i], reverse("spezspellz:attachments", args=(attach_to_add[i].pk,)))
            spell.data = data
            spell.save()
        return HttpResponse("OK", status=200)


class TagsPage(View, RPCView):
    """Shows all tags and query tags."""

    def get(self, _: HttpRequest) -> HttpResponseBase:
        """Show the tags page."""
        return HttpResponse("Not Implemented", status=404)

    def rpc_search(self, _: HttpRequest, query: Optional[str] = None, max_len: int = 50) -> HttpResponseBase:
        """Search for tags that contain the query."""
        if query is None:
            return HttpResponse("Missing `query` parameter", status=400)
        if not isinstance(query, str):
            return HttpResponse("Parameter `query` must be a string", status=400)
        if not isinstance(max_len, int):
            return HttpResponse("Parameter `max_len` must be an integer", status=400)
        if max_len > 100 or max_len < 1:
            return HttpResponse("Parameter `max_len` must be more than 0 but less than 100", status=400)
        return HttpResponse(json.dumps([tag.name for tag in Tag.objects.filter(name__icontains=query)[0:max_len]]), status=200)


@login_required
def profile_view(request: HttpRequest) -> HttpResponseBase:
    """Handle the profile page."""
    user = request.user
    spells = Spell.objects.filter(creator=user)
    bookmarks = Bookmark.objects.filter(user=user)
    return render(request, 'profile.html', {
        'user': user,
        'spells': spells,
        'bookmarks': bookmarks
    })


class UserSettingsPage(View, RPCView):
    """Handle the user settings page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "user_settings.html")

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
            user_info = request.user.userinfo if hasattr(request.user, "userinfo") else UserInfo(user=request.user)
            user_info.timed_notification = bool(timed_noti)
            user_info.review_comment_notification = bool(re_coms_noti)
            user_info.spell_review_notification = bool(sp_re_noti)
            user_info.spell_comment_notification = bool(sp_coms_noti)
            user_info.user_desc = str(desc)
            user_info.save()
        return HttpResponse("OK")


def spell_detail(request: HttpRequest, spell_id: int) -> HttpResponseBase:
    """Return the spell detail page."""
    try:
        spell = Spell.objects.get(id=spell_id)
    except Spell.DoesNotExist:
        return redirect("spezspellz:home")
    return render(request, "spell.html", {"spell": spell})


def thumbnail_view(_: HttpRequest, spell_id: int):
    """Return the thumbnail for a spell."""
    try:
        spell = Spell.objects.get(pk=spell_id)
    except Spell.DoesNotExist:
        return HttpResponse("Not Found", status=404)
    if not spell.thumbnail:
        return redirect("/assets/default_thumbnail.jpg")
    return FileResponse(spell.thumbnail)


def attachment_view(_: HttpRequest, attachment_id: int):
    """Return the attachment."""
    try:
        attachment = Attachment.objects.get(pk=attachment_id)
    except Attachment.DoesNotExist:
        return HttpResponse("Not Found", status=404)
    return FileResponse(attachment.file)


class RegisterView(CreateView):
    """View for registration/signup."""

    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"
