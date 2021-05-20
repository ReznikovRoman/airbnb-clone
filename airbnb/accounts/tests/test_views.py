import re

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse, reverse_lazy

from accounts.models import CustomUser
from .. import views
from ..forms import SignUpForm, CustomPasswordResetForm


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
