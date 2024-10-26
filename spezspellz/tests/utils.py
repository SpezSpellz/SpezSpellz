"""Utility functions for tests."""
from django.contrib.auth.models import User


def create_test_user(username="tester"):
    """Create a test user."""
    user = User(username=username)
    user.set_password("1234")
    user.save()
    return user
