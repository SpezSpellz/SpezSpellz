"""Implements the upload page."""
from typing import Optional, Generator, TypeVar, Any, cast
import json
import os
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.db import transaction
from spezspellz.models import Spell, Tag, Category, HasTag, SpellNotification, Attachment
from spezspellz.utils import safe_cast, get_or_none


class UploadPage(View):
    """Handle the upload page."""

    # 25MB attachment limit
    MAX_ATTACH_SIZE = 25e6

    # 2MB thumbnail limit
    MAX_THUMBNAIL_SIZE = 2e6

    # Max number of tags per post
    MAX_TAGS_PER_POST = 30

    # Max number of notifications per post
    MAX_NOTI_PER_POST = 50

    # Max number of attachments per post
    MAX_ATTACH_PER_POST = 50

    def get(
        self,
        request: HttpRequest,
        spell_id: Optional[int] = None
    ) -> HttpResponseBase:
        """
        Handle GET requests for this view.
        Normally when user edit the spell.
        """
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
                or period not in SpellNotification.EveryType.values:
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
        """
        Handle POST requests for this view.
        When upload or make changes to the spell.
        """
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
        tags_len = min(self.__class__.MAX_TAGS_PER_POST, safe_cast(int, request.POST.get("tags"), 0))
        noti_len = min(self.__class__.MAX_NOTI_PER_POST, safe_cast(int, request.POST.get("notis"), 0))
        attach_len = min(self.__class__.MAX_ATTACH_PER_POST, safe_cast(int, request.POST.get("attachs"), 0))
        title = request.POST.get("title", "No Title")
        if not title.strip():
            return HttpResponse("Title must not be empty", status=400)
        category = get_or_none(Category, name=category_name)
        if category is None:
            return HttpResponse("Unknown category", status=404)
        if spell_id is not None:
            spell = get_or_none(Spell, pk=spell_id)
            if spell is None:
                return HttpResponse("Spell not found", status=404)
            if spell.creator != request.user:
                return HttpResponse("Forbidden", status=403)
            old_attach_len = min(
                self.__class__.MAX_ATTACH_PER_POST, safe_cast(int, request.POST.get("oattachs"), 0)
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
        return HttpResponse("OK", status=200, headers={"pk": spell.pk})
