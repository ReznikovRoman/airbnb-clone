from django.test import TestCase
from django.utils.text import slugify

from ..models import Address


class AddressModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Address.objects.create(
            country='USA',
            city='Los Angeles',
            street='Melrose Avenue',
        )

    def test_model_verbose_name_single(self):
        """Test that model verbose name is set correctly."""
        self.assertEqual(Address._meta.verbose_name, 'address')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is set correctly."""
        self.assertEqual(Address._meta.verbose_name_plural, 'addresses')

    def test_country_field_params(self):
        """Test that country field has all required parameters."""
        country_field = Address._meta.get_field('country')

        self.assertEqual(country_field.verbose_name, 'country')
        self.assertEqual(country_field.max_length, 255)

    def test_city_field_params(self):
        """Test that city field has all required parameters."""
        city_field = Address._meta.get_field('city')

        self.assertEqual(city_field.verbose_name, 'city')
        self.assertEqual(city_field.max_length, 255)

    def test_street_field_params(self):
        """Test that street field has all required parameters."""
        street_field = Address._meta.get_field('street')

        self.assertEqual(street_field.verbose_name, 'street')
        self.assertEqual(street_field.max_length, 255)

    def test_object_name_has_object_id(self):
        """Test that Address object name is set up properly."""
        address: Address = Address.objects.first()
        self.assertEqual(str(address), f"Address #{address.id}")

    def test_country_slug_created_on_object_save(self):
        """Test that `country_slug` is set on object save."""
        address: Address = Address.objects.first()
        self.assertEqual(address.country_slug, slugify(address.country))

    def test_city_slug_created_on_object_save(self):
        """Test that `city_slug` is set on object save."""
        address: Address = Address.objects.first()
        self.assertEqual(address.city_slug, slugify(address.city))

    def test_get_full_address_correct_output(self):
        """Test that `get_full_address` return value consists of `country`, `city` and `street`."""
        address: Address = Address.objects.first()
        expected_value = f"{address.country}, {address.city}: {address.street}"
        self.assertEqual(address.get_full_address(), expected_value)
