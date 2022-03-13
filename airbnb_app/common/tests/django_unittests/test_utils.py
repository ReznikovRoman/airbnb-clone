from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase, override_settings

from airbnb.storage_backends import YandexObjectMediaStorage
from common.utils import select_file_storage


class CommonServicesTests(SimpleTestCase):

    @override_settings(
        USE_S3_BUCKET=True,
        DEBUG=False,
    )
    def test_select_file_storage_yandex_in_prod(self):
        """select_file_storage() returns Yandex Object Storage instance with production settings."""
        result = select_file_storage()
        self.assertIsInstance(result, YandexObjectMediaStorage)

    @override_settings(
        USE_S3_BUCKET=False,
        DEBUG=True,
    )
    def test_select_file_storage_django_storage_in_local(self):
        """select_file_storage() returns default Django File Storage instance with local settings."""
        result = select_file_storage()
        self.assertIsInstance(result, FileSystemStorage)

    @override_settings(
        USE_S3_BUCKET=True,
        DEBUG=True,
    )
    def test_select_file_storage_django_storage_in_debug_mode(self):
        """select_file_storage() returns default Django File Storage instance in the `debug` mode."""
        result = select_file_storage()
        self.assertIsInstance(result, FileSystemStorage)
