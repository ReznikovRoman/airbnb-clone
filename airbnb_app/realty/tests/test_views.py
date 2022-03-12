import json
import shutil
import tempfile
from unittest import mock

import fakeredis

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import CustomUser
from addresses.forms import AddressForm
from addresses.models import Address
from common.collections import FormWithModel
from common.services import get_keys_with_prefixes, get_required_fields_from_form_with_model
from common.session_handler import SessionHandler
from common.testing_utils import create_valid_image
from hosts.models import RealtyHost

from .. import views
from ..constants import MAX_REALTY_IMAGES_COUNT, REALTY_FORM_KEYS_COLLECTOR_NAME, REALTY_FORM_SESSION_PREFIX
from ..forms import RealtyForm, RealtyGeneralInfoForm, RealtyImageFormSet, RealtyTypeForm
from ..models import Amenity, Realty, RealtyImage, RealtyTypeChoices


MEDIA_ROOT = tempfile.mkdtemp()


class RealtySearchResultsViewTests(TestCase):
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
            country='Russia',
            city='Moscow',
            street='Ulitsa Zorge, 4',
        )
        Realty.objects.create(
            name='Realty 2',
            description='Desc 2',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location2,
            host=test_host1,
        )

        test_location3 = Address.objects.create(
            country='Italy',
            city='Rome',
            street='Via Condotti, 2',
        )
        Realty.objects.create(
            name='Realty 3',
            description='Desc 3',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location3,
            host=test_host1,
        )
        test_location4 = Address.objects.create(
            country='Italy',
            city='Rome',
            street='Via del Corso, 4',
        )
        Realty.objects.create(
            name='Realty 4',
            description='Desc 4',
            is_available=True,
            realty_type=RealtyTypeChoices.HOTEL,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location4,
            host=test_host1,
        )

    def test_view_correct_attrs(self):
        """`RealtySearchResultsView` has correct attributes."""
        self.assertEqual(views.RealtySearchResultsView.model, Realty)
        self.assertEqual(views.RealtySearchResultsView.template_name, 'realty/realty/search_results.html')
        self.assertTrue(hasattr(views.RealtySearchResultsView, 'realty_type_form'))

    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        response = self.client.get(reverse('realty:search'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """`RealtySearchResultsView` uses a correct HTML template."""
        response = self.client.get(reverse('realty:search'))
        self.assertTemplateUsed(response, 'realty/realty/search_results.html')

    def test_correct_context_data_if_no_query_params(self):
        """`request.context` has correct data (if there are no query parameters in the URL)."""
        response = self.client.get(reverse('realty:search'))
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)

    def test_correct_context_data_if_query_params(self):
        """`request.context` has correct data (if there are some query parameters in the URL)."""
        realty_type_param = 'Apartments'
        query_param = 'Moscow'
        response = self.client.get(f"{reverse('realty:search')}?realty_type={realty_type_param}&q={query_param}")

        self.assertEqual(response.context['search_query'], query_param)
        self.assertEqual(response.context['realty_count'], 2)
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)
        self.assertEqual(response.context['meta_description'], f"Search results for `{query_param}`")

    def test_get_queryset_if_no_query_params(self):
        """If there are no query parameters in the URL, queryset includes all available realty objects."""
        response = self.client.get(reverse('realty:search'))
        self.assertQuerysetEqual(response.context['realty_list'], Realty.available.all(), transform=lambda x: x)

    def test_get_queryset_if_query_params(self):
        """If there are some query parameters in the URL, queryset includes only valid search results."""
        query_param = 'Moscow'
        response = self.client.get(f"{reverse('realty:search')}?q={query_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            [Realty.objects.get(slug='realty-1'), Realty.objects.get(slug='realty-2')],
            transform=lambda x: x,
        )

    def test_get_queryset_if_query_params_with_realty_type(self):
        """If there is `q` query parameter with other filters/query params qs includes only valid search results."""
        realty_type_param = 'Apartments'
        query_param = 'Rome'
        response = self.client.get(f"{reverse('realty:search')}?realty_type={realty_type_param}&q={query_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            [Realty.objects.get(slug='realty-3')],
            transform=lambda x: x,
        )


