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
        queryset includes only valid search results.
        """
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
        """Test that view has correct attributes."""
        self.assertEqual(views.RealtyListView.model, Realty)
        self.assertEqual(views.RealtyListView.template_name, 'realty/realty/list.html')
        self.assertEqual(views.RealtyListView.paginate_by, 3)
        self.assertTrue(hasattr(views.RealtyListView, 'realty_type_form'))

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        response = self.client.get(reverse('realty:all'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        response = self.client.get(reverse('realty:all'))
        self.assertTemplateUsed(response, 'realty/realty/list.html')

    def test_context_correct_data(self):
        """Test that request.context has correct data."""
        response = self.client.get(reverse('realty:all'))

        self.assertEqual(response.context['realty_count'], Realty.available.count())
        self.assertEqual(response.context['city'], "All cities")
        self.assertEqual(response.context['meta_description'], "List of places in All cities")
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)

    def test_pagination_is_three(self):
        """Test that results are paginated by 3 elements per page."""
        response = self.client.get(reverse('realty:all'))

        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['realty_list']), 3)

    def test_get_queryset_if_no_query_params(self):
        """Test that if there are no query parameters in the URL, queryset includes all available realty objects."""
        response = self.client.get(reverse('realty:all'))

        self.assertQuerysetEqual(
            response.context['realty_list'],
            Realty.available.all()[:3],  # results are paginated by 3, so validate only last 3 realty objects
            transform=lambda x: x,
        )

    def test_get_queryset_if_query_params(self):
        """Test that if there are some query parameters in the URL, queryset includes only filtered results."""
        realty_type_param = RealtyTypeChoices.HOTEL
        response = self.client.get(f"{reverse('realty:all')}?realty_type={realty_type_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            Realty.available.filter(realty_type=realty_type_param),
            transform=lambda x: x,
        )

    def test_view_url_accessible_by_name_with_city_arg(self):
        """Test that url (with additional args) is accessible by its name."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_with_city_arg(self):
        """TEst that view (with additional args) uses a correct HTML template."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))
        self.assertTemplateUsed(response, 'realty/realty/list.html')

    def test_context_correct_data_with_city_arg(self):
        """Test that request.context (from view with additional args) has correct data."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))

        self.assertEqual(
            response.context['realty_count'],
            Realty.available.filter(location__city__iexact='moscow').count(),
        )
        self.assertEqual(response.context['city'], "Moscow")
        self.assertEqual(response.context['meta_description'], "List of places in Moscow")
        self.assertIsInstance(response.context['realty_type_form'], RealtyTypeForm)

    def test_pagination_is_three_with_city_arg(self):
        """Test that results (from view with additional args) are paginated by 3 elements per page."""
        response = self.client.get(reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'}))

        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['realty_list']), 3)

    def test_get_queryset_if_no_query_params_with_city_arg(self):
        """Test that if there are no query parameters in the URL,
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
        """Test that if there are some query parameters in the URL,
        queryset includes only filtered results (from the given `city` arg).
        """
        realty_type_param = RealtyTypeChoices.APARTMENTS
        response = self.client.get(f"{reverse('realty:all_by_city', kwargs={'city_slug': 'moscow'})}"
                                   f"?realty_type={realty_type_param}")

        self.assertQuerysetEqual(
            response.context['realty_list'],
            Realty.available.filter(realty_type=realty_type_param, location__city__iexact='moscow')[:3],
            transform=lambda x: x,
        )
