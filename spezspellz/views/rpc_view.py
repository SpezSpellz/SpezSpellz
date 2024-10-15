"""Implements the RPC view."""
from itertools import chain
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBase


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