class RealtyListViewTests(TestCase):
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
            realty_type=RealtyTypeChoices.HOTEL,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location1,
            host=test_host1,
        )

        test_location2 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Ulitsa Zorge, 4',
        )
        Realty.objects.create(
            name='Realty 2',
            description='Desc 2',
            is_available=False,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location2,
            host=test_host1,
        )

        for realty_index in range(3, 7):
            test_location = Address.objects.create(
                country='Russia',
                city='Moscow',
                street=f'Nikolskaya, {realty_index}',
            )
            Realty.objects.create(
                name=f'Realty {realty_index}',
                description=f'Desc {realty_index}',
                is_available=True,
                realty_type=RealtyTypeChoices.APARTMENTS,
                beds_count=1,
                max_guests_count=2,
                price_per_night=40,
                location=test_location,
                host=test_host1,
            )

        test_location3 = Address.objects.create(
            country='Italy',
            city='Rome',
            street='Via Condotti, 2',
        )
        Realty.objects.create(
            name='Realty 3',
            description='Desc 3',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location3,
            host=test_host1,
        )

    def test_view_correct_attrs(self):
        """`RealtyListView` has correct attributes."""
        self.assertEqual(views.RealtyListView.model, Realty)
        self.assertEqual(views.RealtyListView.template_name, 'realty/realty/list.html')
        self.assertEqual(views.RealtyListView.paginate_by, 3)
        self.assertTrue(hasattr(views.RealtyListView, 'realty_type_form'))

    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        response = self.client.get(reverse('realty:all'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """`RealtyListView` uses a correct HTML template."""
        response = self.client.get(reverse('realty:all'))
        self.assertTemplateUsed(response, 'realty/realty/list.html')

    def test_correct_context_data(self):
        """`request.context` has correct data."""
        response = self.client.get(reverse('realty:all'))

        self.assertEqual(response.context['realty_count'], Realty.available.count())
        self.assertEqual(response.context['city'], "All cities")
        self.assertEqual(response.context['meta_description'], "List of places in All cities")
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)

    def test_pagination_is_three(self):
        """Results are paginated by 3 elements per page."""
        response = self.client.get(reverse('realty:all'))

        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['realty_list']), 3)

    def test_get_queryset_if_no_query_params(self):
        """If there are no query parameters in the URL, queryset includes all available realty objects."""
        response = self.client.get(reverse('realty:all'))

        self.assertQuerysetEqual(
            response.context['realty_list'],
            Realty.available.all()[:3],  # results are paginated by 3, so validate only last 3 realty objects
            transform=lambda x: x,
        )

    def test_get_queryset_if_query_params(self):
        """If there are some query parameters in the URL, queryset includes only filtered results."""
        realty_type_param = RealtyTypeChoices.HOTEL
        response = self.client.get(f"{reverse('realty:all')}?realty_type={realty_type_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            Realty.available.filter(realty_type=realty_type_param),
            transform=lambda x: x,
        )

    def test_view_url_accessible_by_name_with_city_arg(self):
        """Url (with additional args) is accessible by its name."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_with_city_arg(self):
        """`RealtyListView` (with additional args) uses a correct HTML template."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))
        self.assertTemplateUsed(response, 'realty/realty/list.html')

    def test_correct_context_data_with_city_arg(self):
        """`request.context` (from view with additional args) has correct data."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))

        self.assertEqual(
            response.context['realty_count'],
            Realty.available.filter(location__city__iexact='moscow').count(),
        )
        self.assertEqual(response.context['city'], "Moscow")
        self.assertEqual(response.context['meta_description'], "List of places in Moscow")
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)

    def test_pagination_is_three_with_city_arg(self):
        """Results (from view with additional args) are paginated by 3 elements per page."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))

        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['realty_list']), 3)

    def test_get_queryset_if_no_query_params_with_city_arg(self):
        """If there are no query parameters in the URL,
        queryset includes all available realty objects from the given `city` arg.
        """
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))

        self.assertQuerysetEqual(
            response.context['realty_list'],
            # results are paginated by 3, so validate only last 3 realty objects
            Realty.available.filter(location__city__iexact='moscow')[:3],
            transform=lambda x: x,
        )

    def test_get_queryset_if_query_params_with_city_arg(self):
        """If there are some query parameters in the URL,
        queryset includes only filtered results (from the given `city` arg).
        """
        realty_type_param = RealtyTypeChoices.APARTMENTS
        response = self.client.get(
            f"{reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'})}?realty_type={realty_type_param}",
        )

        self.assertQuerysetEqual(
            response.context['realty_list'],
            Realty.available.filter(realty_type=realty_type_param, location__city__iexact='moscow')[:3],
            transform=lambda x: x,
        )


