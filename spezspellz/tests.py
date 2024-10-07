"""This file contains tests."""
import json
from typing import Any
from io import StringIO
from dataclasses import dataclass
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Tag, Category, Spell, HasTag, Attachment


def create_test_user():
    """Create a test user."""
    user = User(username="tester")
    user.set_password("1234")
    user.save()
    return user


@dataclass(frozen=True)
class AttachmentInfo:
    """Stores Attachment Info used to make UploadRequests."""
    attachment: Any
    name: str


class UploadRequest:
    """Holds information to make an upload request."""

    def __init__(self):
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


class SimpleTest(TestCase):
    """A simple test."""

    def test_homepage(self):
        """Go to home page."""
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)

    def test_tag_search(self):
        """Searching tag."""
        tags = (
            "Fireball", "Frostbolt", "Lightning Strike", "Healing Light",
            "Shadow Step", "Arcane Blast", "Wind Gust", "Earthquake",
            "Divine Shield", "Summon Familiar", "Invisibility",
            "Teleportation", "Time Warp", "Poison Cloud",
            "Barrier of Protection"
        )

        def add_tag(name: str) -> None:
            new_tag = Tag(name=name)
            new_tag.save()

        for tag in tags:
            add_tag(tag)

        def search_tag(query: str) -> list[str]:
            res = self.client.post(
                "/tags/",
                json.dumps({
                    "method": "search",
                    "query": query
                }),
                content_type='application/json'
            ).content
            return json.loads(res)

        self.assertListEqual(sorted(search_tag("Fire")), sorted(["Fireball"]))
        self.assertListEqual(
            sorted(search_tag("st")),
            sorted(
                [
                    "Frostbolt", "Shadow Step", "Arcane Blast", "Wind Gust",
                    "Lightning Strike"
                ]
            )
        )
        self.assertListEqual(search_tag("Unknown"), [])
        self.assertListEqual(sorted(search_tag("")), sorted(tags))
        res = self.client.post(
            "/tags/",
            json.dumps({
                "method": "search",
                "query": 80085
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        res = self.client.post(
            "/tags/",
            json.dumps({
                "method": "search",
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)

    def test_rpc_unknown_method(self):
        """Attempt to do an RPC with unknown method."""
        res = self.client.post(
            "/tags/",
            json.dumps({
                "method": "gaynigger",
                420: 69
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 404)

    def test_rpc_bad_json(self):
        """Check whether RPC will return a bad request when the JSON is broken."""
        res = self.client.post(
            "/tags/", "\"{\"{", content_type='application/json'
        )
        self.assertEqual(res.status_code, 500)

    def test_rpc_no_method_parameter(self):
        """Check whether RPC will return a bad request when method parameter is missing."""
        res = self.client.post(
            "/tags/",
            json.dumps({
                "not_method": "search",
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)

    def test_upload_login_redirect(self):
        """Check whether going to upload page without logging first redirects to login."""
        res = self.client.get("/upload/", follow=True)
        self.assertTrue(hasattr(res, "redirect_chain"), msg="Didn't redirect")
        self.assertTrue(res.redirect_chain, msg="Didn't redirect")
        self.assertEqual(
            res.redirect_chain[0][1],
            302,
            msg=
            f"Status code is not temp redirect, got: {res.redirect_chain[0][1]}"
        )
        final_url = res.redirect_chain[-1][0]
        self.assertEqual(
            res.status_code, 200, msg="Final url's status code is not OK"
        )
        self.assertIn(
            reverse("login"), final_url, msg="Login path is not in final url."
        )
        self.assertIn(
            reverse("spezspellz:upload"),
            final_url,
            msg="Upload path is not in final url."
        )

    def test_upload_page(self):
        """Go to upload page."""
        test_category_name = "RANDOMASSCATEGORYLOLLMAOEZGGEZ"
        Category.objects.create(name=test_category_name)
        self.client.force_login(create_test_user())
        response = self.client.get(reverse("spezspellz:upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_category_name)


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
                attachment=StringIO("simple attachment"), name="[ATTACHMENT0]"
            )
        )
        request.tags.extend(("Ice Element", "Dark Element"))
        response = self.client.post(
            reverse("spezspellz:upload"), request.craft()
        )
        self.assertEqual(response.status_code, 200)
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
