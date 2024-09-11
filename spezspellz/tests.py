"""This file contains tests."""
from django.test import TestCase


class SimpleTest(TestCase):
    """A simple test."""

    def test_homepage(self):
        """Go to home page."""
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