class RealtyDetailViewTests(TestCase):
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
            realty_type=RealtyTypeChoices.HOTEL,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location1,
            host=test_host1,
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.RealtyDetailView.model, Realty)
        self.assertEqual(views.RealtyDetailView.template_name, 'realty/realty/detail.html')
        self.assertQuerysetEqual(
            views.RealtyDetailView.queryset,
            Realty.available.all(),
            transform=lambda x: x,
        )

    @mock.patch('realty.services.realty.redis_instance',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        response = self.client.get(reverse('realty:detail', kwargs={'pk': test_realty.pk, 'slug': test_realty.slug}))

        self.assertEqual(response.status_code, 200)

    @mock.patch(
        'realty.services.realty.redis_instance',
        fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True),
    )
    def test_view_uses_correct_template(self):
        """`RealtyDetailView` uses a correct HTML template."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        response = self.client.get(reverse('realty:detail', kwargs={'pk': test_realty.pk, 'slug': test_realty.slug}))

        self.assertTemplateUsed(response, 'realty/realty/detail.html')

    @mock.patch(
        'realty.services.realty.redis_instance',
        fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True),
    )
    def test_correct_context_data(self):
        """`request.context` has correct data (views count)."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')

        # visit page 3 times
        self.client.get(reverse('realty:detail', kwargs={'pk': test_realty.pk, 'slug': test_realty.slug}))
        self.client.get(reverse('realty:detail', kwargs={'pk': test_realty.pk, 'slug': test_realty.slug}))
        response = self.client.get(reverse('realty:detail', kwargs={'pk': test_realty.pk, 'slug': test_realty.slug}))

        self.assertEqual(int(response.context['realty_views_count']), 3)

        # visit page 1 more time
        response = self.client.get(reverse('realty:detail', kwargs={'pk': test_realty.pk, 'slug': test_realty.slug}))

        # views count should change
        self.assertEqual(int(response.context['realty_views_count']), 4)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RealtyEditViewTests(TestCase):
    def setUp(self) -> None:
        Amenity.objects.create(name='wifi')
        Amenity.objects.create(name='kitchen')
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
            realty_type=RealtyTypeChoices.HOTEL,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location1,
            host=test_host1,
        )
        test_image_name1 = 'image1.png'
        test_image1 = create_valid_image(test_image_name1)

        RealtyImage.objects.create(
            image=test_image1,
            realty=test_realty1,
        )

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Peter',
            last_name='Collins',
            password='test',
        )

        test_user3 = CustomUser.objects.create_user(
            email='user3@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )
        test_host2 = RealtyHost.objects.create(user=test_user3)
        test_location2 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Ulitsa Zorge, 12',
        )
        Realty.objects.create(
            name='Realty 2',
            description='Desc 2',
            is_available=True,
            realty_type=RealtyTypeChoices.APARTMENTS,
            beds_count=1,
            max_guests_count=2,
            price_per_night=40,
            location=test_location2,
            host=test_host2,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete temp media dir
        super().tearDownClass()

    def test_view_correct_attrs(self):
        """`RealtyEditView` has correct attributes."""
        self.assertEqual(views.RealtyEditView.template_name, 'realty/realty/form.html')

        self.assertTrue(hasattr(views.RealtyEditView, 'realty'))
        self.assertTrue(hasattr(views.RealtyEditView, 'address'))
        self.assertTrue(hasattr(views.RealtyEditView, 'realty_images'))

        self.assertTrue(hasattr(views.RealtyEditView, 'is_creating_new_realty'))
        self.assertTrue(views.RealtyEditView.is_creating_new_realty)
        self.assertTrue(hasattr(views.RealtyEditView, 'realty_form'))
        self.assertTrue(hasattr(views.RealtyEditView, 'address_form'))
        self.assertTrue(hasattr(views.RealtyEditView, 'realty_address_initial'))
        self.assertTrue(hasattr(views.RealtyEditView, 'realty_info_initial'))

        self.assertTrue(hasattr(views.RealtyEditView, 'session_handler'))

    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        test_realty_id = Realty.objects.get(slug='realty-1').id

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty_id}))

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """`RealtyEditView` uses a correct HTML template."""
        test_realty_id = Realty.objects.get(slug='realty-1').id

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty_id}))

        self.assertTemplateUsed(response, 'realty/realty/form.html')

    def test_redirect_if_user_not_a_host(self):
        """Existing Realty object can be edited only by the RealtyHost, otherwise view redirects user."""
        test_realty_id = Realty.objects.get(slug='realty-1').id

        self.client.login(email='user2@gmail.com', password='test')  # login as a default user (not a host)
        response = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty_id}))

        # redirects, because user is not a host
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:all'))

    def test_redirect_if_user_not_an_owner(self):
        """Existing Realty object can be edited only by the owner, otherwise view redirects user."""
        test_realty_id = Realty.objects.get(slug='realty-1').id

        self.client.login(email='user2@gmail.com', password='test')  # login as a host, but not the owner of Realty-1
        response = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty_id}))

        # redirects, because Host is not an owner of realty-1
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:all'))

    def test_correct_context_data_if_existing_realty(self):
        """`request.context` is correct if we're editing an existing Realty object (`realty_id` in URL args)."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty.id}))

        realty_form: RealtyForm = response.context['realty_form']
        address_form: AddressForm = response.context['address_form']
        realty_image_formset: RealtyImageFormSet = response.context['realty_image_formset']

        self.assertEqual(realty_form.instance, test_realty)
        self.assertEqual(address_form.instance, test_realty.location)
        self.assertQuerysetEqual(
            realty_image_formset.queryset,
            test_realty.images.all(),
            transform=lambda x: x,
        )
        self.assertFalse(response.context['is_creating_new_realty'])
        self.assertQuerysetEqual(
            response.context['realty_images'],
            test_realty.images.all(),
            transform=lambda x: x,
        )
        self.assertEqual(response.context['max_realty_images_count'], MAX_REALTY_IMAGES_COUNT)

    def test_update_existing_realty_success(self):
        """Host can update an existing Realty object."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        test_image = test_realty.images.first()

        new_description = 'New Desc 1'
        new_amenities = Amenity.objects.values_list('id', flat=True)
        new_image = create_valid_image('new_image1.png')

        self.client.login(email='user1@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty.id}))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']

        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'form-0-image': test_image,
            'form-0-id': test_image.id,
            # new fields
            'form-1-image': new_image,
            'description': new_description,
            'amenities': new_amenities,
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        response = self.client.post(reverse('realty:edit_realty', kwargs={'realty_id': test_realty.id}), data=form_data)

        test_realty.refresh_from_db()

        self.assertRedirects(response, reverse('realty:all'))
        self.assertEqual(test_realty.description, new_description)
        self.assertListEqual(list(test_realty.amenities.values_list('id', flat=True)), list(new_amenities))
        self.assertEqual(test_realty.images.count(), 2)
        self.assertIn(test_image, test_realty.images.all())

    def test_view_renders_errors_on_failure_existing_realty(self):
        """If there are some errors in the forms, those errors will be successfully rendered."""
        test_realty: Realty = Realty.objects.get(slug='realty-1')
        test_image = test_realty.images.first()

        new_beds_count = 100  # invalid value: beds count must be < 9

        self.client.login(email='user1@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:edit_realty', kwargs={'realty_id': test_realty.id}))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']

        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'form-0-image': test_image,
            'form-0-id': test_image.id,
            # new fields
            'beds_count': new_beds_count,
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        response = self.client.post(reverse('realty:edit_realty', kwargs={'realty_id': test_realty.id}), data=form_data)

        test_realty.refresh_from_db()

        self.assertTemplateUsed(response, 'realty/realty/form.html')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['realty_form'].is_valid())

    def test_redirect_if_no_required_session_data(self):
        """User is redirected if there is no required data in the session (when creating a new Realty)."""
        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty'))

        self.assertRedirects(response, reverse('realty:new_realty_info'))

    def test_redirect_if_only_some_required_session_data(self):
        """Uer is redirected if there is not all required data in the session."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add some data to the session
        session_handler.add_new_item('name', 'test name')
        session_handler.add_new_item('city', 'test city')
        session_handler.get_session().save()

        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty'))

        # redirect, because there is no all required data in the session
        self.assertRedirects(response, reverse('realty:new_realty_info'))

    def test_correct_response_if_required_session_data_exists(self):
        """User can access page if there is all required session data."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', '2')
        session_handler.add_new_item('max_guests_count', '4')
        session_handler.add_new_item('price_per_night', '100')
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        session_handler.add_new_item('amenities', ['wifi'])

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty'))

        realty_form = response.context['realty_form']
        address_form = response.context['address_form']

        self.assertEqual(response.status_code, 200)

        # form initial from session
        self.assertEqual(realty_form.initial['name'], 'New realty')
        self.assertEqual(address_form.initial['city'], 'Moscow')
        self.assertEqual(realty_form.initial['description'], 'New desc')
        self.assertQuerysetEqual(
            realty_form.initial['amenities'],
            Amenity.objects.filter(name='wifi').values_list('id', flat=True),
            transform=lambda x: x,
        )

    def test_correct_context_data_if_creating_new_realty(self):
        """`request.context` is correct if we're creating a new Realty object."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', '2')
        session_handler.add_new_item('max_guests_count', '4')
        session_handler.add_new_item('price_per_night', '100')
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        session_handler.add_new_item('amenities', ['wifi'])

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty'))

        self.assertTrue(response.context['is_creating_new_realty'])
        self.assertEqual(response.context['realty_image_formset'].queryset.count(), 0)
        self.assertIsNone(response.context['realty_images'])
        self.assertEqual(response.context['max_realty_images_count'], MAX_REALTY_IMAGES_COUNT)

    def test_view_renders_errors_on_creation_failure(self):
        """If there are some errors in the forms (while creating new realty), they are rendered correctly."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 100)  # invalid value: beds count must be < 9
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        self.client.login(email='user2@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:new_realty'))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']
        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'amenities': [],
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        # try to create a new realty with data from the form's initial
        response_post = self.client.post(reverse('realty:new_realty'), data=form_data)

        self.assertEqual(response_post.status_code, 200)
        self.assertFalse(response_post.context['realty_form'].is_valid())

    def test_can_create_new_realty_success(self):
        """User can successfully create new realty."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 2)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        session_handler.add_new_item('amenities', ['wifi'])

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        self.client.login(email='user2@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:new_realty'))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']
        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        # create new realty using initial form values
        response_post = self.client.post(reverse('realty:new_realty'), data=form_data)

        test_new_realty = Realty.objects.get(slug='new-realty')

        self.assertRedirects(response_post, reverse('realty:all'))

        # test that new realty has been successfully created
        self.assertEqual(test_new_realty.name, 'New realty')
        self.assertEqual(test_new_realty.location.city, 'Moscow')
        self.assertEqual(test_new_realty.amenities.first().name, 'wifi')

    def test_creating_new_host_on_realty_creation(self):
        """New RealtyHost is created on realty creation (if current user is not already a host)."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 4)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        test_user = CustomUser.objects.get(email='user2@gmail.com')
        self.client.login(email='user2@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:new_realty'))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']
        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'amenities': [],
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        # create a new realty with data from the form's initial
        response_post = self.client.post(reverse('realty:new_realty'), data=form_data)

        new_host_qs = RealtyHost.objects.filter(user=test_user)

        self.assertRedirects(response_post, reverse('realty:all'))
        self.assertTrue(new_host_qs.exists())
        self.assertEqual(new_host_qs.first().realty.count(), 1)

    def test_creating_no_new_host_on_realty_creation_if_user_is_a_host(self):
        """New RealtyHost is not created on realty creation if current user is already a host."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 4)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        # user3@gmail.com - is a RealtyHost
        test_user = CustomUser.objects.get(email='user3@gmail.com')
        self.client.login(email='user3@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:new_realty'))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']
        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'amenities': [],
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        current_hosts_count = RealtyHost.objects.count()

        # create a new realty with data from the form's initial
        response_post = self.client.post(reverse('realty:new_realty'), data=form_data)

        new_host_qs = RealtyHost.objects.filter(user=test_user)

        self.assertRedirects(response_post, reverse('realty:all'))
        self.assertTrue(new_host_qs.exists())
        self.assertEqual(new_host_qs.first().realty.count(), 2)
        self.assertEqual(current_hosts_count, RealtyHost.objects.count())

    def test_flushes_session_after_realty_creation(self):
        """Session is flushed after successful realty creation."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 4)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        CustomUser.objects.get(email='user2@gmail.com')
        self.client.login(email='user2@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:new_realty'))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']
        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'amenities': [],
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        # create a new realty with data from the form's initial
        self.client.post(reverse('realty:new_realty'), data=form_data)

        self.assertNotIn('name', self.client.session)
        self.assertNotIn('city', self.client.session)
        self.assertNotIn('description', self.client.session)

    def test_session_data_remains_on_failure(self):
        """If there is an error while creating new Realty, session data is not removed."""
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 100)  # invalid value: beds count must be < 9
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Test street')
        session_handler.add_new_item('description', 'New desc')

        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        CustomUser.objects.get(email='user2@gmail.com')
        self.client.login(email='user2@gmail.com', password='test')
        response_get = self.client.get(reverse('realty:new_realty'))

        realty_form = response_get.context['realty_form']
        address_form = response_get.context['address_form']
        form_data = {
            'form-TOTAL_FORMS': '6',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '0',
            'form-MIN_NUM_FORMS': '6',
            'amenities': [],
        }
        form_data = dict(realty_form.initial, **address_form.initial, **form_data)

        # create a new realty with data from the form's initial
        self.client.post(reverse('realty:new_realty'), data=form_data)

        self.assertIn(f'{REALTY_FORM_SESSION_PREFIX}_name', self.client.session)
        self.assertIn(f'{REALTY_FORM_SESSION_PREFIX}_city', self.client.session)
        self.assertIn(f'{REALTY_FORM_SESSION_PREFIX}_description', self.client.session)


