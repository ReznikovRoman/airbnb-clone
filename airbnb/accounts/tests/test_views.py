import re
import base64
import shutil
import tempfile
from unittest import mock

import fakeredis

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse, reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile

from hosts.models import RealtyHost
from hosts.services import get_host_or_none_by_user
from realty.models import Realty
from common.constants import (VERIFICATION_CODE_STATUS_DELIVERED, VERIFICATION_CODE_STATUS_FAILED)
from common.collections import TwilioShortPayload
from accounts.models import CustomUser, SMSLog
from addresses.models import Address
from realty.services.realty import get_available_realty_by_host
from .. import views
from ..forms import (SignUpForm, CustomPasswordResetForm, ProfileForm, UserInfoForm, ProfileImageForm,
                     ProfileDescriptionForm, VerificationCodeForm)

MEDIA_ROOT = tempfile.mkdtemp()


class SignUpViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.SignUpView.form_class, SignUpForm)
        self.assertEqual(views.SignUpView.template_name, 'accounts/registration/signup.html')

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        response = self.client.get(reverse('accounts:signup'))
        self.assertTemplateUsed(response, 'accounts/registration/signup.html')

    def test_context_correct_data(self):
        """Test that request.context has correct data."""
        response = self.client.get(reverse('accounts:signup'))
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_redirect_if_logged_in(self):
        """Test that an authenticated user is redirected to the home page."""
        self.client.login(username='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:signup'))

        self.assertRedirects(response, reverse('home_page'))

    def test_redirects_to_login_page_on_success(self):
        """Test that user is redirected to the login page on the successful form submission."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        response = self.client.post(reverse('accounts:signup'), data=form_data)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_renders_form_errors_on_failure(self):
        """Test that form errors are rendered if there are some errors in the form."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'invalid',
        }
        response = self.client.post(reverse('accounts:signup'), data=form_data)

        self.assertTemplateUsed(response, 'accounts/registration/signup.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_creates_new_user_on_success(self):
        """Test that new user is created on the successful form submission."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        self.client.post(reverse('accounts:signup'), data=form_data)

        self.assertTrue(CustomUser.objects.filter(email=form_data['email']).exists())

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sends_email_verification_link_on_success(self):
        """Test that verification link is sent on the successful form submission."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        self.client.post(reverse('accounts:signup'), data=form_data)

        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.to, [form_data['email']])


class LoginViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.LoginView.template_name, 'accounts/registration/login.html')

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_logged_in(self):
        """Test that an authenticated user is redirected to the home page."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:login'))

        self.assertRedirects(response, reverse('home_page'))

    def test_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        response = self.client.get(reverse('accounts:login'))
        self.assertTemplateUsed(response, 'accounts/registration/login.html')


class CustomPasswordResetViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.CustomPasswordResetView.template_name, 'accounts/registration/password_reset.html')
        self.assertEqual(views.CustomPasswordResetView.success_url, reverse_lazy('accounts:password_reset_done'))
        self.assertEqual(views.CustomPasswordResetView.html_email_template_name,
                         'accounts/registration/password_reset_email.html')
        self.assertEqual(views.CustomPasswordResetView.email_template_name,
                         'accounts/registration/password_reset_email.html')
        self.assertEqual(views.CustomPasswordResetView.form_class, CustomPasswordResetForm)

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:password_reset'))

        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:password_reset'))

        self.assertTemplateUsed(response, 'accounts/registration/password_reset.html')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_sends_email_using_celery_on_success(self):
        """Test that view sends a custom email using Celery on the successful form submission."""
        form_data = {
            'email': 'user1@gmail.com',
        }
        self.client.login(email='user1@gmail.com', password='test')
        self.client.post(reverse('accounts:password_reset'), data=form_data)

        test_email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.to, [form_data['email']])


class AccountActivationViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_confirmed_on_success(self):
        """Test that user's email is confirmed on successful activation."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        self.client.post(reverse('accounts:signup'), data=form_data)

        test_email = mail.outbox[0]

        link = re.search(r'href=[\'"]?([^\'" >]+)', test_email.body).group(1)

        self.client.get(link)

        self.assertTrue(CustomUser.objects.get(email='new1@gmail.com').is_email_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_unconfirmed_on_failure(self):
        """Test that user's email is unconfirmed if activation fails."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        self.client.post(reverse('accounts:signup'), data=form_data)

        test_email = mail.outbox[0]

        link = re.search(r'href=[\'"]?([^\'" >]+)', test_email.body).group(1)

        self.client.get(link[:-3])  # link with the invalid token

        self.assertFalse(CustomUser.objects.get(email='new1@gmail.com').is_email_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_logged_in_on_success(self):
        """Test that user is logged in on successful activation."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        self.client.post(reverse('accounts:signup'), data=form_data)
        test_email = mail.outbox[0]
        link = re.search(r'href=[\'"]?([^\'" >]+)', test_email.body).group(1)
        self.client.get(link)
        response = self.client.get(reverse('home_page'))

        self.assertTrue(response.context['user'].is_authenticated)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_redirect_on_success(self):
        """Test that user is redirected on successful activation."""
        form_data = {
            'email': 'new1@gmail.com',
            'first_name': 'New 1',
            'last_name': 'User 1',
            'password1': 'test',
            'password2': 'test',
        }
        self.client.post(reverse('accounts:signup'), data=form_data)
        test_email = mail.outbox[0]
        link = re.search(r'href=[\'"]?([^\'" >]+)', test_email.body).group(1)

        response = self.client.get(link)

        self.assertRedirects(response, reverse('home_page'))


class ActivationRequiredViewTests(SimpleTestCase):
    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.ActivationRequiredView.template_name,
                         'accounts/registration/account_activation_required.html')

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        response = self.client.get(reverse('accounts:activation_required'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        response = self.client.get(reverse('accounts:activation_required'))
        self.assertTemplateUsed(response, 'accounts/registration/account_activation_required.html')


class AccountSettingsDashboardViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.AccountSettingsDashboardView.template_name,
                         'accounts/settings/settings_dashboard.html')

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:settings_dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:settings_dashboard'))
        self.assertTemplateUsed(response, 'accounts/settings/settings_dashboard.html')


class PersonalInfoEditViewTests(TestCase):
    redis_server = fakeredis.FakeServer()

    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

        # create user with the phone number
        test_user2 = CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )
        test_user2.profile.phone_number = '+79851234567'
        test_user2.profile.save()

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.PersonalInfoEditView.template_name, 'accounts/settings/user_form.html')
        self.assertTrue(hasattr(views.PersonalInfoEditView, 'profile_form'))
        self.assertTrue(hasattr(views.PersonalInfoEditView, 'user_info_form'))

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:user_info_edit'))

        self.assertEqual(response.status_code, 200)

    def test_correct_context_data(self):
        """Test that request.context is correct."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:user_info_edit'))

        self.assertIsInstance(response.context['user_info_form'], UserInfoForm)
        self.assertIsInstance(response.context['profile_form'], ProfileForm)

    def test_correct_user_instance(self):
        """Test that we are editing the logged in user."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:user_info_edit'))

        user_form: UserInfoForm = response.context['user_info_form']
        profile_form: ProfileForm = response.context['profile_form']

        self.assertEqual(user_form.instance, CustomUser.objects.get(email='user1@gmail.com'))
        self.assertEqual(profile_form.instance, CustomUser.objects.get(email='user1@gmail.com').profile)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_email_update_successful(self):
        """Test that if email has been changed, new email should be `unconfirmed` and verification should be sent."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        form_data = {
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'email': 'new1@gmail.com',
        }

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        test_email = mail.outbox[0]

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:user_info_edit'))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(test_email.to, [form_data['email']])

        self.assertFalse(test_user.is_email_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_renders_form_errors_on_failure(self):
        """Test that form errors are rendered correctly if there are any errors in the form."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        form_data = {
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'email': 'user2@gmail.com',  # error: email is not unique
        }

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/settings/user_form.html')
        self.assertFalse(response.context['user_info_form'].is_valid())

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_phone_number_new(self, message_mock):
        """Test that if phone number has been added,
        SMS code should be sent, `phone_number` is `unconfirmed` and `phone_code_status` should be updated.
        """
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        redis_key = f"user:{test_user.id}:phone_code_status"
        form_data = {
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'email': test_user.email,
            'phone_number': '+79851686043',  # add new phone number
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        self.client.login(email='user1@gmail.com', password='test')
        self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        # SMS has been sent by Twilio
        self.assertTrue(message_mock.called)

        # Message has been delivered --> `phone_code_status` has appropriate value
        self.assertEqual(r.get(redis_key), VERIFICATION_CODE_STATUS_DELIVERED)

        # New phone number has been added --> it isn't `confirmed` yet
        self.assertFalse(test_user.profile.is_phone_number_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_phone_number_update(self, message_mock):
        """Test that if phone number has been updated,
        SMS code should be sent, `phone_number` is `unconfirmed` and `phone_code_status` should be updated.
        """
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        redis_key = f"user:{test_user.id}:phone_code_status"
        form_data = {
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'email': test_user.email,
            'phone_number': '8 (301) 123-45-67',  # update phone number
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        self.client.login(email='user2@gmail.com', password='test')
        self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        # SMS has been sent by Twilio
        self.assertTrue(message_mock.called)

        # Message has been delivered --> `phone_code_status` has appropriate value
        self.assertEqual(r.get(redis_key), VERIFICATION_CODE_STATUS_DELIVERED)

        # Phone number has been updated --> it isn't `confirmed` yet
        self.assertFalse(test_user.profile.is_phone_number_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_phone_number_resend(self, message_mock):
        """Test that if verification code hasn't been sent, new code will be sent."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        redis_key = f"user:{test_user.id}:phone_code_status"
        form_data = {
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'email': test_user.email,
            'phone_number': '8 (301) 123-45-67',  # update phone number
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_FAILED, sid=expected_sid)

        r = fakeredis.FakeStrictRedis(server=self.redis_server, charset="utf-8", decode_responses=True)

        self.client.login(email='user2@gmail.com', password='test')
        self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        # Twilio SMS
        self.assertTrue(message_mock.called)

        # Message has been delivered --> `phone_code_status` has appropriate value
        self.assertEqual(r.get(redis_key), VERIFICATION_CODE_STATUS_FAILED)

        # Try to post form data again
        self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        # Twilio tries to send a verification code again (because it wasn't delivered earlier)
        self.assertTrue(message_mock.called)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_phone_number_remove(self, message_mock):
        """Test that if phone number has been removed, phone number is `unconfirmed`."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        form_data = {
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'email': test_user.email,
            'phone_number': '',  # remove existing phone number
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        self.client.login(email='user2@gmail.com', password='test')
        self.client.post(reverse('accounts:user_info_edit'), data=form_data)

        # No SMS has been sent
        self.assertFalse(message_mock.called)

        # No phone_number --> phone_number is `unconfirmed`
        self.assertFalse(test_user.profile.is_phone_number_confirmed)


class ProfileShowViewTests(TestCase):
    def setUp(self) -> None:
        user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )
        host1 = RealtyHost.objects.create(user=user1)
        location1 = Address.objects.create(
            country='Russia',
            city='Moscow',
            street='Arbat, 20'
        )
        Realty.objects.create(
            host=host1,
            location=location1,
            name='test',
            description='test',
            is_available=True,
            beds_count=2,
            max_guests_count=4,
            price_per_night=100,
        )

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Mike',
            last_name='Smith',
            password='test'
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.ProfileShowView.template_name, 'accounts/profile/show.html')
        self.assertTrue(hasattr(views.ProfileShowView, 'profile_owner'))
        self.assertTrue(hasattr(views.ProfileShowView, 'is_profile_of_current_user'))

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        response = self.client.get(reverse('accounts:profile_show', kwargs={'user_pk': CustomUser.objects.first().id}))
        self.assertEqual(response.status_code, 200)

    def test_correct_context_data_if_profile_owner(self):
        """Test that request.context is correct if current user is a profile owner."""
        self.client.login(email='user1@gmail.com', password='test')
        current_user = CustomUser.objects.get(email='user1@gmail.com')
        response = self.client.get(reverse('accounts:profile_show', kwargs={'user_pk': current_user.pk}))

        self.assertEqual(response.context['profile_owner'], current_user)
        self.assertTrue(response.context['is_profile_of_current_user'])
        self.assertQuerysetEqual(
            response.context['host_listings'],
            get_available_realty_by_host(get_host_or_none_by_user(user=current_user)),
            transform=lambda qs: qs,
        )

    def test_correct_context_data_if_not_a_profile_owner(self):
        """Test that request.context is correct if current user is not a profile owner."""
        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.get(reverse('accounts:profile_show', kwargs={'user_pk': CustomUser.objects.first().id}))

        self.assertEqual(response.context['profile_owner'], CustomUser.objects.first())
        self.assertFalse(response.context['is_profile_of_current_user'])
        self.assertQuerysetEqual(
            response.context['host_listings'],
            get_available_realty_by_host(get_host_or_none_by_user(user=CustomUser.objects.first())),
            transform=lambda qs: qs,
        )

    def test_correct_context_data_if_not_logged_in(self):
        """Test that request.context is correct if current user is a `AnonymousUser`."""
        response = self.client.get(reverse('accounts:profile_show', kwargs={'user_pk': CustomUser.objects.first().id}))

        self.assertEqual(response.context['profile_owner'], CustomUser.objects.first())
        self.assertFalse(response.context['is_profile_of_current_user'])
        self.assertQuerysetEqual(
            response.context['host_listings'],
            get_available_realty_by_host(get_host_or_none_by_user(user=CustomUser.objects.first())),
            transform=lambda qs: qs,
        )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ProfileImageEditViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete temp media dir
        super().tearDownClass()

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.ProfileImageEditView.template_name, 'accounts/profile/edit_image.html')
        self.assertTrue(hasattr(views.ProfileImageEditView, 'profile_image_form'))

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:edit_image'))

        self.assertEqual(response.status_code, 200)

    def test_correct_context_data_if_logged_in(self):
        """Test that request.context is correct if user is logged in."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:edit_image'))

        self.assertIsInstance(response.context['profile_image_form'], ProfileImageForm)
        self.assertEqual(response.context['profile_image_form'].instance, test_user.profile)

    def test_view_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:edit_image'))

        self.assertTemplateUsed(response, 'accounts/profile/edit_image.html')

    def test_post_image_success(self):
        """Test that user can upload a profile image."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        test_image_name = 'image.png'
        test_image = SimpleUploadedFile(
            name=test_image_name,
            content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4"
                                     "//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="),
            content_type='image/png',
        )

        form_data = {
            'profile_image': test_image,
        }

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.post(reverse('accounts:edit_image'), data=form_data)

        self.assertRedirects(response, reverse('accounts:profile_show', kwargs={'user_pk': test_user.pk}))
        self.assertIsNotNone(test_user.profile.profile_image)
        self.assertEqual(test_user.profile.profile_image.name,
                         f"upload/users/{test_user.email}/profile/{test_image_name}")

    def test_post_image_fail(self):
        """Test that form errors are rendered correctly if uploaded image is not valid."""
        test_image_name = 'image.png'
        test_image = SimpleUploadedFile(
            name=test_image_name,
            content=b"_",  # invalid image
        )

        form_data = {
            'profile_image': test_image,
        }

        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.post(reverse('accounts:edit_image'), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['profile_image_form'].is_valid())


class ProfileDescriptionEditViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

        test_user2 = CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Bill',
            last_name='Smith',
            password='test',
        )
        test_user2.profile.description = "First desc"
        test_user2.profile.save()

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.ProfileDescriptionEditView.template_name, 'accounts/profile/edit_description.html')
        self.assertTrue(hasattr(views.ProfileDescriptionEditView, 'profile_description_form'))

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:edit_description'))

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that view uses a correct HTML template."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:edit_description'))

        self.assertTemplateUsed(response, 'accounts/profile/edit_description.html')

    def test_correct_context_data_if_logged_in(self):
        """Test that request.context is correct if user is logged in."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:edit_description'))

        self.assertIsInstance(response.context['profile_description_form'], ProfileDescriptionForm)
        self.assertEqual(response.context['profile_description_form'].instance, test_user.profile)

    def test_add_description_success(self):
        """Test that user can add `description`."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        form_data = {
            'description': 'Test desc',
        }
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.post(reverse('accounts:edit_description'), data=form_data)

        self.assertRedirects(response, reverse('accounts:profile_show', kwargs={'user_pk': test_user.pk}))
        self.assertEqual(test_user.profile.description, form_data['description'])

    def test_update_description_success(self):
        """Test that user can edit `description`."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        form_data = {
            'description': '',
        }
        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.post(reverse('accounts:edit_description'), data=form_data)

        self.assertRedirects(response, reverse('accounts:profile_show', kwargs={'user_pk': test_user.pk}))
        self.assertEqual(test_user.profile.description, form_data['description'])


class SecurityDashboardViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.SecurityDashboardView.template_name, 'accounts/settings/security_dashboard.html')

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:security_dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_correct_context_data_if_logged_in(self):
        """Test that request.context is correct if user is logged in."""
        test_user = CustomUser.objects.get(email='user1@gmail.com')
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:security_dashboard'))

        self.assertEqual(response.context['phone_number'], test_user.profile.phone_number)
        self.assertEqual(response.context['email'], test_user.email)


class PhoneNumberConfirmPageViewTests(TestCase):
    redis_server = fakeredis.FakeServer()

    def setUp(self) -> None:
        test_user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        test_user1.profile.phone_number = '+79851686043'
        test_user1.profile.save()

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Bill',
            last_name='Smith',
            password='test',
        )

        test_user3 = CustomUser.objects.create_user(
            email='user3@gmail.com',
            first_name='Mike',
            last_name='Williams',
            password='test',
        )
        test_user3.profile.phone_number = '89261234567'
        test_user3.profile.is_phone_number_confirmed = True
        test_user3.profile.save()

    def test_view_correct_attrs(self):
        """Test that view has correct attributes."""
        self.assertEqual(views.PhoneNumberConfirmPageView.template_name, 'accounts/settings/confirm_phone.html')
        self.assertTrue(hasattr(views.PhoneNumberConfirmPageView, 'verification_code_form'))
        self.assertTrue(hasattr(views.PhoneNumberConfirmPageView, 'is_verification_code_sent'))

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name."""
        self.client.login(email='user1@gmail.com', password='test')
        response = self.client.get(reverse('accounts:confirm_phone'))

        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_correct_context_data_if_verification_code_sent(self, message_mock):
        """Test that request.context is correct if verification code has been sent."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        test_phone_number = '89851234567'
        user_form_data = {
            'email': test_user.email,
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'phone_number': test_phone_number,
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        # user without a phone_number
        self.client.login(email='user2@gmail.com', password='test')

        # add new phone number
        self.client.post(reverse('accounts:user_info_edit'), data=user_form_data)

        response = self.client.get(reverse('accounts:confirm_phone'))

        self.assertIsInstance(response.context['verification_code_form'], VerificationCodeForm)
        self.assertTrue(response.context['is_verification_code_sent'])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_correct_context_data_if_verification_code_not_sent(self, message_mock):
        """Test that request.context is correct if verification code hasn't been sent."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        test_phone_number = '89851234567'
        user_form_data = {
            'email': test_user.email,
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'phone_number': test_phone_number,
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_FAILED, sid=expected_sid)

        # user without a phone_number
        self.client.login(email='user2@gmail.com', password='test')

        # add new phone number
        self.client.post(reverse('accounts:user_info_edit'), data=user_form_data)

        response = self.client.get(reverse('accounts:confirm_phone'))

        self.assertIsInstance(response.context['verification_code_form'], VerificationCodeForm)
        self.assertFalse(response.context['is_verification_code_sent'])

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_redirect_if_no_phone_number(self):
        """Test that if user has no `phone_number`, he should be redirected."""
        self.client.login(email='user2@gmail.com', password='test')  # user without phone_number
        response = self.client.get(reverse('accounts:confirm_phone'))

        self.assertRedirects(response, reverse('accounts:settings_dashboard'))

    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_redirect_if_phone_number_confirmed(self):
        """Test that if user has a `confirmed` `phone_number`, he should be redirected."""
        self.client.login(email='user3@gmail.com', password='test')  # user with a `confirmed` phone_number
        response = self.client.get(reverse('accounts:confirm_phone'))

        self.assertRedirects(response, reverse('accounts:settings_dashboard'))

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_confirm_phone_number_success(self, message_mock):
        """Test that user can confirm a phone number."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        test_phone_number = '89851234567'
        user_form_data = {
            'email': test_user.email,
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'phone_number': test_phone_number,
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        # user without a phone_number
        self.client.login(email='user2@gmail.com', password='test')

        # add new phone number
        self.client.post(reverse('accounts:user_info_edit'), data=user_form_data)

        test_sms_log = SMSLog.objects.get(profile=test_user.profile)
        test_verification_code = test_sms_log.sms_code
        code_form_data = {
            'digit_1': test_verification_code[0],
            'digit_2': test_verification_code[1],
            'digit_3': test_verification_code[2],
            'digit_4': test_verification_code[3],
        }

        response_get = self.client.get(reverse('accounts:confirm_phone'))
        response_post = self.client.post(reverse('accounts:confirm_phone'), data=code_form_data)

        # `is_verification_code_sent` from request.context should be `True`
        self.assertTrue(response_get.context['is_verification_code_sent'])

        self.assertRedirects(response_post, reverse('accounts:settings_dashboard'))
        # phone number is now `confirmed`
        self.assertTrue(CustomUser.objects.get(email=test_user.email).profile.is_phone_number_confirmed)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch('configs.twilio_conf.twilio_client.messages.create')
    @mock.patch('accounts.services.r',
                fakeredis.FakeStrictRedis(server=redis_server, charset="utf-8", decode_responses=True))
    def test_confirm_phone_number_invalid_code(self, message_mock):
        """Test that user can't confirm phone number with the invalid verification code."""
        test_user = CustomUser.objects.get(email='user2@gmail.com')
        test_phone_number = '89851234567'
        user_form_data = {
            'email': test_user.email,
            'first_name': test_user.first_name,
            'last_name': test_user.last_name,
            'phone_number': test_phone_number,
        }

        expected_sid = 'SM87105da94bff44b999e4e6eb90d8eb6a'
        message_mock.return_value = TwilioShortPayload(status=VERIFICATION_CODE_STATUS_DELIVERED, sid=expected_sid)

        # user without a phone_number
        self.client.login(email='user2@gmail.com', password='test')

        # add new phone number
        self.client.post(reverse('accounts:user_info_edit'), data=user_form_data)

        test_sms_log = SMSLog.objects.get(profile=test_user.profile)
        test_verification_code = test_sms_log.sms_code
        invalid_code_form_data = {
            'digit_1': test_verification_code[0],
            'digit_2': test_verification_code[1],
            'digit_3': test_verification_code[2],
            'digit_4': str(9 - int(test_verification_code[3])),
        }

        response_get = self.client.get(reverse('accounts:confirm_phone'))
        response_post = self.client.post(reverse('accounts:confirm_phone'), data=invalid_code_form_data)

        # `is_verification_code_sent` from request.context should be `True`
        self.assertTrue(response_get.context['is_verification_code_sent'])

        self.assertTemplateUsed(response_post, 'accounts/settings/confirm_phone.html')
        # phone number is not `confirmed` (invalid verification code)
        self.assertFalse(CustomUser.objects.get(email=test_user.email).profile.is_phone_number_confirmed)


