from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase
from django.test.utils import override_settings

from accounts.models import CustomUser
from addresses.models import Address
from hosts.models import RealtyHost
from realty.models import Realty, RealtyTypeChoices

from ..models import Subscriber
from ..services import (
    get_subscriber_by_email, get_subscriber_by_user, send_recommendation_email_to_subscriber, set_user_for_subscriber,
    update_email_for_subscriber_by_user,
)


class SubscribersServicesTests(TestCase):
    def setUp(self) -> None:
        Subscriber.objects.create(email='sub1@gmail.com')

        test_user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        Subscriber.objects.create(user=test_user1, email=test_user1.email)

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )

        # create user with the email: user3@gmail.com
        CustomUser.objects.create_user(
            email='user3@gmail.com',
            first_name='Peter',
            last_name='Collins',
            password='test',
        )
        # create subscriber with the same email
        Subscriber.objects.create(email='user3@gmail.com')

        # create user with the email: user4@gmail.com
        test_user2 = CustomUser.objects.create_user(
            email='user4@gmail.com',
            first_name='Brad',
            last_name='Parker',
            password='test',
        )
        # create subscriber and link it to the `test_user2`
        Subscriber.objects.create(user=test_user2, email=test_user2.email)

        test_user3 = CustomUser.objects.create_user(
            email='user5@gmail.com',
            first_name='Jake',
            last_name='White',
            password='test',
        )
        Subscriber.objects.create(user=test_user3, email=test_user3.email)

    @classmethod
    def setUpTestData(cls):
        test_user1 = CustomUser.objects.create_user(
            email='host1@gmail.com',
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

    def test_get_subscriber_by_email_correct_qs(self):
        """get_subscriber_by_email() returns a QuerySet[Subscriber] if subscriber with the given `email` exists."""
        test_sub = Subscriber.objects.first()
        self.assertEqual(get_subscriber_by_email(email='sub1@gmail.com').first(), test_sub)

    def test_get_subscriber_by_email_empty_qs(self):
        """get_subscriber_by_email() returns an empty QuerySet if there is no subscriber with the given `email`."""
        self.assertQuerysetEqual(get_subscriber_by_email(email='invalid@gmail.com'), [])

    def test_get_subscriber_by_user_correct_qs(self):
        """get_subscriber_by_user() returns a QuerySet[Subscriber] if subscriber linked to the given `user` exists."""
        test_sub = Subscriber.objects.get(email='user1@gmail.com')
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        self.assertEqual(get_subscriber_by_user(user=test_user).first(), test_sub)

    def test_get_subscriber_by_user_empty_qs(self):
        """get_subscriber_by_user() returns an empty QuerySet if there is no subscriber linked to the given `user`."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        self.assertQuerysetEqual(get_subscriber_by_user(user=test_user), [])

    def test_set_user_for_subscriber_successful_update(self):
        """set_user_for_subscriber() links subscriber with the given `user`
        if there is a subscriber with the `user.email`.
        """
        test_user = CustomUser.objects.get(email='user3@gmail.com')

        # update `user` field for test_sub
        is_updated = set_user_for_subscriber(user=test_user)

        test_sub = Subscriber.objects.get(email='user3@gmail.com')

        self.assertTrue(is_updated)
        self.assertEqual(test_sub.user, test_user)

    def test_set_user_for_subscriber_no_update(self):
        """set_user_for_subscriber() doesn't link subscriber with the given `user`
        if there is no subscriber with the `user.email`.
        """
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        is_updated = set_user_for_subscriber(user=test_user)

        self.assertFalse(is_updated)

    def test_update_email_for_subscriber_by_user_successful_update(self):
        """update_email_for_subscriber_by_user() updates subscriber's email when user updates his email."""
        test_user = CustomUser.objects.get(email='user4@gmail.com')
        test_sub = Subscriber.objects.get(email='user4@gmail.com')

        test_user.email = 'new4@gmail.com'
        test_user.save(update_fields=['email'])

        is_updated = update_email_for_subscriber_by_user(user=test_user)

        self.assertTrue(is_updated)
        self.assertTrue(test_sub.email, 'new4@gmail.com')

    def test_update_email_for_subscriber_by_user_no_update(self):
        """update_email_for_subscriber_by_user() doesn't update subscriber's email
        if the is no subscriber with `user.email`.
        """
        test_user = CustomUser.objects.get(email='user5@gmail.com')
        test_sub = Subscriber.objects.get(email='user5@gmail.com')

        update_email_for_subscriber_by_user(test_user)

        self.assertEqual(test_sub.email, 'user5@gmail.com')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_recommendation_email_to_subscriber_correct_body(self):
        """Verification email's body is correct (subject, content, recipient)."""
        test_subscriber: Subscriber = Subscriber.objects.get(email='user4@gmail.com')
        realty_recommendations = Realty.objects.all()
        test_domain = 'airbnb'
        test_protocol = settings.DEFAULT_PROTOCOL
        test_content = render_to_string(
            template_name='subscribers/promo/new_realty.html',
            context={
                'subscriber': test_subscriber,
                'realty_list': realty_recommendations,
                'protocol': test_protocol,
                'domain': test_domain,
            },
        )

        send_recommendation_email_to_subscriber(
            site_domain=test_domain,
            subscriber_id=test_subscriber.pk,
            realty_recommendations=realty_recommendations,
        )

        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.subject, 'Check out new realty')
        self.assertEqual(str(test_email.body), str(test_content))
        self.assertEqual(test_email.to, [test_subscriber.email])