class RealtyGeneralInfoEditViewTests(TestCase):
    def setUp(self) -> None:
        Amenity.objects.create(name='Kitchen')
        Amenity.objects.create(name='Breakfast')
        Amenity.objects.create(name='Wi-Fi')

        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

        test_user2 = CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )
        RealtyHost.objects.create(user=test_user2)

    def test_view_correct_attrs(self):
        """`RealtyGeneralInfoEditView` has correct attributes."""
        self.assertEqual(
            views.RealtyGeneralInfoEditView.template_name,
            'realty/realty/creation_steps/step_1_general_info.html',
        )
        self.assertTrue(hasattr(views.RealtyGeneralInfoEditView, 'realty_form'))
        self.assertTrue(hasattr(views.RealtyGeneralInfoEditView, 'session_handler'))

    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty_info'))

        self.assertEqual(response.status_code, 200)

    def test_correct_context_data_if_logged_in(self):
        """`request.context` is correct if user is logged in."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty_info'))

        self.assertIsInstance(response.context['realty_form'], RealtyGeneralInfoForm)

    def test_correct_initial_if_session_data(self):
        """Form has correct initial if there is some session data."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )
        amenity1 = Amenity.objects.get(name='Kitchen')

        # add data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('amenities', ['Kitchen'])
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_info'))
        expected_initial = {
            'amenities': Amenity.objects.filter(id__in=[amenity1.id]).values_list('id', flat=True),
            'beds_count': None,
            'max_guests_count': None,
            'name': 'New realty',
            'price_per_night': None,
            'realty_type': None,
        }

        self.assertIsNone(response.context['realty_form'].initial['beds_count'])
        self.assertEqual(response.context['realty_form'].initial['name'], expected_initial['name'])
        self.assertQuerysetEqual(
            response.context['realty_form'].initial['amenities'],
            expected_initial['amenities'],
            transform=lambda x: x,
        )

    def test_no_initial_in_form_if_no_session_data(self):
        """There is no initial data in the form if `session` is empty."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('realty:new_realty_info'))

        expected_initial = {
            'amenities': None,
            'beds_count': None,
            'max_guests_count': None,
            'name': None,
            'price_per_night': None,
            'realty_type': None,
        }

        self.assertDictEqual(response.context['realty_form'].initial, expected_initial)

    def test_update_session_data_on_post(self):
        """POST request updates session data correctly."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )
        session_handler.get_session().save()
        amenity1 = Amenity.objects.get(name='Kitchen')
        amenity2 = Amenity.objects.get(name='Wi-Fi')

        post_data = {
            'amenities': [
                amenity1.id,
                amenity2.id,
            ],
            'beds_count': 2,
            'max_guests_count': 4,
            'name': 'New realty',
            'price_per_night': 100,
            'realty_type': RealtyTypeChoices.APARTMENTS.value,
        }
        self.client.post(reverse('realty:new_realty_info'), post_data)

        self.assertEqual(self.client.session[f'{prefix}_name'], 'New realty')
        self.assertListEqual(self.client.session[f'{prefix}_amenities'], [amenity1.name, amenity2.name])

    def test_redirect_on_valid_post(self):
        """User is redirected if POST data is correct."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        amenity1 = Amenity.objects.get(name='Kitchen')
        amenity2 = Amenity.objects.get(name='Wi-Fi')

        post_data = {
            'amenities': [
                amenity1.id,
                amenity2.id,
            ],
            'beds_count': 2,
            'max_guests_count': 4,
            'name': 'New realty',
            'price_per_night': 100,
            'realty_type': RealtyTypeChoices.APARTMENTS.value,
        }
        response = self.client.post(reverse('realty:new_realty_info'), post_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:new_realty_location'))

    def test_view_renders_errors_on_failure(self):
        """Form errors are rendered correctly if there was an error in POST data."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        amenity1 = Amenity.objects.get(name='Kitchen')
        amenity2 = Amenity.objects.get(name='Wi-Fi')

        post_data = {
            'amenities': [
                amenity1.id,
                amenity2.id,
            ],
            'beds_count': 2,
            'max_guests_count': 4,
            'name': 'New realty',
            'price_per_night': 100,
            'realty_type': 'INVALID',
        }
        response = self.client.post(reverse('realty:new_realty_info'), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('realty_type', response.context['realty_form'].errors.as_data())


class RealtyGeneralLocationEditViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

        test_user2 = CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )
        RealtyHost.objects.create(user=test_user2)

    def test_view_correct_attrs(self):
        """`RealtyLocationEditView` has correct attributes."""
        self.assertEqual(
            views.RealtyLocationEditView.template_name,
            'realty/realty/creation_steps/step_2_location.html',
        )
        self.assertListEqual(
            views.RealtyLocationEditView.required_session_data,
            get_keys_with_prefixes(
                names=get_required_fields_from_form_with_model(
                    forms_with_models=[
                        FormWithModel(RealtyGeneralInfoForm, Realty),
                    ],
                ),
                prefix=REALTY_FORM_SESSION_PREFIX,
            ),
        )
        self.assertTrue(hasattr(views.RealtyLocationEditView, 'location_form'))
        self.assertTrue(hasattr(views.RealtyLocationEditView, 'session_handler'))

    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_location'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_no_session_data(self):
        """If there is no all required data in the session user is redirected."""
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_location'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:new_realty_info'))

    def test_correct_initial_if_session_data(self):
        """Form has correct initial if there is some session data."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_location'))
        expected_initial = {
            'country': 'Russia',
            'city': None,
            'street': None,
        }

        self.assertIsNone(response.context['location_form'].initial['city'])
        self.assertEqual(response.context['location_form'].initial['country'], expected_initial['country'])

    def test_no_initial_in_form_if_no_session_data(self):
        """There is no initial data in the form if `session` is empty."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_location'))

        expected_initial = {
            'country': None,
            'city': None,
            'street': None,
        }

        self.assertDictEqual(response.context['location_form'].initial, expected_initial)

    def test_update_session_data_on_post(self):
        """POST request updates session data correctly."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        post_data = {
            'country': 'Russia',
            'city': 'Moscow',
            'street': 'Arbat, 20',
        }
        self.client.post(reverse('realty:new_realty_location'), post_data)

        self.assertEqual(self.client.session[f'{prefix}_country'], post_data['country'])
        self.assertEqual(self.client.session[f'{prefix}_city'], post_data['city'])
        self.assertEqual(self.client.session[f'{prefix}_street'], post_data['street'])

    def test_redirect_on_valid_post(self):
        """User is redirected if POST data is correct."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        post_data = {
            'country': 'Russia',
            'city': 'Moscow',
            'street': 'Arbat, 20',
        }
        response = self.client.post(reverse('realty:new_realty_location'), post_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:new_realty_description'))

    def test_view_renders_errors_on_failure(self):
        """Form errors are rendered correctly if there was an error in POST data."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        post_data = {
            'country': 'Russia',
        }
        response = self.client.post(reverse('realty:new_realty_location'), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('city', response.context['location_form'].errors.as_data())
        self.assertIn('street', response.context['location_form'].errors.as_data())


class RealtyGeneralDescriptionEditViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

        test_user2 = CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )
        RealtyHost.objects.create(user=test_user2)

    def test_view_correct_attrs(self):
        """`RealtyDescriptionEditView` has correct attributes."""
        self.assertEqual(
            views.RealtyDescriptionEditView.template_name,
            'realty/realty/creation_steps/step_3_description.html',
        )
        self.assertListEqual(
            views.RealtyDescriptionEditView.required_session_data,
            get_keys_with_prefixes(
                names=get_required_fields_from_form_with_model(
                    forms_with_models=[
                        FormWithModel(RealtyGeneralInfoForm, Realty),
                        FormWithModel(AddressForm, Address),
                    ],
                ),
                prefix=REALTY_FORM_SESSION_PREFIX,
            ),
        )
        self.assertTrue(hasattr(views.RealtyDescriptionEditView, 'description_form'))
        self.assertTrue(hasattr(views.RealtyDescriptionEditView, 'session_handler'))

    def test_view_url_accessible_by_name(self):
        """Url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Arbat, 20')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_description'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_no_session_data(self):
        """If there is no all required data in the session user is redirected."""
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_description'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:new_realty_info'))

    def test_correct_initial_if_session_data(self):
        """Form has correct initial if there is some session data."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Arbat, 20')
        session_handler.add_new_item('description', 'Desc')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_description'))
        expected_initial = {
            'description': 'Desc',
        }

        self.assertEqual(response.context['description_form'].initial['description'], expected_initial['description'])

    def test_no_initial_in_form_if_no_session_data(self):
        """There is no initial data in the form if `session` is empty."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Arbat, 20')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        response = self.client.get(reverse('realty:new_realty_description'))

        expected_initial = {
            'description': None,
        }

        self.assertDictEqual(response.context['description_form'].initial, expected_initial)

    def test_update_session_data_on_post(self):
        """POST request updates session data correctly."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Arbat, 20')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        post_data = {
            'description': 'Desc',
        }
        self.client.post(reverse('realty:new_realty_description'), post_data)

        self.assertEqual(self.client.session[f'{prefix}_description'], post_data['description'])

    def test_redirect_on_valid_post(self):
        """User is redirected if POST data is correct."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        test_session = self.client.session
        keys_collector_name = REALTY_FORM_KEYS_COLLECTOR_NAME
        prefix = REALTY_FORM_SESSION_PREFIX
        session_handler = SessionHandler(
            session=test_session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        # add all required data to the session
        session_handler.add_new_item('name', 'New realty')
        session_handler.add_new_item('type', 'Apartments')
        session_handler.add_new_item('beds_count', 23)
        session_handler.add_new_item('max_guests_count', 4)
        session_handler.add_new_item('price_per_night', 100)
        session_handler.add_new_item('country', 'Russia')
        session_handler.add_new_item('city', 'Moscow')
        session_handler.add_new_item('street', 'Arbat, 20')
        # have to save session manually to be able to use it in other modules (only while testing)
        session_handler.get_session().save()

        post_data = {
            'description': 'Desc',
        }
        response = self.client.post(reverse('realty:new_realty_description'), post_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('realty:new_realty'))


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RealtyImageOrderViewTests(TestCase):
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
        self.test_realty1 = Realty.objects.create(
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

        test_image_name1 = 'image1.png'
        test_image1 = create_valid_image(test_image_name1)

        self.image1 = RealtyImage.objects.create(
            image=test_image1,
            realty=self.test_realty1,
        )

        test_image_name2 = 'image2.png'
        test_image2 = create_valid_image(test_image_name2)

        self.image2 = RealtyImage.objects.create(
            image=test_image2,
            realty=self.test_realty1,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete temp media dir
        super().tearDownClass()

    def test_update_image_order(self):
        """User can update images' order."""
        CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        post_data = {
            self.image1.id: 1,
            self.image2.id: 0,
        }

        # initial order
        self.assertEqual(self.image1.order, 0)
        self.assertEqual(self.image2.order, 1)
        self.client.post(
            path=reverse('realty:image_change_order'),
            data=json.dumps(post_data),
            content_type='application/json',
        )

        self.image1.refresh_from_db()
        self.image2.refresh_from_db()
        # new order
        self.assertEqual(self.image1.order, 1)
        self.assertEqual(self.image2.order, 0)
