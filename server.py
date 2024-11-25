"""Launches the server."""
import os

import uvicorn
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

if __name__ == "__main__":
    uvicorn.run("config.asgi:application")
