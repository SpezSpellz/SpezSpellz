"""Contains views for SpezSpellz."""
from typing import Optional
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import render
from django.views import View
from .models import Tag


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
        return render(
            request,
            "index.html", {
                "latest_spells": [
                    {
                        "title": "Spell 1",
                        "image_url":
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrQaiqVBiGcaVKeGnRMx0Z7WSm5reolSrZPg&s"
                    },
                    {
                        "title": "Spell 2",
                        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrQaiqVBiGcaVKeGnRMx0Z7WSm5reolSrZPg&s"
                    }
                ]
            }
        )


class UploadPage(View):
    """Handle the upload page."""

    def get(self, request: HttpRequest) -> HttpResponseBase:
        """Handle GET requests for this view."""
        return render(request, "upload.html")


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
        return HttpResponse(json.dumps([tag.name for tag in Tag.objects.filter(name__contains=query)[0:max_len]]), status=200)
