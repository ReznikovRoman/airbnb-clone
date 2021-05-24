from django.test import TestCase

from hosts.models import RealtyHost
from accounts.models import CustomUser
from addresses.models import Address
from common.session_handler import SessionHandler
from ..models import Amenity, Realty, RealtyTypeChoices
from ..services.realty import (get_amenity_ids_from_session, set_realty_host_by_user, get_all_available_realty,
                               get_available_realty_by_city_slug, get_available_realty_by_host,
                               get_available_realty_filtered_by_type, get_last_realty, get_n_latest_available_realty,
                               get_available_realty_count_by_city, get_available_realty_search_results)
from ..constants import REALTY_FORM_SESSION_PREFIX, REALTY_FORM_KEYS_COLLECTOR_NAME


class RealtyServicesRealtyTests(TestCase):
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

    def test_set_realty_host_by_user_new_host(self):
        """set_realty_host_by_user() updates `host` field with the new host."""
        # user2 is not a host yet
        test_user = CustomUser.objects.get(email='user2@gmail.com')

        test_realty = Realty.objects.get(slug='realty-1')

        set_realty_host_by_user(test_realty, test_user)
        new_host = RealtyHost.objects.get(user=test_user)

        test_realty.refresh_from_db()

        self.assertEqual(test_realty.host, new_host)

    def test_set_realty_host_by_user_existing_host(self):
        """set_realty_host_by_user() updates `host` field with the existing host."""
        # user1 is a host
        test_user = CustomUser.objects.get(email='user1@gmail.com')

        test_realty = Realty.objects.get(slug='realty-1')

        set_realty_host_by_user(test_realty, test_user)
        new_host = RealtyHost.objects.get(user=test_user)

        test_realty.refresh_from_db()

        self.assertEqual(test_realty.host, new_host)

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
        """get_available_realty_search_results() returns available Realty objects filtered by the `query` ."""
        test_query = 'realty 1'

        self.assertListEqual(
            list(get_available_realty_search_results(test_query)),
            [Realty.objects.get(slug='realty-1')],
        )
