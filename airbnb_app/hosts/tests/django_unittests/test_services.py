from django.test import TestCase

from accounts.models import CustomUser
from hosts.models import RealtyHost
from hosts.services import get_host_or_none_by_user


class HostsServicesTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user@gmail.com',
            first_name='Peter',
            last_name='Smith',
            password='test',
        )

        user1 = CustomUser.objects.create_user(
            email='host@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        RealtyHost.objects.create(user=user1)

    def test_get_host_or_none_by_user_existing_host(self):
        """get_host_or_none_by_user() returns RealtyHost if host with the given `user` exists."""
        host = get_host_or_none_by_user(user=CustomUser.objects.get(email='host@gmail.com'))
        self.assertEqual(host, RealtyHost.objects.first())

    def test_get_host_or_none_by_user_not_a_host(self):
        """get_host_or_none_by_user() returns None if there is no host for the `user`. (i.e. `user` is not a host)."""
        host = get_host_or_none_by_user(user=CustomUser.objects.get(email='user@gmail.com'))
        self.assertIsNone(host)
