"""This file contains tests."""
import json
from django.test import TestCase
from .models import Tag


class SimpleTest(TestCase):
    """A simple test."""

    def test_homepage(self):
        """Go to home page."""
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)

    def test_tag_search(self):
        """Searching tag."""
        tags = ("Fireball", "Frostbolt", "Lightning Strike", "Healing Light",
                "Shadow Step", "Arcane Blast", "Wind Gust", "Earthquake",
                "Divine Shield", "Summon Familiar", "Invisibility",
                "Teleportation", "Time Warp", "Poison Cloud",
                "Barrier of Protection")

        def add_tag(name: str) -> None:
            new_tag = Tag(name=name)
            new_tag.save()

        for tag in tags:
            add_tag(tag)

        def search_tag(query: str) -> list[str]:
            res = self.client.post("/tags/",
                                   json.dumps({
                                       "method": "search",
                                       "query": query
                                   }),
                                   content_type='application/json').content
            return json.loads(res)

        self.assertListEqual(sorted(search_tag("Fire")), sorted(["Fireball"]))
        self.assertListEqual(
            sorted(search_tag("st")),
            sorted([
                "Frostbolt", "Shadow Step", "Arcane Blast", "Wind Gust",
                "Lightning Strike"
            ]))
        self.assertListEqual(search_tag("Unknown"), [])
        self.assertListEqual(sorted(search_tag("")), sorted(tags))
        res = self.client.post("/tags/",
                               json.dumps({
                                   "method": "search",
                                   "query": 80085
                               }),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)
        res = self.client.post("/tags/",
                               json.dumps({
                                   "method": "search",
                               }),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)
        res = self.client.post("/tags/",
                               json.dumps({
                                   "method": "get",
                               }),
                               content_type='application/json')
        self.assertEqual(res.status_code, 404)
        res = self.client.post("/tags/",
                               "\"{\"{",
                               content_type='application/json')
        self.assertEqual(res.status_code, 500)
