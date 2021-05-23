from django.test import TestCase

from ..models import Amenity


class AmenityModelTests(TestCase):
    def setUp(self) -> None:
        Amenity.objects.create(name='wifi')

    def test_model_verbose_name_single(self):
        """Test that model verbose name is correct."""
        self.assertEqual(Amenity._meta.verbose_name, 'amenity')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is correct."""
        self.assertEqual(Amenity._meta.verbose_name_plural, 'amenities')

    def test_name_field_params(self):
        """Test that `name` field has all required parameters."""
        name_field = Amenity._meta.get_field('name')

        self.assertEqual(name_field.verbose_name, 'name')
        self.assertEqual(name_field.max_length, 100)

    def test_object_name_is_name(self):
        """Test that Amenity object name is set up properly."""
        test_amenity: Amenity = Amenity.objects.first()
        self.assertEqual(str(test_amenity), test_amenity.name)
