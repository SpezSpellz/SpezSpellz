"""Implements the tags page."""
from typing import Optional
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.views import View
from spezspellz.models import Tag
from .rpc_view import RPCView


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
