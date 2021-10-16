from model_bakery import baker

from django.test import TestCase
from django.urls import reverse

from hosts.models import RealtyHost
from realty.models import Realty, CustomDeleteQueryset
from accounts.models import CustomUser


class RealtyAdminActionsTests(TestCase):
    test_url: str = reverse('admin:realty_realty_changelist')

    def setUp(self) -> None:
        test_user = CustomUser.objects.create_superuser(
            email='test_action@gmail.com',
            first_name='Test',
            last_name='Action',
            password='test',
        )

        test_host = RealtyHost.objects.create(user=test_user)
        test_host.save()

        baker.make(
            'Realty',
            _quantity=2,
            host=test_host,
            is_available=True,
        )
        baker.make(
            'Realty',
            _quantity=2,
            host=test_host,
            is_available=False,
        )

    def test_make_realty_available_with_unavailable_realty(self):
        """If all selected Realty objects are unavailable, after `make_realty_available` action they become `available`.
        """
        self.client.login(username='test_action@gmail.com', password='test')
        data = {'action': 'make_realty_available',
                '_selected_action': [realty_obj.pk for realty_obj in Realty.objects.filter(is_available=False)]}
        response = self.client.post(self.test_url, data, follow=True)

        self.assertFalse(Realty.objects.filter(is_available=False).exists())

    def test_make_realty_available_with_available_realty(self):
        """
        If all selected Realty objects are available, after `make_realty_available` action they are still `available`.
        """
        self.client.login(username='test_action@gmail.com', password='test')
        available_realty_qs: CustomDeleteQueryset[Realty] = Realty.objects.filter(is_available=True)
        data = {'action': 'make_realty_available',
                '_selected_action': [realty_obj.pk for realty_obj in available_realty_qs]}
        response = self.client.post(self.test_url, data, follow=True)

        self.assertFalse(available_realty_qs.filter(is_available=False).exists())

    def test_make_realty_available_with_mixed_realty(self):
        """
        If some selected Realty objects are available and some of them are not,
        after `make_realty_available` action they all become `available`.
        """
        self.client.login(username='test_action@gmail.com', password='test')
        realty_qs: CustomDeleteQueryset[Realty] = Realty.objects.filter(is_available=False)[1:] | \
                                                  Realty.objects.filter(is_available=True)[1:]
        data = {'action': 'make_realty_available',
                '_selected_action': [realty_obj.pk for realty_obj in realty_qs]}
        response = self.client.post(self.test_url, data, follow=True)

        self.assertFalse(realty_qs.filter(is_available=False).exists())

    def test_make_realty_unavailable_with_available_realty(self):
        """
        If all selected Realty objects are available, after `make_realty_unavailable` action they become `unavailable`.
        """
        self.client.login(username='test_action@gmail.com', password='test')
        data = {'action': 'make_realty_unavailable',
                '_selected_action': [realty_obj.pk for realty_obj in Realty.objects.filter(is_available=True)]}
        response = self.client.post(self.test_url, data, follow=True)

        self.assertFalse(Realty.objects.filter(is_available=True).exists())

    def test_make_realty_unavailable_with_unavailable_realty(self):
        """
        If all selected Realty objects are unavailable,
        after `make_realty_unavailable` action they are still `unavailable`.
        """
        self.client.login(username='test_action@gmail.com', password='test')
        unavailable_realty_qs: CustomDeleteQueryset[Realty] = Realty.objects.filter(is_available=False)
        data = {'action': 'make_realty_unavailable',
                '_selected_action': [realty_obj.pk for realty_obj in unavailable_realty_qs]}
        response = self.client.post(self.test_url, data, follow=True)

        self.assertFalse(unavailable_realty_qs.filter(is_available=True).exists())

    def test_make_realty_unavailable_with_mixed_realty(self):
        """
        If some selected Realty objects are available and some of them are not,
        after `make_realty_unavailable` action they all become `unavailable`.
        """
        self.client.login(username='test_action@gmail.com', password='test')
        realty_qs: CustomDeleteQueryset[Realty] = Realty.objects.filter(is_available=False)[1:] | \
                                                  Realty.objects.filter(is_available=True)[1:]
        data = {'action': 'make_realty_unavailable',
                '_selected_action': [realty_obj.pk for realty_obj in realty_qs]}
        response = self.client.post(self.test_url, data, follow=True)

        self.assertFalse(realty_qs.filter(is_available=True).exists())
