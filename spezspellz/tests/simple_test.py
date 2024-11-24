"""Implements simple tests."""
import json
from django.test import TestCase
from django.urls import reverse
from spezspellz.models import Tag, Category
from .utils import create_test_user


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
            msg=f"Status code is not temp redirect, got: {res.redirect_chain[0][1]}"
        )
        final_url = res.redirect_chain[-1][0]
        self.assertEqual(
            res.status_code, 200, msg="Final url's status code is not OK"
        )
        self.assertIn(
            reverse("spezspellz:login"), final_url, msg="Login path is not in final url."
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
