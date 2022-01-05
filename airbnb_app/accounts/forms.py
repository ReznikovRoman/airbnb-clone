from typing import Union

from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import CustomUser, Profile
from .tasks import send_password_reset_code


class SignUpForm(UserCreationForm):
    """Form for signing up/creating new account."""

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Email address'


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form.

    Send emails using Celery.
    """

    def send_mail(
            self,
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name=None,
    ):
        context['user'] = context['user'].pk
        send_password_reset_code.delay(
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            context=context,
            from_email=from_email,
            to_email=to_email,
            html_email_template_name=html_email_template_name,
        )


class AdminCustomUserChangeForm(UserChangeForm):
    """Form for editing CustomUser (used on the admin panel)."""

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'is_email_confirmed')


class UserInfoForm(forms.ModelForm):
    """Form for editing user info."""

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    """Form for editing user profile."""

    class Meta:
        model = Profile
        fields = ('gender', 'date_of_birth', 'phone_number')
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select a date',
                    'type': 'date',
                },
            ),
        }

    def clean_date_of_birth(self):
        """Handles input of date_of_birth field.

        date of birth can't be in the future, Host must be at least 18 years old
        """
        date_of_birth = self.cleaned_data['date_of_birth']
        if date_of_birth:
            date_now = timezone.now().date()
            year_diff = (date_now.month, date_now.day) < (date_of_birth.month, date_of_birth.day)
            host_age = date_now.year - date_of_birth.year - year_diff
            if date_of_birth > date_now:
                raise ValidationError('Invalid date: date of birth in the future.', code='invalid')
            elif host_age < 18:
                raise ValidationError('Invalid date: You must be at least 18 years old.', code='underage')
        return date_of_birth


class ProfileImageForm(forms.ModelForm):
    """Form for uploading profile image."""

    class Meta:
        model = Profile
        fields = ('profile_image',)
        widgets = {
            'profile_image': forms.FileInput(),
        }


class ProfileDescriptionForm(forms.ModelForm):
    """Form for editing user description ('about me' section)."""

    class Meta:
        model = Profile
        fields = ('description',)


class VerificationCodeForm(forms.Form):
    """Form for entering a SMS verification code."""

    digit_1 = forms.CharField(
        min_length=1,
        max_length=1,
        widget=forms.NumberInput(
            attrs={'min': '0', 'max': '9', 'class': 'code', 'placeholder': '0'},
        ),
        label='',
    )
    digit_2 = forms.CharField(
        min_length=1,
        max_length=1,
        widget=forms.NumberInput(
            attrs={'min': '0', 'max': '9', 'class': 'code', 'placeholder': '0'},
        ),
        label='',
    )
    digit_3 = forms.CharField(
        min_length=1,
        max_length=1,
        widget=forms.NumberInput(
            attrs={'min': '0', 'max': '9', 'class': 'code', 'placeholder': '0'},
        ),
        label='',
    )
    digit_4 = forms.CharField(
        min_length=1,
        max_length=1,
        widget=forms.NumberInput(
            attrs={'min': '0', 'max': '9', 'class': 'code', 'placeholder': '0'},
        ),
        label='',
    )

    def clean_digit_1(self):
        return self._clean_digit(digit_index=1)

    def clean_digit_2(self):
        return self._clean_digit(digit_index=2)

    def clean_digit_3(self):
        return self._clean_digit(digit_index=3)

    def clean_digit_4(self):
        return self._clean_digit(digit_index=4)

    def _clean_digit(self, digit_index: Union[str, int], digit_template: str = 'digit_'):
        digit = f"{digit_template}{str(digit_index)}"
        data = self.cleaned_data.get(digit)

        if not 0 <= int(data) <= 9:
            raise ValidationError('Digit must be in range [0, 9].')

        return data
