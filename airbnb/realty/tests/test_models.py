from django.test import TestCase
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

from hosts.models import RealtyHost
from accounts.models import CustomUser
from addresses.models import Address
from ..models import (Amenity, Realty, RealtyTypeChoices, RealtyManager, AvailableRealtyManager)


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


class RealtyModelTests(TestCase):
    def setUp(self) -> None:
        test_amenity1 = Amenity.objects.create(name='kitchen')
        test_amenity2 = Amenity.objects.create(name='wifi')

        test_user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        test_host1 = RealtyHost.objects.create(user=test_user1)
        test_location1 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Arbat, 20',
        )
        test_realty1 = Realty.objects.create(
            name='Realty 1',
            description='Desc 1',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location1,
            host=test_host1,
        )
        test_realty1.amenities.add(test_amenity1, test_amenity2)

        test_location2 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Ulitsa Zorge, 14',
        )
        Realty.objects.create(
            name='Realty 2',
            description='Desc 2',
            is_available=False,
            realty_type=RealtyTypeChoices.HOTEL,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location2,
            host=test_host1,
        )

    def test_model_verbose_name_single(self):
        """Test that model verbose name is set correctly."""
        self.assertEqual(Realty._meta.verbose_name, 'realty')

    def test_model_verbose_name_plural(self):
        """Test that model verbose name (in plural) is set correctly."""
        self.assertEqual(Realty._meta.verbose_name_plural, 'realty')

    def test_model_ordering_is_desc_created(self):
        """Test that model's default ordering is correct."""
        self.assertTupleEqual(Realty._meta.ordering, ('-created',))

    def test_name_field_correct_params(self):
        """Test that `name` field has all required parameters."""
        name_field = Realty._meta.get_field('name')

        self.assertEqual(name_field.verbose_name, 'name')
        self.assertEqual(name_field.max_length, 255)

    def test_slug_field_correct_params(self):
        """Test that `slug` field has all required parameters."""
        slug_field = Realty._meta.get_field('slug')

        self.assertEqual(slug_field.verbose_name, 'slug')
        self.assertEqual(slug_field.max_length, 255)

    def test_description_field_correct_params(self):
        """Test that `description` field has all required parameters."""
        description_field = Realty._meta.get_field('description')

        self.assertEqual(description_field.verbose_name, 'description')

    def test_is_available_field_correct_params(self):
        """Test that `is_available` field has all required parameters."""
        is_available_field = Realty._meta.get_field('is_available')

        self.assertEqual(is_available_field.verbose_name, 'is realty available')
        self.assertFalse(is_available_field.default)

    def test_created_field_correct_params(self):
        """Test that `created` field has all required parameters."""
        created_field = Realty._meta.get_field('created')

        self.assertEqual(created_field.verbose_name, 'creation date')
        self.assertTrue(created_field.auto_now_add)

    def test_updated_field_correct_params(self):
        """Test that `updated` field has all required parameters."""
        updated_field = Realty._meta.get_field('updated')

        self.assertEqual(updated_field.verbose_name, 'update date')
        self.assertTrue(updated_field.auto_now)

    def test_realty_type_field_correct_params(self):
        """Test that `realty_type` field has all required parameters."""
        realty_type_field = Realty._meta.get_field('realty_type')

        self.assertEqual(realty_type_field.verbose_name, 'type of the realty')
        self.assertEqual(realty_type_field.max_length, 31)
        self.assertEqual(realty_type_field.choices, RealtyTypeChoices.choices)
        self.assertEqual(realty_type_field.default, RealtyTypeChoices.APARTMENTS)

    def test_beds_count_field_correct_params(self):
        """Test that `beds_count` field has all required parameters."""
        beds_count_field = Realty._meta.get_field('beds_count')

        self.assertEqual(beds_count_field.verbose_name, 'beds count')
        self.assertIn(MinValueValidator(1), beds_count_field.validators)
        self.assertIn(MaxValueValidator(8), beds_count_field.validators)

    def test_max_guests_count_field_correct_params(self):
        """Test that `max_guests_count` field has all required parameters."""
        max_guests_count_field = Realty._meta.get_field('max_guests_count')

        self.assertEqual(max_guests_count_field.verbose_name, 'maximum guests amount')
        self.assertIn(MinValueValidator(1), max_guests_count_field.validators)
        self.assertIn(MaxValueValidator(100), max_guests_count_field.validators)

    def test_price_per_night_field_correct_params(self):
        """Test that `price_per_night` field has all required parameters."""
        price_per_night_field = Realty._meta.get_field('price_per_night')

        self.assertEqual(price_per_night_field.verbose_name, 'price per night')
        self.assertIn(MinValueValidator(1), price_per_night_field.validators)

    def test_location_field_correct_params(self):
        """Test that `location` field has all required parameters."""
        location_field = Realty._meta.get_field('location')
        self.assertEqual(location_field.verbose_name, 'location')

    def test_host_field_correct_params(self):
        """Test that `host` field has all required parameters."""
        host_field = Realty._meta.get_field('host')
        self.assertEqual(host_field.verbose_name, 'realty host')

    def test_amenities_field_correct_params(self):
        """Test that `amenities` field has all required parameters."""
        amenities_field = Realty._meta.get_field('amenities')

        self.assertEqual(amenities_field.verbose_name, 'amenities')
        self.assertTrue(amenities_field.blank)

    def test_objects_manager(self):
        """Test that default object manager is a custom manager."""
        self.assertIsInstance(Realty.objects, RealtyManager)

    def test_available_manager(self):
        """Test that `available` manager is a `AvailableRealty` manager, and it returns only `available` realty."""
        self.assertIsInstance(Realty.available, AvailableRealtyManager)
        self.assertListEqual(list(Realty.available.all()), [Realty.objects.get(slug='realty-1')])

    def test_object_name_is_name(self):
        """Test that Realty object name is set up correctly."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        self.assertEqual(str(test_realty), test_realty.name)

    def test_save_slugify_name(self):
        """Test that `name` field is 'slugified' and saved to a `slug` field."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        self.assertEqual(test_realty.slug, 'realty-1')

    def test_get_absolute_url(self):
        """Test that absolute url includes object's ID and `slug`."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        self.assertEqual(test_realty.get_absolute_url(),
                         reverse('realty:detail', kwargs={"pk": test_realty.id, "slug": test_realty.slug}))

    def test_delete_object_removes_location(self):
        """Test that `location` is deleted on Realty object deletion."""
        test_address_id = Address.objects.first().id
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        test_realty.delete()

        self.assertFalse(Address.objects.filter(id=test_address_id).exists())

    def test_delete_qs_removes_location(self):
        """Test that `location` is deleted on Realty QuerySet deletion."""
        test_address_id = Address.objects.first().id
        Realty.objects.filter(slug='realty-1').delete()

        self.assertFalse(Address.objects.filter(id=test_address_id).exists())
