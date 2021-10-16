import shutil
import tempfile
from unittest import mock

import fakeredis

from django.test import SimpleTestCase, TestCase, override_settings

from accounts.models import CustomUser
from addresses.models import Address
from common.session_handler import SessionHandler
from common.testing_utils import create_valid_image
from hosts.models import RealtyHost

from ..constants import REALTY_FORM_KEYS_COLLECTOR_NAME, REALTY_FORM_SESSION_PREFIX
from ..models import Amenity, Realty, RealtyImage, RealtyTypeChoices
from ..services.images import get_image_by_id, get_images_by_realty_id, update_images_order
from ..services.order import ImageOrder, convert_response_to_orders
from ..services.realty import (get_all_available_realty, get_amenity_ids_from_session,
                               get_available_realty_by_city_slug, get_available_realty_by_host,
                               get_available_realty_count_by_city, get_available_realty_filtered_by_type,
                               get_available_realty_search_results, get_cached_realty_visits_count_by_realty_id,
                               get_last_realty, get_n_latest_available_realty, get_or_create_realty_host_by_user,
                               update_realty_visits_count, update_realty_visits_from_redis)


MEDIA_ROOT = tempfile.mkdtemp()


class RealtyServicesRealtyTests(TestCase):
    redis_server = fakeredis.FakeServer()

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
        Realty.objects.create(
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
            country='Italy',
            city='Rome',
            street='Via Bari, 2',
        )
        Realty.objects.create(
            name='Realty 2',
            description='Desc 2',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=2,
            max_guests_count=2,
            price_per_night=40,
            location=test_location2,
            host=test_host1,
        )

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )

        test_user3 = CustomUser.objects.create_user(
            email='user3@gmail.com',
            first_name='Peter',
            last_name='Collins',
            password='test',
        )
        test_host2 = RealtyHost.objects.create(user=test_user3)
        test_location3 = Address.objects.create(
            country='Italy',
            city='Rome',
            street='Via Po',
        )
        Realty.objects.create(
            name='Realty 3',
            description='Desc 3',
            is_available=True,
            realty_type=RealtyTypeChoices.HOTEL,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location3,
            host=test_host2,
        )

        Amenity.objects.create(name='wifi')
        Amenity.objects.create(name='kitchen')
        Amenity.objects.create(name='breakfast')

    def test_get_amenity_ids_from_session_existing_amenities(self):
        """get_amenity_ids_from_session() returns Amenity ids from the session."""
        session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )
        amenity_names = ['wifi', 'kitchen']
        session_handler.add_new_item('amenities', amenity_names)

        amenity_ids = get_amenity_ids_from_session(session_handler)

        self.assertListEqual(
            list(amenity_ids),
            [Amenity.objects.get(name=amenity_names[0]).id, Amenity.objects.get(name=amenity_names[1]).id],
        )

    def test_get_amenity_ids_from_session_no_amenities(self):
        """get_amenity_ids_from_session() returns None if there are no amenities in the session."""
        session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        amenity_ids = get_amenity_ids_from_session(session_handler)

        self.assertIsNone(amenity_ids)

    def test_get_or_create_realty_host_by_user_new_host(self):
        """get_or_create_realty_host_by_user() returns the created RealtyHost object."""
        # user2 is not a host yet
        test_user = CustomUser.objects.get(email='user2@gmail.com')

        host, created = get_or_create_realty_host_by_user(test_user)

        self.assertTrue(created)
        self.assertEqual(host, RealtyHost.objects.get(user=test_user))

    def test_get_or_create_realty_host_by_user_existing_host(self):
        """get_or_create_realty_host_by_user() returns an existing RealtyHost object (by a given `user`)."""
        # user1 is a host
        test_user = CustomUser.objects.get(email='user1@gmail.com')

        host, created = get_or_create_realty_host_by_user(test_user)

        self.assertFalse(created)
        self.assertEqual(host, RealtyHost.objects.get(user=test_user))

    def test_get_all_available_realty(self):
        """get_all_available_realty() returns all Realty objects that are `available`."""
        self.assertListEqual(list(get_all_available_realty()), list(Realty.available.all()))

    def test_get_available_realty_by_host(self):
        """get_available_realty_by_host() returns all available Realty objects from a given `realty_host`."""
        test_user = CustomUser.objects.get(email='user3@gmail.com')
        test_host = RealtyHost.objects.get(user=test_user)

        self.assertListEqual(
            list(get_available_realty_by_host(test_host)),
            [Realty.objects.get(slug='realty-3')],
        )

    def test_get_available_realty_by_city_slug_all_realty(self):
        """get_available_realty_by_city_slug() returns all available realty filtered by a `city_slug`."""
        city_slug = 'moscow'

        self.assertListEqual(
            list(get_available_realty_by_city_slug(city_slug)),
            [Realty.objects.get(slug='realty-1')],
        )

    def test_get_available_realty_by_city_slug_realty_qs(self):
        """get_available_realty_by_city_slug() filters a given QuerySet by a `city_slug`."""
        city_slug = 'moscow'
        test_qs = Realty.available.all()

        self.assertListEqual(
            list(get_available_realty_by_city_slug(city_slug, test_qs)),
            [Realty.objects.get(slug='realty-1')],
        )

    def test_get_available_realty_filtered_by_type_all_realty(self):
        """get_available_realty_filtered_by_type() returns all available realty filtered by `realty_types`."""
        test_types = [RealtyTypeChoices.APARTMENTS]

        self.assertListEqual(
            list(get_available_realty_filtered_by_type(test_types)),
            [Realty.objects.get(slug='realty-2'), Realty.objects.get(slug='realty-1')],
        )

    def test_get_available_realty_filtered_by_type_realty_qs(self):
        """get_available_realty_filtered_by_type() filters a given QuerySet by `realty_types`."""
        test_types = [RealtyTypeChoices.APARTMENTS]
        test_qs = Realty.available.filter(beds_count__gte=2)

        self.assertListEqual(
            list(get_available_realty_filtered_by_type(test_types, test_qs)),
            [Realty.objects.get(slug='realty-2')],
        )

    def test_get_last_realty(self):
        """get_last_realty() returns the latest Realty object."""
        self.assertEqual(get_last_realty(), Realty.objects.last())

    def test_get_n_latest_available_realty(self):
        """get_n_latest_available_realty() returns `realty_count` latest Realty objects."""
        test_count = 2
        self.assertListEqual(
            list(get_n_latest_available_realty(test_count)),
            [Realty.objects.get(slug='realty-3'), Realty.objects.get(slug='realty-2')],
        )

    def test_get_available_realty_count_by_city(self):
        """get_available_realty_count_by_city() returns count of available Realty objects in the given `city`."""
        test_city = 'Rome'
        self.assertEqual(get_available_realty_count_by_city(test_city), 2)

    def test_get_available_realty_search_results_no_query(self):
        """get_available_realty_search_results() returns all available Realty objects if `query` is not given."""
        self.assertListEqual(
            list(get_available_realty_search_results()),
            list(Realty.available.all()),
        )

    def test_get_available_realty_search_results_with_query(self):
        """get_available_realty_search_results() returns available Realty objects filtered by the `query`."""
        test_query = 'realty 1'

        self.assertListEqual(
            list(get_available_realty_search_results(test_query)),
            [Realty.objects.get(slug='realty-1')],
        )

    @mock.patch('realty.services.realty.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_get_cached_realty_visits_count_by_id(self):
        """get_cached_realty_visits_count_by_id() returns realty visits count from Redis DB."""
        realty_id = 5
        realty_visits_count = 5
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        r.flushall()

        r.set(f"realty:{str(realty_id)}:views_count", realty_visits_count)

        self.assertEqual(get_cached_realty_visits_count_by_realty_id(realty_id), realty_visits_count)

    @mock.patch('realty.services.realty.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_update_realty_visits_count(self):
        """update_realty_visits_count() increments counter in the Redis DB."""
        realty_id = 5
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        r.flushall()

        self.assertEqual(get_cached_realty_visits_count_by_realty_id(realty_id), 0)

        update_realty_visits_count(realty_id)
        self.assertEqual(get_cached_realty_visits_count_by_realty_id(realty_id), 1)

    @mock.patch('realty.services.realty.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_update_realty_visits_from_redis(self):
        """update_realty_visits_from_redis() updates `visits_count` field in DB using Redis values."""
        realty = Realty.objects.first()
        visits_count = 10
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        r.flushall()

        self.assertEqual(realty.visits_count, 0)

        r.set(f"realty:{realty.id}:views_count", visits_count)
        update_realty_visits_from_redis()
        realty.refresh_from_db()

        self.assertEqual(realty.visits_count, visits_count)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RealtyServicesImagesTests(TestCase):

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
        test_realty2 = Realty.objects.create(
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

        test_image_name1_1 = 'image1_1.png'
        test_image1_1 = create_valid_image(test_image_name1_1)
        RealtyImage.objects.create(
            image=test_image1_1,
            realty=test_realty1,
        )

        test_image_name1_2 = 'image1_2.png'
        test_image1_2 = create_valid_image(test_image_name1_2)
        RealtyImage.objects.create(
            image=test_image1_2,
            realty=test_realty1,
        )

        test_image_name1_3 = 'image1_3.png'
        test_image1_3 = create_valid_image(test_image_name1_3)
        RealtyImage.objects.create(
            image=test_image1_3,
            realty=test_realty1,
        )

        test_image_name2 = 'image2.png'
        test_image2 = create_valid_image(test_image_name2)
        RealtyImage.objects.create(
            image=test_image2,
            realty=test_realty2,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete temp media dir
        RealtyImage.objects.delete()
        super().tearDownClass()

    def test_get_images_by_realty_id(self):
        """get_images_by_realty_id() returns RealtyImage objects by the given `realty_id`."""
        test_realty_id = Realty.objects.first().id
        self.assertListEqual(
            list(get_images_by_realty_id(test_realty_id)),
            [Realty.objects.first().images.first()],
        )

    def test_get_image_by_id(self):
        """get_image_by_id() returns a RealtyImage object by the given `image_id`."""
        test_image_id = RealtyImage.objects.first().id
        self.assertListEqual(
            list(get_image_by_id(test_image_id)),
            [RealtyImage.objects.get(id=test_image_id)],
        )

    def test_update_images_order(self):
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        test_image1: RealtyImage = test_realty.images.all()[0]
        test_image2: RealtyImage = test_realty.images.all()[1]
        test_image3: RealtyImage = test_realty.images.all()[2]

        new_order = [
            ImageOrder(image_id=test_image1.id, order=1),
            ImageOrder(image_id=test_image2.id, order=0),
            ImageOrder(image_id=test_image3.id, order=2),
        ]

        update_images_order(new_order)

        test_image1.refresh_from_db()
        test_image2.refresh_from_db()
        test_image3.refresh_from_db()

        self.assertEqual(test_image1.order, 1)
        self.assertEqual(test_image2.order, 0)
        self.assertEqual(test_image3.order, 2)


class RealtyServicesOrderTests(SimpleTestCase):
    def test_convert_response_to_orders(self):
        """convert_response_to_orders() converts response to the list of ImageOrders."""
        # Response: list of tuples where the first element is a RealtyImage ID and the last one - image order
        test_response = [
            ('5', 1),
            ('6', 0),
            ('7', 2),
            ('', 3),  # should skip all items, where image id is not a digit
        ]

        self.assertListEqual(
            convert_response_to_orders(test_response),
            list2=[
                ImageOrder('5', 1),
                ImageOrder('6', 0),
                ImageOrder('7', 2),
            ],
        )
