from django.conf import settings
from django.test import SimpleTestCase, override_settings

from ..services import get_target_image_url_with_size


class MainServicesSimpleTests(SimpleTestCase):

    @override_settings(
        USE_S3_BUCKET=False,  # disable S3 bucket
    )
    def test_get_target_image_url_with_size_s3_disabled(self):
        """Return initial url if S3 bucket is disabled."""
        image_url = f"{settings.MEDIA_URL}path/to/image.png"
        target_size = "300x300"

        result = get_target_image_url_with_size(image_url=image_url, target_size=target_size)

        self.assertEqual(result, image_url)

    @override_settings(
        USE_S3_BUCKET=True,  # enable S3 bucket
    )
    def test_get_target_image_url_with_size_correct_url(self):
        """Return url with specified size if S3 bucket is enabled."""
        image_url = f"{settings.MEDIA_URL}path/to/image.png"
        target_size = "300x300"

        result = get_target_image_url_with_size(image_url=image_url, target_size=target_size)
        expected_result = f"{settings.RESIZED_MEDIA_URL}path/to/300x300/image.png"
        self.assertEqual(result, expected_result)

    @override_settings(
        USE_S3_BUCKET=True,  # enable S3 bucket
    )
    def test_get_target_image_url_with_size_wrong_size_separator(self):
        """Return initial url if `target_size` has incorrect separator."""
        image_url = f"{settings.MEDIA_URL}path/to/image.png"
        target_size = "300|300"

        result = get_target_image_url_with_size(image_url=image_url, target_size=target_size)
        self.assertEqual(result, image_url)

    @override_settings(
        USE_S3_BUCKET=True,  # enable S3 bucket
    )
    def test_get_target_image_url_with_size_wrong_size_format(self):
        """Return initial url if `target_size` has incorrect format."""
        image_url = f"{settings.MEDIA_URL}path/to/image.png"
        target_size = "300x300dad"

        result = get_target_image_url_with_size(image_url=image_url, target_size=target_size)
        self.assertEqual(result, image_url)
