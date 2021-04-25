from model_bakery import baker

from django.test import TestCase

from ..models import RealtyHost


class RealtyHostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_user = baker.make('CustomUser')
        baker.make(
            'RealtyHost',
            user=test_user,
            host_rating=4,
        )

    def test_host_rating_verbose_name(self):
        """Test that host_rating verbose name is set correctly."""
        host: RealtyHost = RealtyHost.objects.first()
        host_rating_verbose_name = host._meta.get_field('host_rating').verbose_name
        self.assertEqual(host_rating_verbose_name, 'rating')

    def test_object_name_has_first_name_and_last_name(self):
        """Test that object name is set up properly."""
        host: RealtyHost = RealtyHost.objects.first()
        expected_object_name = f"Host: {host.user.first_name} {host.user.last_name}"
        self.assertEqual(str(host), expected_object_name)

    def test_host_has_appropriate_group(self):
        """Test that the `host.user` is in the right group (`hosts`)."""
        host: RealtyHost = RealtyHost.objects.first()
        self.assertTrue(host.user.groups.filter(name='hosts').exists())
