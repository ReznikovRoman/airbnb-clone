from django.test import TestCase

from subscribers.models import Subscriber


class SubscriberModelTests(TestCase):
    def setUp(self) -> None:
        Subscriber.objects.create(email='user1@gmail.com')

    def test_verbose_name_single(self):
        """Subscriber verbose name is set correctly."""
        self.assertEqual(Subscriber._meta.verbose_name, 'subscriber')

    def test_verbose_name_plural(self):
        """Subscriber verbose name (in plural) is set correctly."""
        self.assertEqual(Subscriber._meta.verbose_name_plural, 'subscribers')

    def test_object_name_has_email(self):
        """Subscriber object name is set up correctly."""
        test_subscriber = Subscriber.objects.first()
        self.assertEqual(str(test_subscriber), f"Subscriber: {test_subscriber.email}")

    def test_user_field_params(self):
        """`user` field has correct parameters."""
        user_field = Subscriber._meta.get_field('user')

        self.assertEqual(user_field.verbose_name, 'subscriber')
        self.assertTrue(user_field.null)
        self.assertTrue(user_field.blank)

    def test_email_field_params(self):
        """`email` field has correct parameters."""
        email_field = Subscriber._meta.get_field('email')
        self.assertTrue(email_field.unique)
