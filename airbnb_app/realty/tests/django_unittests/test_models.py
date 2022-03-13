import shutil
import tempfile

from django.core.validators import MaxValueValidator, MinValueValidator
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import CustomUser
from addresses.models import Address
from common.testing_utils import create_valid_image
from hosts.models import RealtyHost
from realty.fields import OrderField
from realty.models import (
    Amenity, AvailableRealtyManager, Realty, RealtyImage, RealtyImageModelManager, RealtyManager, RealtyTypeChoices,
    get_realty_image_upload_path,
)


MEDIA_ROOT = tempfile.mkdtemp()


class AmenityModelTests(TestCase):
    def setUp(self) -> None:
        Amenity.objects.create(name='wifi')

    def test_model_verbose_name_single(self):
        """Amenity verbose name is correct."""
        self.assertEqual(Amenity._meta.verbose_name, 'amenity')

    def test_model_verbose_name_plural(self):
        """Amenity verbose name (in plural) is correct."""
        self.assertEqual(Amenity._meta.verbose_name_plural, 'amenities')

    def test_name_field_params(self):
        """`name` field has all required parameters."""
        name_field = Amenity._meta.get_field('name')

        self.assertEqual(name_field.verbose_name, 'name')
        self.assertEqual(name_field.max_length, 100)

    def test_object_name_is_name(self):
        """Amenity object name is set up properly."""
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
        """Realty verbose name is set correctly."""
        self.assertEqual(Realty._meta.verbose_name, 'realty')

    def test_model_verbose_name_plural(self):
        """Realty verbose name (in plural) is set correctly."""
        self.assertEqual(Realty._meta.verbose_name_plural, 'realty')

    def test_model_ordering_is_desc_created(self):
        """Realty default ordering is correct."""
        self.assertTupleEqual(Realty._meta.ordering, ('-created',))

    def test_name_field_correct_params(self):
        """`name` field has all required parameters."""
        name_field = Realty._meta.get_field('name')

        self.assertEqual(name_field.verbose_name, 'name')
        self.assertEqual(name_field.max_length, 255)

    def test_slug_field_correct_params(self):
        """`slug` field has all required parameters."""
        slug_field = Realty._meta.get_field('slug')

        self.assertEqual(slug_field.verbose_name, 'slug')
        self.assertEqual(slug_field.max_length, 255)

    def test_description_field_correct_params(self):
        """`description` field has all required parameters."""
        description_field = Realty._meta.get_field('description')

        self.assertEqual(description_field.verbose_name, 'description')

    def test_is_available_field_correct_params(self):
        """`is_available` field has all required parameters."""
        is_available_field = Realty._meta.get_field('is_available')

        self.assertEqual(is_available_field.verbose_name, 'is realty available')
        self.assertFalse(is_available_field.default)

    def test_created_field_correct_params(self):
        """`created` field has all required parameters."""
        created_field = Realty._meta.get_field('created')

        self.assertEqual(created_field.verbose_name, 'creation date')
        self.assertTrue(created_field.auto_now_add)

    def test_updated_field_correct_params(self):
        """`updated` field has all required parameters."""
        updated_field = Realty._meta.get_field('updated')

        self.assertEqual(updated_field.verbose_name, 'update date')
        self.assertTrue(updated_field.auto_now)

    def test_visits_count_field_correct_params(self):
        """`visits_count` field has all required parameters."""
        visits_count_field = Realty._meta.get_field('visits_count')

        self.assertEqual(visits_count_field.verbose_name, 'visits count')
        self.assertEqual(visits_count_field.default, 0)

    def test_realty_type_field_correct_params(self):
        """`realty_type` field has all required parameters."""
        realty_type_field = Realty._meta.get_field('realty_type')

        self.assertEqual(realty_type_field.verbose_name, 'type of the realty')
        self.assertEqual(realty_type_field.max_length, 31)
        self.assertEqual(realty_type_field.choices, RealtyTypeChoices.choices)
        self.assertEqual(realty_type_field.default, RealtyTypeChoices.APARTMENTS)

    def test_beds_count_field_correct_params(self):
        """`beds_count` field has all required parameters."""
        beds_count_field = Realty._meta.get_field('beds_count')

        self.assertEqual(beds_count_field.verbose_name, 'beds count')
        self.assertIn(MinValueValidator(1), beds_count_field.validators)
        self.assertIn(MaxValueValidator(8), beds_count_field.validators)

    def test_max_guests_count_field_correct_params(self):
        """`max_guests_count` field has all required parameters."""
        max_guests_count_field = Realty._meta.get_field('max_guests_count')

        self.assertEqual(max_guests_count_field.verbose_name, 'maximum guests amount')
        self.assertIn(MinValueValidator(1), max_guests_count_field.validators)
        self.assertIn(MaxValueValidator(100), max_guests_count_field.validators)

    def test_price_per_night_field_correct_params(self):
        """`price_per_night` field has all required parameters."""
        price_per_night_field = Realty._meta.get_field('price_per_night')

        self.assertEqual(price_per_night_field.verbose_name, 'price per night')
        self.assertIn(MinValueValidator(1), price_per_night_field.validators)

    def test_location_field_correct_params(self):
        """`location` field has all required parameters."""
        location_field = Realty._meta.get_field('location')
        self.assertEqual(location_field.verbose_name, 'location')

    def test_host_field_correct_params(self):
        """`host` field has all required parameters."""
        host_field = Realty._meta.get_field('host')
        self.assertEqual(host_field.verbose_name, 'realty host')

    def test_amenities_field_correct_params(self):
        """`amenities` field has all required parameters."""
        amenities_field = Realty._meta.get_field('amenities')

        self.assertEqual(amenities_field.verbose_name, 'amenities')
        self.assertTrue(amenities_field.blank)

    def test_objects_manager(self):
        """Default object manager is a custom manager."""
        self.assertIsInstance(Realty.objects, RealtyManager)

    def test_available_manager(self):
        """`available` manager is a `AvailableRealty` manager, and it returns only `available` realty."""
        self.assertIsInstance(Realty.available, AvailableRealtyManager)
        self.assertListEqual(list(Realty.available.all()), [Realty.objects.get(slug='realty-1')])

    def test_object_name_is_name(self):
        """Realty object name is set up correctly."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        self.assertEqual(str(test_realty), test_realty.name)

    def test_save_slugify_name(self):
        """`name` field is 'slugified' and saved to a `slug` field."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        self.assertEqual(test_realty.slug, 'realty-1')

    def test_get_absolute_url(self):
        """Absolute url includes object's ID and `slug`."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        self.assertEqual(
            test_realty.get_absolute_url(),
            reverse('realty:detail', kwargs={"pk": test_realty.id, "slug": test_realty.slug}),
        )

    def test_delete_object_removes_location(self):
        """`location` is deleted on Realty object deletion."""
        test_address_id = Address.objects.first().id
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        test_realty.delete()

        self.assertFalse(Address.objects.filter(id=test_address_id).exists())

    def test_delete_qs_removes_location(self):
        """`location` is deleted on Realty QuerySet deletion."""
        test_address_id = Address.objects.first().id
        Realty.objects.filter(slug='realty-1').delete()

        self.assertFalse(Address.objects.filter(id=test_address_id).exists())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RealtyImageModelTests(TestCase):
    def setUp(self) -> None:
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

        test_location2 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Ulitsa Zorge, 14',
        )
        Realty.objects.create(
            name='Image test',
            description='Desc 1',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location2,
            host=test_host1,
        )

        test_image_name1 = 'image1.png'
        test_image1 = create_valid_image(test_image_name1)

        RealtyImage.objects.create(
            image=test_image1,
            realty=test_realty1,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete temp media dir
        super().tearDownClass()

    def test_model_verbose_name_single(self):
        """`RealtyImage` verbose name is set correctly."""
        self.assertEqual(RealtyImage._meta.verbose_name, 'realty image')

    def test_model_verbose_name_plural(self):
        """`RealtyImage` verbose name (in plural) is set correctly."""
        self.assertEqual(RealtyImage._meta.verbose_name_plural, 'realty images')

    def test_model_ordering_is_asc_created(self):
        """`RealtyImage` default ordering is correct."""
        self.assertTupleEqual(RealtyImage._meta.ordering, ('order',))

    def test_get_realty_image_upload_path(self):
        """get_realty_image_upload_path() returns path to the file based on `realty.id` and `filename`."""
        test_realty_image = RealtyImage.objects.first()
        test_filename = 'image.png'

        upload_path = get_realty_image_upload_path(instance=test_realty_image, filename=test_filename)

        self.assertEqual(upload_path, f"upload/images/realty/{test_realty_image.realty.id}/{test_filename}")

    def test_image_field_params(self):
        """`image` field has all required parameters."""
        image_field = RealtyImage._meta.get_field('image')

        self.assertEqual(image_field.verbose_name, 'image')
        self.assertEqual(image_field.upload_to, get_realty_image_upload_path)

    def test_realty_field_params(self):
        """`realty` field has all required parameters."""
        realty_field = RealtyImage._meta.get_field('realty')

        self.assertEqual(realty_field.verbose_name, 'realty')

    def test_order_field_params(self):
        """`order` field has all required parameters, and it is a custom `OrderField`."""
        order_field = RealtyImage._meta.get_field('order')

        self.assertIsInstance(order_field, OrderField)
        self.assertEqual(order_field.verbose_name, 'order')
        self.assertTrue(order_field.blank)
        self.assertTrue(order_field.null)
        self.assertListEqual(order_field.related_fields, ['realty'])

    def test_objects_manager(self):
        """Default object manager is a custom manager."""
        self.assertIsInstance(RealtyImage.objects, RealtyImageModelManager)

    def test_object_name_has_id_and_realty_name(self):
        """`RealtyImage` is set up correctly."""
        test_realty_image = RealtyImage.objects.first()
        self.assertEqual(str(test_realty_image), f"Image #{test_realty_image.id} for {test_realty_image.realty.name}")

    def test_delete_object_updates_ordering_first_image(self):
        """If RealtyImage object is deleted, ordering of images is updated."""
        test_realty = Realty.objects.get(slug='image-test')

        # create 3 RealtyImage objects
        test_image1 = create_valid_image('image1')
        test_realty_image1 = RealtyImage.objects.create(realty=test_realty, image=test_image1)

        test_image2 = create_valid_image('image2')
        test_realty_image2 = RealtyImage.objects.create(realty=test_realty, image=test_image2)

        test_image3 = create_valid_image('image3')
        test_realty_image3 = RealtyImage.objects.create(realty=test_realty, image=test_image3)

        # delete the first RealtyImage
        test_realty_image1.delete()

        # refresh remaining objects
        test_realty_image2.refresh_from_db()
        test_realty_image3.refresh_from_db()

        ordering = test_realty.images.values_list('order', flat=True)

        # first image has been deleted --> image ordering has been changed
        self.assertListEqual(list(ordering), [0, 1])
        self.assertEqual(test_realty_image2.order, 0)
        self.assertEqual(test_realty_image3.order, 1)

    def test_delete_object_updates_ordering_middle_image(self):
        """If RealtyImage object is deleted, ordering of images is updated.

        If image was not the first one, order of previous images remains the same.
        """
        test_realty = Realty.objects.get(slug='image-test')

        # create 3 RealtyImage objects
        test_image1 = create_valid_image('image1')
        test_realty_image1 = RealtyImage.objects.create(realty=test_realty, image=test_image1)

        test_image2 = create_valid_image('image2')
        test_realty_image2 = RealtyImage.objects.create(realty=test_realty, image=test_image2)

        test_image3 = create_valid_image('image3')
        test_realty_image3 = RealtyImage.objects.create(realty=test_realty, image=test_image3)

        # delete the second RealtyImage
        test_realty_image2.delete()

        # refresh remaining objects
        test_realty_image1.refresh_from_db()
        test_realty_image3.refresh_from_db()

        ordering = test_realty.images.values_list('order', flat=True)

        # first image has been deleted --> image ordering has been changed
        self.assertListEqual(list(ordering), [0, 1])
        self.assertEqual(test_realty_image1.order, 0)
        self.assertEqual(test_realty_image3.order, 1)

    def test_delete_object_updates_ordering_last_image(self):
        """If RealtyImage object is deleted, ordering of images is updated.

        If image was the last one, order of previous images remains the same.
        """
        test_realty = Realty.objects.get(slug='image-test')

        # create 3 RealtyImage objects
        test_image1 = create_valid_image('image1')
        test_realty_image1 = RealtyImage.objects.create(realty=test_realty, image=test_image1)

        test_image2 = create_valid_image('image2')
        test_realty_image2 = RealtyImage.objects.create(realty=test_realty, image=test_image2)

        test_image3 = create_valid_image('image3')
        test_realty_image3 = RealtyImage.objects.create(realty=test_realty, image=test_image3)

        # delete the last RealtyImage
        test_realty_image3.delete()

        # refresh remaining objects
        test_realty_image1.refresh_from_db()
        test_realty_image2.refresh_from_db()

        ordering = test_realty.images.values_list('order', flat=True)

        # last image has been deleted --> image ordering hasn't changed
        self.assertListEqual(list(ordering), [0, 1])
        self.assertEqual(test_realty_image1.order, 0)
        self.assertEqual(test_realty_image2.order, 1)

    def test_delete_qs_updates_ordering_middle_image(self):
        """If RealtyImage QuerySet is deleted, ordering of images is updated.

        If image was not the first one, order of previous images remains the same.
        """
        test_realty = Realty.objects.get(slug='image-test')

        # create 3 RealtyImage objects
        test_image1 = create_valid_image('image1')
        test_realty_image1 = RealtyImage.objects.create(realty=test_realty, image=test_image1)

        test_image2 = create_valid_image('image2')
        test_realty_image2 = RealtyImage.objects.create(realty=test_realty, image=test_image2)

        test_image3 = create_valid_image('image3')
        test_realty_image3 = RealtyImage.objects.create(realty=test_realty, image=test_image3)

        # delete QuerySet (with the second image)
        RealtyImage.objects.filter(id=test_realty_image2.id).delete()

        # refresh remaining objects
        test_realty_image1.refresh_from_db()
        test_realty_image3.refresh_from_db()

        ordering = test_realty.images.values_list('order', flat=True)

        # first image has been deleted --> image ordering has been changed
        self.assertListEqual(list(ordering), [0, 1])
        self.assertEqual(test_realty_image1.order, 0)
        self.assertEqual(test_realty_image3.order, 1)
