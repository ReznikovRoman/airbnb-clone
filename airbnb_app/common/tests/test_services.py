import datetime
from unittest import mock

import fakeredis
import sentry_sdk
from freezegun import freeze_time
from twilio.base.exceptions import TwilioRestException

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from accounts.forms import ProfileForm, UserInfoForm
from accounts.models import CustomUser, Profile

from ..collections import FormWithModel, TwilioShortPayload
from ..constants import VERIFICATION_CODE_STATUS_DELIVERED, VERIFICATION_CODE_STATUS_FAILED
from ..services import (
    _send_sms_by_twilio, create_name_with_prefix, get_field_names_from_form, get_keys_with_prefixes,
    get_required_fields_from_form_with_model, is_cooldown_ended, set_key_with_timeout,
)


class CommonServicesTests(SimpleTestCase):
    redis_server = fakeredis.FakeServer()

    def test_get_field_names_from_form(self):
        """get_field_names_from_form() returns list of form fields."""
        result = get_field_names_from_form(form=UserInfoForm)
        self.assertListEqual(result, ['first_name', 'last_name', 'email'])

    def test_create_name_with_prefix_no_prefix(self):
        """create_name_with_prefix() returns `name` if no `prefix` is given."""
        result = create_name_with_prefix('name', '')
        self.assertEqual(result, 'name')

    def test_create_name_with_prefix_custom_prefix(self):
        """create_name_with_prefix() returns `prefix``name` if prefix is given."""
        result = create_name_with_prefix('name', 'prefix')
        self.assertEqual(result, 'prefix_name')

    def test_create_name_with_prefix_with_underscore_prefix(self):
        """create_name_with_prefix() removes last underscore from the given `prefix` (if any)."""
        result = create_name_with_prefix('name', 'prefix_')
        self.assertEqual(result, 'prefix_name')

    def test_create_name_with_prefix_no_name_no_prefix(self):
        """create_name_with_prefix() returns '_' if both `name` and `prefix` are empty strings."""
        result = create_name_with_prefix('', '')
        self.assertEqual(result, '')

    def test_create_name_with_prefix_no_name_with_prefix(self):
        """create_name_with_prefix() returns `prefix`_ if `name` is an empty string."""
        result = create_name_with_prefix('', 'prefix')
        self.assertEqual(result, 'prefix_')

    def test_create_name_with_prefix_no_name_with_prefix_with_underscore(self):
        """create_name_with_prefix() removes last underscore from the given `prefix` (even if `name` is empty)."""
        result = create_name_with_prefix('', 'prefix_')
        self.assertEqual(result, 'prefix_')

    def test_get_required_fields_from_form_with_model_required_fields_exist(self):
        """get_required_fields_from_form_with_model() returns all required fields from the `form` by `model`."""
        result = get_required_fields_from_form_with_model(
            forms_with_models=[FormWithModel(UserInfoForm, CustomUser)],
        )
        self.assertListEqual(result, ['first_name', 'last_name', 'email'])

    def test_get_required_fields_from_form_with_model_no_required_fields(self):
        """get_required_fields_from_form_with_model() returns [] if there are no required fields in `form`."""
        result = get_required_fields_from_form_with_model(
            forms_with_models=[FormWithModel(ProfileForm, Profile)],
        )
        self.assertListEqual(result, [])

    def test_get_required_fields_from_form_with_model_multiple_forms(self):
        """get_required_fields_from_form_with_model() returns all required fields from the list of `FormWithModel`s."""
        result = get_required_fields_from_form_with_model(
            forms_with_models=[FormWithModel(UserInfoForm, CustomUser), FormWithModel(ProfileForm, Profile)],
        )
        self.assertListEqual(result, ['first_name', 'last_name', 'email'])

    def test_get_keys_with_prefixes_no_prefix(self):
        """get_keys_with_prefixes() returns list of names with prefixes. If given `prefix` is empty, name -> `name`."""
        names = ['name1', 'name2']
        result = get_keys_with_prefixes(names)
        self.assertListEqual(result, ['name1', 'name2'])

    def test_get_keys_with_prefixes_custom_prefix(self):
        """get_keys_with_prefixes() returns list of names with prefixes. If `prefix` is given, name -> prefix_name."""
        names = ['name1', 'name2']
        result = get_keys_with_prefixes(names, prefix='test')
        self.assertListEqual(result, ['test_name1', 'test_name2'])

    @mock.patch(
        'common.services.redis_instance',
        fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True),
    )
    def test_is_cooldown_ended_false(self):
        """is_cooldown_ended() returns False if cooldown hasn't ended."""
        redis_instance = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        key = "user:1:email.sent"
        redis_instance.set(key, 1)
        self.assertFalse(is_cooldown_ended(key))

    @mock.patch(
        'common.services.redis_instance',
        fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True),
    )
    def test_is_cooldown_ended_true_no_key(self):
        """is_cooldown_ended() returns True if there is no `key` in the db."""
        redis_instance = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        redis_instance.flushall()
        key = "user:1:email.sent"
        self.assertTrue(is_cooldown_ended(key))

    @mock.patch(
        'common.services.redis_instance',
        fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True),
    )
    def test_is_cooldown_ended_true_cooldown_ended(self):
        """is_cooldown_ended() returns True if cooldown has ended."""
        redis_instance = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        redis_instance.flushall()
        key = "user:1:email.sent"
        timeout = 1
        set_key_with_timeout(key, timeout, 1)
        time_after_timeout = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

        with freeze_time(time_after_timeout.isoformat()):
            self.assertTrue(is_cooldown_ended(key))

    @mock.patch(
        'common.services.redis_instance',
        fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True),
    )
    def test_is_cooldown_ended_false_cooldown_did_not_end(self):
        """is_cooldown_ended() returns False if cooldown hasn't ended yet."""
        redis_instance = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)
        redis_instance.flushall()
        key = "user:1:email.sent"
        timeout = 1

        set_key_with_timeout(key, timeout, 1)

        self.assertFalse(is_cooldown_ended(key))

    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    def test_send_sms_by_twilio_success(self, message_mock):
        """_send_sms_by_twilio() sends SMS to the given number - `sms_to` with the `body`."""
        body = "Test SMS"
        sms_from = settings.TWILIO_PHONE_NUMBER
        sms_to = "+79851686043"

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        with self.assertLogs(logger='common.services', level='INFO') as cm:
            twilio_payload = _send_sms_by_twilio(body, sms_from, sms_to)

            self.assertEqual(len(cm.output), 2)
            self.assertIn(body, cm.output[0])
            self.assertIn(sms_to, cm.output[0])
            self.assertIn(sms_from, cm.output[0])
            self.assertIn(sms_to, cm.output[1])
            self.assertIn(expected_sid, cm.output[1])

        self.assertTrue(message_mock.called)
        self.assertEqual(twilio_payload.sid, expected_sid)
        self.assertEqual(twilio_payload.status, VERIFICATION_CODE_STATUS_DELIVERED)

    @override_settings(SENTRY_CONF=sentry_sdk.init())  # disable sentry
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    def test_send_sms_by_twilio_failure(self, message_mock):
        """_send_sms_by_twilio() returns payload with `failed` status and logs an exception."""
        body = "Test SMS"
        sms_to = "+79851686043121212"
        sms_from = settings.TWILIO_PHONE_NUMBER
        error_message = f"Unable to create record: The 'To' number {sms_to} is not a valid phone number."

        status = 500
        uri = '/Accounts/ACXXXXXXXXXXXXXXXXX/Messages.json'
        message_mock.side_effect = TwilioRestException(status, uri, msg=error_message)

        with self.assertLogs(logger='common.services') as cm:
            twilio_payload = _send_sms_by_twilio(body, sms_from, sms_to)

            self.assertEqual(len(cm.output), 2)
            self.assertIn(body, cm.output[0])
            self.assertIn(sms_to, cm.output[0])
            self.assertIn(sms_from, cm.output[0])
            self.assertIn(sms_to, cm.output[1])
            self.assertIn(error_message, cm.output[1])

        self.assertTrue(message_mock.called)
        self.assertEqual(twilio_payload.status, VERIFICATION_CODE_STATUS_FAILED)
        self.assertIsNone(twilio_payload.sid)
