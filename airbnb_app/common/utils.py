from typing import TypeVar

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage

from airbnb.storage_backends import YandexObjectMediaStorage


BaseStorageType = TypeVar('BaseStorageType', bound=Storage)


def select_file_storage() -> BaseStorageType:
    if settings.USE_S3_BUCKET and not settings.DEBUG:
        return YandexObjectMediaStorage()
    return FileSystemStorage()
