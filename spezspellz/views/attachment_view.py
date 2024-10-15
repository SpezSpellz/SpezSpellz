"""Implements the attachment view."""
from django.http import HttpRequest, HttpResponse, FileResponse
from spezspellz.models import get_or_none, Attachment


def attachment_view(_: HttpRequest, attachment_id: int):
    """Return the attachment."""
    attachment = get_or_none(Attachment, pk=attachment_id)
    if attachment is None:
        return HttpResponse("Not Found", status=404)
    return FileResponse(attachment.file)
