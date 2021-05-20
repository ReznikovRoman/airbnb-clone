from django.core import mail
from django.test import TestCase, override_settings
from django.http import HttpResponse, HttpRequest
from django.urls import reverse

from accounts.models import CustomUser
from ..views import SignUpView
from ..forms import SignUpForm


class SignUpViewTests(TestCase):
    def setUp(self) -> None:
        CustomUser.objects.create_user(
            email='user1@gmail.com',
            first_name='John',
            last_name='Doe',
            password='test'
        )

    def test_view_correct_params(self):
        """Test that view has correct attributes."""
        self.assertEqual(SignUpView.form_class, SignUpForm)
        self.assertEqual(SignUpView.template_name, 'accounts/registration/signup.html')

    def test_view_url_accessible_by_name(self):
        """Test that url is accessible by its name (`reverse url`)."""
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
