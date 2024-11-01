"""Implements a translation layer from file to model."""
from io import BytesIO
from typing import cast, Any
from django.db.models import Model, BinaryField, CharField
from django.core.files import File
from django.core.files.storage import Storage


class VirtualFileModel(Model):
    """Stores on file on database."""

    path: CharField = CharField(max_length=256, unique=True, primary_key=True)
    data: BinaryField = BinaryField(max_length=50000000)


class File2Model(Storage):
    """Converts file to model."""

    def delete(self, name: str):
        """Delete."""
        VirtualFileModel.objects.get(path=name).delete()

    def exists(self, name: str):
        """Exist."""
        try:
            VirtualFileModel.objects.get(path=name)
        except Exception:
            return False
        return True

    def size(self, name) -> int:
        """Size."""
        file = VirtualFileModel.objects.get(path=name)
        return len(file.data)

    def _open(self, name, mode) -> File:
        """Open."""
        vfile = VirtualFileModel.objects.get(path=name)
        return File(file=cast(Any, BytesIO(vfile.data)), name=vfile.path)

    def _save(self, name, content):
        """Save."""
        VirtualFileModel.objects.create(path=name, data=content.read())
        return name
