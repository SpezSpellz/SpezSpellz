"""Contains views for SpezSpellz."""
from typing import Optional
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBase, FileResponse
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.utils.dateparse import parse_datetime
from django.views.generic import CreateView
from .models import Spell, User, Tag, Category, get_or_none, HasTag, SpellNotification, Attachment


def safe_cast(t, val, default=None):
    """Attempt to cast or else return default."""
    try:
        return t(val)
    except:
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
        category = request.POST.get("category")
        if category is None:
            return HttpResponse("Missing parameter `category`.", status=400)
        thumbnail = request.FILES.get("thumbnail")
        if thumbnail is not None and thumbnail.size > self.__class__.MAX_THUMBNAIL_SIZE:
            return HttpResponse("Thumbnail too large.", status=400)
        tags_len = min(30, safe_cast(int, request.POST.get("tags"), 0))
        noti_len = min(50, safe_cast(int, request.POST.get("notis"), 0))
        attach_len = min(50, safe_cast(int, request.POST.get("attachs"), 0))
        title = request.POST.get("title", "No Title")
        category = get_or_none(Category, name=category)
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
            noti_date = request.POST.get(f"notidate{i}")
            try:
                noti_date = parse_datetime(noti_date)
                if noti_date is None:
                    continue
            except ValueError:
                continue
            noti_every = request.POST.get(f"notiev{i}")
            if noti_msg is None or noti_every is None or noti_every not in SpellNotification.EveryType.choices:
                continue
            noti = SpellNotification(spell=spell, datetime=noti_date, every=noti_every, message=noti_msg)
            notis_to_add.append(noti)
        total_attach_size = 0
        attach_to_add = []
        for i in range(attach_len):
            attach = request.FILES.get(f"attach{i}")
            if attach is None:
                continue
            if total_attach_size + attach.size > self.__class__.MAX_ATTACH_SIZE:
                break
            total_attach_size += attach.size
            attachment = Attachment(spell=spell, file=attach)
            attach_to_add.append(attachment)
        spell.save()
        HasTag.objects.bulk_create(tags_to_add)
        SpellNotification.objects.bulk_create(notis_to_add)
        Attachment.objects.bulk_create(attach_to_add)
        return HttpResponse("OK", status=200)


class TagsPage(View, RPCView):
    """Shows all tags and query tags."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
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


class ProfilePage(View):
    """Handle the profile page."""

    def get(self, request: HttpRequest, user_id: int) -> HttpResponseBase:
        """Handle GET requests for this view."""
        user = User.objects.get(pk=user_id)
        return render(request, "profile.html", {"user_info": user})


def spell_detail(request: HttpRequest, spell_id: int) -> HttpResponseBase:
    """Return the spell detail page."""
    try:
        spell = Spell.objects.get(id=spell_id)
    except Spell.DoesNotExist:
        return redirect("spezspellz:home")
    return render(request, "spell.html", {"spell": spell})


def thumbnail(_: HttpRequest, spell_id: int):
    """Return the thumbnail for a spell."""
    try:
        spell = Spell.objects.get(id=spell_id)
    except Spell.DoesNotExist:
        return HttpResponse("Not Found", status=404)
    return FileResponse(spell.thumbnail)


class RegisterView(CreateView):
    """View for registration/signup."""

    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"