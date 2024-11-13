"""Implements the tags page."""
from typing import Optional, cast, Any
import json
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.views import View
from spezspellz.models import Tag, TagRequest
from spezspellz.utils import get_or_none
from .rpc_view import RPCView


MAX_TAGS_RESULT = 100


class TagsPage(View, RPCView):
    """Shows all tags and query tags."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Show the tags page."""
        context = {
            "tags": Tag.objects.all(),
            "tag_requests": ({
                "req": tag_request,
                "vote": cast(Any, tag_request).ratetagrequest_set.filter(user=request.user).first() if request.user.is_authenticated else None
            } for tag_request in TagRequest.objects.all())
        }
        return render(request, "tags.html", context)

    def rpc_create_request(self, req: HttpRequest, name: str, desc: str) -> HttpResponseBase:
        """Create a tag request."""
        if not req.user.is_authenticated:
            return HttpResponse("Unauthenticated", status=401)
        if not isinstance(name, str):
            return HttpResponse("Parameter `name` must be a string", status=400)
        if not isinstance(desc, str):
            return HttpResponse("Parameter `desc` must be a string", status=400)
        if len(name) > cast(int, TagRequest.name.field.max_length):
            return HttpResponse("Parameter `name` is too long", status=400)
        if len(desc) > cast(int, TagRequest.desc.field.max_length):
            return HttpResponse("Parameter `name` is too long", status=400)
        if not name or not desc:
            return HttpResponse("Name and Description must not be empty", status=400)
        name = name.lower()
        tag = get_or_none(Tag, name=name)
        if tag is not None:
            return HttpResponse("A tag with such name already exist", status=400)
        TagRequest.objects.create(name=name, desc=desc)
        return HttpResponse("Tag request created")

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
        if max_len > MAX_TAGS_RESULT or max_len < 1:
            return HttpResponse(
                f"Parameter `max_len` must be more than 0 but less than {MAX_TAGS_RESULT}",
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
