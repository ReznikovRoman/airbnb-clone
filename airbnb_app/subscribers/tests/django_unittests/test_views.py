from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from subscribers.models import Subscriber


class SubscribeViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

    def test_subscribe_success_if_not_logged_in(self):
        """`AnonymousUser` can subscribe to the newsletter."""
        form_data = {
            'email': 'sub1@gmail.com',
        }
        response = self.client.post(reverse('subscribers:new_subscription'), data=form_data)

        self.assertRedirects(response, reverse('home_page'))
        self.assertTrue(Subscriber.objects.filter(email=form_data['email']).exists())

    def test_subscribe_success_if_logged_in(self):
        """Authenticated user can subscribe to the newsletter."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        form_data = {
            'email': 'user1@gmail.com',
        }
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.post(reverse('subscribers:new_subscription'), data=form_data)

        self.assertRedirects(response, reverse('home_page'))
        self.assertTrue(Subscriber.objects.filter(email=form_data['email']).exists())
        self.assertEqual(Subscriber.objects.get(email=form_data['email']).user, test_user)

    def test_can_subscribe_multiple_times_if_not_logged_in(self):
        """`AnonymousUser` can subscribe multiple times (for different emails)."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        form_data1 = {
            'email': 'user1@gmail.com',
        }
        form_data2 = {
            'email': 'sub2@gmail.com',
        }
        self.client.login(email='user1@gmail.com', password='test')
        self.client.post(reverse('subscribers:new_subscription'), data=form_data1)
        self.client.post(reverse('subscribers:new_subscription'), data=form_data2)

        self.assertEqual(Subscriber.objects.count(), 2)
        self.assertTrue(Subscriber.objects.filter(email=form_data1['email']).exists())
        self.assertTrue(Subscriber.objects.filter(email=form_data2['email']).exists())

        self.assertEqual(Subscriber.objects.get(email=form_data1['email']).user, test_user)
        self.assertNotEqual(Subscriber.objects.get(email=form_data2['email']).user, test_user)

    def test_can_subscribe_multiple_times_if_logged_in(self):
        """Authenticated user can subscribe multiple times (for different emails)."""
        form_data1 = {
            'email': 'sub1@gmail.com',
        }
        form_data2 = {
            'email': 'sub2@gmail.com',
        }
        self.client.post(reverse('subscribers:new_subscription'), data=form_data1)
        self.client.post(reverse('subscribers:new_subscription'), data=form_data2)

        self.assertEqual(Subscriber.objects.count(), 2)
        self.assertTrue(Subscriber.objects.filter(email=form_data1['email']).exists())
        self.assertTrue(Subscriber.objects.filter(email=form_data2['email']).exists())
