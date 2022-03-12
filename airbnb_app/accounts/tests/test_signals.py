from django.test import TestCase

from subscribers.models import Subscriber

from ..models import CustomUser


class AccountsSignalsTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

        Subscriber.objects.create(email='user2@gmail.com')
        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Bill',
            last_name='White',
            password='test',
        )

    def test_handle_user_sign_up_new_user_has_common_group(self):
        """All new users are in the `common` Group."""
        self.assertTrue(CustomUser.objects.first().groups.filter(name='common_users').exists())

    def test_handle_user_sign_up_profile_for_new_user_is_created(self):
        """Profile is created for all new users."""
        self.assertTrue(hasattr(CustomUser.objects.first(), 'profile'))
        self.assertEqual(CustomUser.objects.first().profile.user, CustomUser.objects.first())

    def test_handle_user_sign_up_update_user_field_in_subscriber_object(self):
        """If there is a Subscriber with `new user email` - Subscriber's `user` field will be updated."""
        self.assertEqual(Subscriber.objects.first().user, CustomUser.objects.get(email='user2@gmail.com'))

    def test_update_profile_new_subscriber_email(self):
        """If User changes an email and User was a Subscriber, Subscriber's email will be also changed."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        new_user_email = 'newuser2@gmail.com'
        test_user.email = new_user_email
        test_user.save()

        # There was a Subscriber with email 'user2@gmail.com', now Subscriber's email should be `new_user_email`
        self.assertEqual(Subscriber.objects.first().email, new_user_email)
