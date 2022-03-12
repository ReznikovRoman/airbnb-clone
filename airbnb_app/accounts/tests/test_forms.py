import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from accounts.models import CustomUser, Profile

from ..forms import (
    AdminCustomUserChangeForm, ProfileDescriptionForm, ProfileForm, ProfileImageForm, SignUpForm, UserInfoForm,
    VerificationCodeForm,
)


class SignUpFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """`SignUpForm` uses correct model - `CustomUser`."""
        form = SignUpForm()
        self.assertEqual(form._meta.model, CustomUser)

    def test_form_correct_fields(self):
        """`SignUpForm` has correct fields."""
        form = SignUpForm()
        self.assertEqual(
            form._meta.fields,
            ('email', 'first_name', 'last_name', 'password1', 'password2'),
        )

    def test_email_field_params(self):
        """Email field has all required parameters."""
        form = SignUpForm()
        self.assertTrue(
            form.fields['email'].label is None or
            form.fields['email'].label == 'Email address',
        )


class AdminCustomUserChangeFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """`AdminCustomUserChangeForm` uses correct model - `CustomUser`."""
        form = AdminCustomUserChangeForm()
        self.assertEqual(form._meta.model, CustomUser)

    def test_form_correct_fields(self):
        """`AdminCustomUserChangeForm` has correct fields."""
        form = AdminCustomUserChangeForm()
        self.assertEqual(
            form._meta.fields,
            ('email', 'first_name', 'last_name', 'is_email_confirmed'),
        )


class UserInfoFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """`UserInfoForm` uses correct model - `CustomUser`."""
        form = UserInfoForm()
        self.assertEqual(form._meta.model, CustomUser)

    def test_form_correct_fields(self):
        """`UserInfoForm` has correct fields."""
        form = UserInfoForm()
        self.assertEqual(
            form._meta.fields,
            ('first_name', 'last_name', 'email'),
        )


class ProfileFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """`ProfileForm` uses correct model - `Profile`."""
        form = ProfileForm()
        self.assertEqual(form._meta.model, Profile)

    def test_form_correct_fields(self):
        """`ProfileForm` has correct fields."""
        form = ProfileForm()
        self.assertEqual(
            form._meta.fields,
            ('gender', 'date_of_birth', 'phone_number'),
        )

    def test_form_correct_widgets(self):
        """`ProfileForm` fields widgets are correct."""
        form = ProfileForm()
        self.assertIsInstance(form._meta.widgets.get('date_of_birth'), forms.DateInput)

    def test_clean_date_of_birth_date_in_the_future(self):
        """User cannot specify a `date_of_birth` in the future."""
        date = datetime.date.today() + datetime.timedelta(days=1)
        form = ProfileForm(data={'date_of_birth': date})

        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_clean_date_of_birth_underage(self):
        """User cannot specify a `date_of_birth` if he isn't mature."""
        date = datetime.date.today() - datetime.timedelta(days=365 * 18)
        form = ProfileForm(data={'date_of_birth': date})

        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_clean_date_of_birth_valid_age(self):
        """clean_date_of_birth() returns `date_of_birth` if a user is mature and `date_of_birth` is valid."""
        date = datetime.date.today() - datetime.timedelta(days=365 * 19)
        form = ProfileForm(data={'date_of_birth': date})

        self.assertTrue(form.is_valid())


class ProfileImageFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """`ProfileImageForm` uses correct model - `Profile`."""
        form = ProfileImageForm()
        self.assertEqual(form._meta.model, Profile)

    def test_form_correct_fields(self):
        """`ProfileImageForm` has correct fields."""
        form = ProfileImageForm()
        self.assertEqual(
            form._meta.fields,
            ('profile_image',),
        )

    def test_form_correct_widgets(self):
        """`ProfileImageForm` fields widgets are correct."""
        form = ProfileImageForm()
        self.assertIsInstance(form._meta.widgets.get('profile_image'), forms.FileInput)


class ProfileDescriptionFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """`ProfileDescriptionForm` uses correct model - `Profile`."""
        form = ProfileDescriptionForm()
        self.assertEqual(form._meta.model, Profile)

    def test_form_correct_fields(self):
        """`ProfileDescriptionForm` has correct fields."""
        form = ProfileDescriptionForm()
        self.assertEqual(
            form._meta.fields,
            ('description',),
        )


class VerificationCodeFormTests(SimpleTestCase):
    def test_digit_field_params(self):
        """`digit_*` field has all required parameters."""

        def is_digit_field_params_correct(digit_field: forms.CharField):
            self.assertEqual(digit_field.min_length, 1)
            self.assertEqual(digit_field.max_length, 1)
            self.assertIsInstance(digit_field.widget, forms.NumberInput)
            self.assertEqual(digit_field.label, '')

        form = VerificationCodeForm()

        digit_template = 'digit_'
        digit_range = range(1, 5)
        digits = [form.fields.get(f"{digit_template}{digit_index}") for digit_index in digit_range]

        for digit in digits:
            is_digit_field_params_correct(digit)

    def test_clean_digit_less_than_zero(self):
        """Digit cannot be less than zero."""
        form = VerificationCodeForm(
            data={'digit_1': '-1', 'digit_2': '2', 'digit_3': '3', 'digit_4': '4'},
        )

        self.assertFalse(form.is_valid())
        self.assertRaises(forms.ValidationError)

    def test_clean_digit_greater_than_nine(self):
        """Digit cannot be greater than nine."""
        form = VerificationCodeForm(
            data={'digit_1': '10', 'digit_2': '2', 'digit_3': '3', 'digit_4': '4'},
        )

        self.assertFalse(form.is_valid())
        self.assertRaises(forms.ValidationError)

    def test_clean_digit_valid_digit(self):
        """clean_digit_*() returns `digit_*` if digit is in range [0, 9]."""
        form = VerificationCodeForm(
            data={'digit_1': '1', 'digit_2': '2', 'digit_3': '3', 'digit_4': '4'},
        )

        self.assertTrue(form.is_valid())
