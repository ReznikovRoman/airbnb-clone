from model_bakery import baker

from django.test import TestCase
from django.core.validators import MaxValueValidator, MinValueValidator

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

    def test_model_verbose_name_single(self):
        """Test that model verbose name is set correctly."""
        self.assertEqual(RealtyHost._meta.verbose_name, 'realty host')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is set correctly."""
        self.assertEqual(RealtyHost._meta.verbose_name_plural, 'realty hosts')

    def test_host_rating_field_params(self):
        """Test that host_rating field has all required parameters."""
        host_rating_field = RealtyHost._meta.get_field('host_rating')

        self.assertEqual(host_rating_field.verbose_name, 'rating')
        self.assertTrue(host_rating_field.blank)
        self.assertTrue(host_rating_field.null)
        self.assertIn(MinValueValidator(0), host_rating_field.validators)
        self.assertIn(MaxValueValidator(5), host_rating_field.validators)

    def test_object_name_has_first_name_and_last_name(self):
        """Test that RealtyHost object name is set up properly."""
        host: RealtyHost = RealtyHost.objects.first()
        self.assertEqual(str(host), f"Host: {host.user.first_name} {host.user.last_name}")

    def test_host_has_appropriate_group(self):
        """Test that the `host.user` is in the right group (`hosts`)."""
        host: RealtyHost = RealtyHost.objects.first()
        self.assertTrue(host.user.groups.filter(name='hosts').exists())
