from unittest import mock

import fakeredis

from django.core import mail
from django.http import Http404
from django.test import TestCase, override_settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.models import Group

from accounts.models import CustomUser, Profile, SMSLog
from common.constants import VERIFICATION_CODE_STATUS_DELIVERED, VERIFICATION_CODE_STATUS_FAILED
from common.collections import TwilioShortPayload
from ..tokens import account_activation_token
from ..services import (has_user_profile_image, get_user_by_email, get_user_from_uid, add_user_to_group,
                        update_phone_number_confirmation_status, update_user_email_confirmation_status,
                        get_verification_code_from_digits_dict, is_verification_code_for_profile_valid,
                        handle_phone_number_change, send_greeting_email, send_verification_link, get_user_by_pk,
                        get_phone_code_status_by_user_id, set_phone_code_status_by_user_id)


class AccountsServicesTests(TestCase):
    redis_server = fakeredis.FakeServer()

    def setUp(self):
        test_user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        test_user1.profile.profile_image = 'image.png'
        test_user1.save()

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='William',
            last_name='Brown',
            password='test',
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_greeting_email_correct_body(self):
        """Test that Greeting Email's body is correct (subject, content, recipient)."""
        test_user: CustomUser = CustomUser.objects.first()
        test_domain = 'airbnb'
        test_scheme = 'https'
        test_content = render_to_string(
            template_name='accounts/emails/greeting_email.html',
            context={
                'protocol': test_scheme,
                'domain': test_domain,
            }
        )

        send_greeting_email(domain=test_domain, scheme=test_scheme, user=test_user)

        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.subject, 'Thanks for signing up')
        self.assertEqual(test_email.body, test_content)
        self.assertEqual(test_email.to, [test_user.email])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_verification_link_correct_body(self):
        """Test that Verification Email's body is correct (subject, content, recipient)."""
        test_user: CustomUser = CustomUser.objects.first()
        test_domain = 'airbnb'
        test_scheme = 'https'
        test_content = render_to_string(
            template_name='accounts/registration/account_activation_email.html',
            context={
                'user': test_user,
                'protocol': test_scheme,
                'domain': test_domain,
                'uid': urlsafe_base64_encode(force_bytes(test_user.pk)),
                'token': account_activation_token.make_token(test_user),
            }
        )

        send_verification_link(domain=test_domain, scheme=test_scheme, user=test_user)

        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.subject, 'Activate your account')
        self.assertEqual(str(test_email.body), str(test_content))
        self.assertEqual(test_email.to, [test_user.email])

    def test_get_user_by_pk_existing_user(self):
        """get_user_by_pk() returns a CustomUser object if user with the given `pk` exists."""
        self.assertEqual(get_user_by_pk(pk=CustomUser.objects.first().pk), CustomUser.objects.first())

    def test_get_user_by_pk_invalid_pk(self):
        """get_user_by_pk() raises a Http404 exception if there is no user with the given `pk`."""
        with self.assertRaises(Http404):
            get_user_by_pk(pk=1)

    def test_get_user_by_email_existing_user(self):
        """get_user_by_email() returns a QuerySet with a CustomUser if user with the given `email` exists."""
        qs = get_user_by_email(email='user1@gmail.com')

        self.assertTrue(qs.exists())
        self.assertEqual(qs.first(), CustomUser.objects.first())

    def test_test_get_user_by_email_empty_queryset(self):
        """get_user_by_email() returns an empty QuerySet if user with the given `email` doesn't exists."""
        qs = get_user_by_email(email='empty@gmail.com')

        self.assertFalse(qs.exists())
        self.assertEqual(list(qs), [])

    def test_get_user_from_uid_success(self):
        """get_user_from_uid() returns a CustomUser object by a UID."""
        test_user = CustomUser.objects.first()
        test_uid = urlsafe_base64_encode(force_bytes(test_user.pk))

        result = get_user_from_uid(uid=test_uid)

        self.assertEqual(result, test_user)

    def test_add_user_to_group_new_group(self):
        """add_user_to_group() adds `user` to a Group with the given `group_name` (creates group if necessary)."""
        test_user: CustomUser = CustomUser.objects.first()
        add_user_to_group(user=test_user, group_name='new_group')

        self.assertIn('new_group', test_user.groups.values_list('name', flat=True))

    def test_add_user_to_group_existing_group(self):
        """add_user_to_group() adds `user` to a Group with the given `group_name`."""
        test_user: CustomUser = CustomUser.objects.first()
        Group.objects.create(name='test_group')

        add_user_to_group(user=test_user, group_name='test_group')

        self.assertIn('test_group', test_user.groups.values_list('name', flat=True))

    def test_has_user_profile_image_valid_image(self):
        """has_user_profile_image() returns True if CustomUser has a profile image and it is not a default one."""
        self.assertTrue(has_user_profile_image(user_profile=CustomUser.objects.first().profile))

    def test_has_user_profile_image_default_image(self):
        """has_user_profile_image() returns False if user doesn't have a profile image or it is a default one."""
        self.assertFalse(has_user_profile_image(user_profile=CustomUser.objects.get(email='user2@gmail.com').profile))

    def test_update_phone_number_confirmation_status_success(self):
        """update_phone_number_confirmation_status() updates status to the given `is_phone_number_confirmed`."""
        test_profile: Profile = CustomUser.objects.first().profile
        update_phone_number_confirmation_status(user_profile=test_profile, is_phone_number_confirmed=True)

        self.assertTrue(test_profile.is_phone_number_confirmed)

    def test_update_user_email_confirmation_status_success(self):
        """update_user_email_confirmation_status() updates status to the given `is_email_confirmed`."""
        test_user: CustomUser = CustomUser.objects.first()
        update_user_email_confirmation_status(user=test_user, is_email_confirmed=True)

        self.assertTrue(test_user.is_email_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    def test_handle_phone_number_change(self, message_mock):
        """Test that user's phone number is now unconfirmed, and SMS verification code was sent."""
        test_profile: Profile = CustomUser.objects.first().profile
        test_domain: str = 'airbnb'
        test_phone_number = '+79851686043'

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        twilio_payload: TwilioShortPayload = handle_phone_number_change(test_profile, test_domain, test_phone_number)

        self.assertFalse(test_profile.is_phone_number_confirmed)

        self.assertTrue(message_mock.called)
        self.assertTrue(twilio_payload.sid, expected_sid)

    def test_get_verification_code_from_digits_dict_correct_result(self):
        """get_verification_code_from_digits_dict() joins values of a given dict and returns result."""
        test_dict = {'a': '1', 'b': '2'}
        result = get_verification_code_from_digits_dict(test_dict)

        self.assertEqual(result, '12')

    def test_is_verification_code_for_profile_valid_correct_code(self):
        """is_verification_code_for_profile_valid() returns True if the given `verification_code` is valid."""
        test_profile: Profile = CustomUser.objects.first().profile
        test_sms_code: str = SMSLog.objects.create(sms_code='1234', profile=test_profile).sms_code

        self.assertTrue(is_verification_code_for_profile_valid(test_profile, test_sms_code))

    def test_is_verification_code_for_profile_valid_invalid_code(self):
        """is_verification_code_for_profile_valid() returns False if the given `verification_code` is invalid."""
        test_profile: Profile = CustomUser.objects.first().profile
        test_sms_code: str = SMSLog.objects.create(sms_code='1234', profile=test_profile).sms_code

        self.assertFalse(is_verification_code_for_profile_valid(test_profile, test_sms_code + '1'))

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_set_phone_code_status_by_user_id_new_item(self):
        """set_phone_code_status_by_user_id() creates `phone_code_status` with the given `user_id` and code_status."""
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        user_id = 1
        test_value = VERIFICATION_CODE_STATUS_FAILED

        set_phone_code_status_by_user_id(user_id, test_value)

        self.assertEqual(r.get(f"user:{user_id}:phone_code_status"), test_value)

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_set_phone_code_status_by_user_id_overwrite_existing(self):
        """set_phone_code_status_by_user_id() overwrites `phone_code_status` if it already exists."""
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        user_id = 1
        test_key = f"user:{user_id}:phone_code_status"
        initial_value = VERIFICATION_CODE_STATUS_FAILED

        r.set(test_key, initial_value)

        new_value = VERIFICATION_CODE_STATUS_DELIVERED

        set_phone_code_status_by_user_id(user_id, new_value)

        self.assertEqual(r.get(f"user:{user_id}:phone_code_status"), new_value)

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_get_phone_code_status_by_user_id_existing_key(self):
        """get_phone_code_status_by_user_id() returns `phone_code_status` from Redis by the given `user_id`."""
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        user_id = 1
        test_key = f"user:{user_id}:phone_code_status"
        test_value = VERIFICATION_CODE_STATUS_FAILED

        r.set(test_key, test_value)

        self.assertEqual(get_phone_code_status_by_user_id(user_id), test_value)

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_get_phone_code_status_by_user_id_no_key(self):
        """get_phone_code_status_by_user_id() returns None if key with the given `user_id` doesn't exist."""
        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        user_id = 1
        test_key = f"user:{user_id}:phone_code_status"
        test_value = VERIFICATION_CODE_STATUS_FAILED

        r.set(test_key, test_value)

        self.assertIsNone(get_phone_code_status_by_user_id(2))
