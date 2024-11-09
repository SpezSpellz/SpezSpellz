"""Implements user settings api tests."""
from json import dumps as json_stringify
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .utils import create_test_user


class UserSettingsAPITest(TestCase):
    """Tests for user settings API."""

    def test_change_username(self):
        """Test changing username successfully."""
        user = create_test_user()
        self.client.force_login(user)
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify({
                "method": "up_uname",
                "name": "gaynigger"
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.username, "gaynigger")

    def test_change_username_noauth(self):
        """Test changing username without logging in first."""
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify({
                "method": "up_uname",
                "name": "gaynigger"
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 401)

    def test_change_username_empty(self):
        """Test changing username to an empty username."""
        user = create_test_user()
        self.client.force_login(user)
        old_name = user.username
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify({
                "method": "up_uname",
                "name": ""
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.username, old_name)

    def test_change_password(self):
        """Test changing password successfully."""
        user = create_test_user()
        self.client.force_login(user)
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify(
                {
                    "method": "up_passwd",
                    "opasswd": "1234",
                    "npasswd": "4321",
                }
            ),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password("4321"))

    def test_change_password_noauth(self):
        """Test changing password without logging in first."""
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify(
                {
                    "method": "up_passwd",
                    "opasswd": "a",
                    "npasswd": "b",
                }
            ),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 401)

    def test_change_password_wrong_old(self):
        """Test changing password with wrong old password."""
        user = create_test_user()
        self.client.force_login(user)
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify(
                {
                    "method": "up_passwd",
                    "opasswd": "404",
                    "npasswd": "4321",
                }
            ),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password("1234"))

    def test_change_password_empty(self):
        """Test changing password to an empty password."""
        user = create_test_user()
        self.client.force_login(user)
        res = self.client.post(
            reverse("spezspellz:usersettings"),
            json_stringify(
                {
                    "method": "up_passwd",
                    "opasswd": "1234",
                    "npasswd": "",
                }
            ),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password("1234"))
