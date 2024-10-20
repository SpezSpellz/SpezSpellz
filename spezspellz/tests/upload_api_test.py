"""Implements upload api tests."""
from typing import Any
from dataclasses import dataclass
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from spezspellz.models import Tag, Category, Spell, HasTag, Attachment
from .utils import create_test_user


@dataclass(frozen=True)
class AttachmentInfo:
    """Stores Attachment Info used to make UploadRequests."""

    attachment: Any
    name: str


class UploadRequest:
    """Holds information to make an upload request."""

    def __init__(self):
        """Initialize the upload request fields."""
        self.title = None
        self.data = None
        self.category = None
        self.thumbnail = None
        self.tags = []
        self.attachments = []
        self.notifications = []

    def craft(self) -> dict:
        """Crafts the request."""
        req = {}
        if self.title is not None:
            req["title"] = self.title
        if self.data is not None:
            req["data"] = self.data
        if self.category is not None:
            req["category"] = self.category
        if self.thumbnail is not None:
            req["thumbnail"] = self.thumbnail
        if not isinstance(self.tags, list):
            req["tags"] = self.tags
        else:
            req["tags"] = len(self.tags)
            for i, tag_name in enumerate(self.tags):
                req[f"tag{i}"] = tag_name
        if not isinstance(self.attachments, list):
            req["attachs"] = self.attachments
        else:
            req["attachs"] = len(self.attachments)
            for i, attachment_info in enumerate(self.attachments):
                req[f"attach{i}"] = attachment_info.attachment
                req[f"attachn{i}"] = attachment_info.name

        return req


class UploadAPITest(TestCase):
    """Tests for the uploading spell."""

    def test_upload_unauthenticated(self):
        """Attempt to upload a spell without authentication."""
        Category.objects.create(name="Test Category")
        request = UploadRequest()
        request.title = "Test title"
        request.category = "Test Category"
        request.data = "Here[ATTACHMENT0]ItIs"
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(response.status_code, 401)

    def test_upload_no_body(self):
        """Attempt to upload a spell without any body/detail."""
        self.client.force_login(create_test_user())
        Category.objects.create(name="Test Category")
        request = UploadRequest()
        request.title = "Test title"
        request.category = "Test Category"
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_no_category(self):
        """Attempt to upload a spell without any category."""
        self.client.force_login(create_test_user())
        Category.objects.create(name="Test Category")
        request = UploadRequest()
        request.title = "Test title"
        request.data = "Here[ATTACHMENT0]ItIs"
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_unknown_category(self):
        """Attempt to upload a spell with a category that doesn't exist."""
        self.client.force_login(create_test_user())
        Category.objects.create(name="Test Category")
        request = UploadRequest()
        request.title = "Test title"
        request.data = "Here[ATTACHMENT0]ItIs"
        request.category = "Best Category"
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(response.status_code, 404)

    def test_upload_empty_title(self):
        """Attempt to upload a spell with an empty title."""
        self.client.force_login(create_test_user())
        Category.objects.create(name="Test Category")
        request = UploadRequest()
        request.title = "  \r\t\t\n  \r\t\n"
        request.data = "Here[ATTACHMENT0]ItIs"
        request.category = "Test Category"
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(response.status_code, 400)

    def test_upload(self):
        """Attempt to upload a spell."""
        self.client.force_login(create_test_user())
        Category.objects.bulk_create(
            (Category(name="Test Category"), Category(name="Best Category"))
        )
        Tag.objects.bulk_create(
            (
                Tag(name="Ice Element"), Tag(name="Fire Element"),
                Tag(name="Dark Element"), Tag(name="Light Element")
            )
        )
        request = UploadRequest()
        request.title = "Test Spell"
        request.data = "Here=[ATTACHMENT0]=ItIs"
        request.category = "Test Category"
        request.attachments.append(
            AttachmentInfo(
                attachment=SimpleUploadedFile(
                    "test_file.txt",
                    b"simple test file content",
                    content_type="text/plain"
                ),
                name="[ATTACHMENT0]"
            )
        )
        request.tags.extend(("Ice Element", "Dark Element"))
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(
            response.status_code, 200, str(response.content, encoding="UTF-8")
        )
        created_spell = Spell.objects.get(title="Test Spell")
        self.assertEqual(request.category, created_spell.category.name)
        attachment = Attachment.objects.filter(spell=created_spell).first()
        self.assertIsNotNone(attachment, "Attachment not found.")
        self.assertEqual(
            created_spell.data,
            f"Here={reverse('spezspellz:attachments', args=(attachment.pk,))}=ItIs"
        )
        tags = list(HasTag.objects.filter(spell=created_spell).all())
        tags.sort(key=lambda v: v.tag.name)
        self.assertEqual(
            len(tags), 2, "Number of tags not equal to requested."
        )
        self.assertEqual(tags[0].tag.name, "Dark Element")
        self.assertEqual(tags[1].tag.name, "Ice Element")