class SendConfirmationEmailViewTests(TestCase):
    def setUp(self) -> None:
        test_user1 = CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test',
        )
        test_user1.is_email_confirmed = True
        test_user1.save()

        CustomUser.objects.create_user(
            email='user2@gmail.com',
            first_name='Bill',
            last_name='Smith',
            password='test',
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_view_url_accessible_by_name(self):
        """Test that view is accessible by its name."""
        self.client.login(email='user2@gmail.com', password='test')
        response = self.client.get(reverse('accounts:confirm_email'))

        self.assertRedirects(response, reverse('accounts:security_dashboard'))

    def test_redirect_if_confirmed_email(self):
        """Test that if user's email is `confirmed`, he is redirected."""
        self.client.login(email='user1@gmail.com', password='test')  # user with a `confirmed` email
        response = self.client.get(reverse('accounts:confirm_email'))

        self.assertRedirects(response, reverse('accounts:settings_dashboard'))

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_sent_if_unconfirmed_email(self):
        """Test that verification email is sent, if user's email is `unconfirmed` yet."""
        self.client.login(email='user2@gmail.com', password='test')  # user with a `unconfirmed` email
        response = self.client.get(reverse('accounts:confirm_email'))

        # email has been sent
        self.assertEqual(len(mail.outbox), 1)

        self.assertRedirects(response, reverse('accounts:security_dashboard'))
