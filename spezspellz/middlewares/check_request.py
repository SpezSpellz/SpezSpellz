"""Handles checking request."""
from django.http import HttpResponse
from django.core.exceptions import RequestDataTooBig


class CheckRequest:
    """Checks request size."""

    def __init__(self, response):
        """Initialize CheckRequest."""
        self.get_response = response

    def __call__(self, request):
        """Handle such requests."""
        try:
            _ = request.body
        except RequestDataTooBig:
            return HttpResponse("Request data too big", status=400)
        return self.get_response(request)
