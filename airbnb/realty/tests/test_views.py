from django.test import TestCase
from django.urls import reverse

from hosts.models import RealtyHost
from accounts.models import CustomUser
from addresses.models import Address
from .. import views
from ..forms import (RealtyTypeForm)
from ..models import (Realty, RealtyTypeChoices)


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
        """Test that view has correct attributes."""
        self.assertEqual(views.RealtySearchResultsView.model, Realty)
        self.assertEqual(views.RealtySearchResultsView.template_name, 'realty/realty/search_results.html')
        self.assertTrue(hasattr(views.RealtySearchResultsView, 'realty_type_form'))

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        response = self.client.get(reverse('realty:search'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """TEst that view uses a correct HTML template."""
        response = self.client.get(reverse('realty:search'))
        self.assertTemplateUsed(response, 'realty/realty/search_results.html')

    def test_context_correct_data_if_no_query_params(self):
        """Test that request.context has correct data (if there are no query parameters in the URL)."""
        response = self.client.get(reverse('realty:search'))
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)

    def test_context_correct_data_if_query_params(self):
        """Test that request.context has correct data (if there are some query parameters in the URL)."""
        realty_type_param = 'Apartments'
        query_param = 'Moscow'
        response = self.client.get(f"{reverse('realty:search')}?realty_type={realty_type_param}&q={query_param}")

        self.assertEqual(response.context['search_query'], query_param)
        self.assertEqual(response.context['realty_count'], 2)
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)
        self.assertEqual(response.context['meta_description'], f"Search results for `{query_param}`")

    def test_get_queryset_if_no_query_params(self):
        """Test that if there are no query parameters in the URL, queryset includes all available realty objects."""
        response = self.client.get(reverse('realty:search'))
        self.assertQuerysetEqual(response.context['realty_list'], Realty.available.all(), transform=lambda x: x)

    def test_get_queryset_if_query_params(self):
        """Test that if there are some query parameters in the URL, queryset includes only valid search results."""
        query_param = 'Moscow'
        response = self.client.get(f"{reverse('realty:search')}?q={query_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            [Realty.objects.get(slug='realty-1'), Realty.objects.get(slug='realty-2')],
            transform=lambda x: x,
        )

    def test_get_queryset_if_query_params_with_realty_type(self):
        """Test that if there is not only `q` query parameter, but also other filters/query parameters in the URL,
        queryset includes only valid search results."""
        realty_type_param = 'Apartments'
        query_param = 'Rome'
        response = self.client.get(f"{reverse('realty:search')}?realty_type={realty_type_param}&q={query_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            [Realty.objects.get(slug='realty-3')],
            transform=lambda x: x,
        )
