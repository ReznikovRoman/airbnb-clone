from django.test import TestCase
from django.utils.text import slugify

from ..models import Address


class AddressModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        test_address = Address.objects.create(
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

    def test_country_verbose_name(self):
        """Test that country verbose name is set correctly."""
        address: Address = Address.objects.first()
        country_verbose_name = address._meta.get_field('country').verbose_name
        self.assertEqual(country_verbose_name, 'country')

    def test_city_verbose_name(self):
        """Test that city verbose name is set correctly."""
        address: Address = Address.objects.first()
        city_verbose_name = address._meta.get_field('city').verbose_name
        self.assertEqual(city_verbose_name, 'city')

    def test_street_verbose_name(self):
        """Test that street verbose name is set correctly."""
        address: Address = Address.objects.first()
        street_verbose_name = address._meta.get_field('street').verbose_name
        self.assertEqual(street_verbose_name, 'street')

    def test_object_name_has_object_id(self):
        """Test that object name is set up properly."""
        address: Address = Address.objects.first()
        expected_object_name = f"Address #{address.id}"
        self.assertEqual(str(address), expected_object_name)

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
