"""Implements spell page tests."""
from typing import cast, Any
from django.test import TestCase
from django.urls import reverse
from spezspellz.models import Spell, Category
from .utils import create_test_user


class SpellPageTest(TestCase):
    """Tests for the spell page."""

    def test_view_spell_unauthenticated(self):
        """Attempt to view a spell while unauthenticated."""
        user = create_test_user("tester")
        category = Category.objects.create(name="Test Category")
        spell = Spell.objects.create(
            creator=user,
            title="Test spell",
            thumbnail=None,
            data="test data",
            category=category
        )
        res = self.client.get(reverse("spezspellz:spell", args=(spell.pk, )))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, b"tester")
        self.assertContains(res, b"test data")
        self.assertContains(res, b"Test Category")
        self.assertContains(res, b"Test spell")

    def test_view_spell_authenticated(self):
        """Attempt to view a spell while authenticated."""
        user = create_test_user("tester1")
        category = Category.objects.create(name="Test Category")
        spell = Spell.objects.create(
            creator=user,
            title="Test spell",
            thumbnail=None,
            data="test data",
            category=category
        )
        user2 = create_test_user("tester2")
        self.client.force_login(user2)
        res = self.client.get(reverse("spezspellz:spell", args=(spell.pk, )))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, b"tester1")
        self.assertContains(res, b"test data")
        self.assertContains(res, b"Test Category")
        self.assertContains(res, b"Test spell")

    def test_view_spell_history(self):
        """Attempt to view a spell while authenticated."""
        user = create_test_user("tester1")
        category = Category.objects.create(name="Test Category")
        spell = Spell.objects.create(
            creator=user,
            title="Test spell",
            thumbnail=None,
            data="test data",
            category=category
        )
        user2 = create_test_user("tester2")
        self.client.force_login(user2)
        res = self.client.get(reverse("spezspellz:spell", args=(spell.pk, )))
        self.assertEqual(res.status_code, 200)

        # Test whether history is added
        history_entry = cast(Any, user2).spellhistoryentry_set.first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.spell, spell)

        # Test whether history time gets updated
        first_time = history_entry.time
        res = self.client.get(reverse("spezspellz:spell", args=(spell.pk, )))
        self.assertEqual(res.status_code, 200)
        history_entry2 = cast(Any, user2).spellhistoryentry_set.first()
        self.assertLess(first_time, history_entry2.time)
