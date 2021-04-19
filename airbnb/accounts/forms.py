from django import forms
from django.utils import timezone
from django.template import loader
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm

from mailings.tasks import send_email_with_attachments
from .models import CustomUser, Profile


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

    Sends emails using Celery.
    """
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        html = loader.get_template(html_email_template_name)
        html_content = html.render(context)

        # launch celery task
        send_email_with_attachments.delay(
            subject=subject,
            body=body,
            email_to=[to_email],
            email_from=from_email,
            alternatives=[(html_content, 'text/html')]
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
                    'type': 'date'
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
            host_age = date_now.year - date_of_birth.year - ((date_now.month, date_now.day) <
                                                             (date_of_birth.month, date_of_birth.day))
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
        data = self.cleaned_data['digit_1']
        if not 0 <= int(data) <= 9:
            raise ValidationError('Digit must be in range [0, 9].')
        return data

    def clean_digit_2(self):
        data = self.cleaned_data['digit_2']
        if not 0 <= int(data) <= 9:
            raise ValidationError('Digit must be in range [0, 9].')
        return data

    def clean_digit_3(self):
        data = self.cleaned_data['digit_3']
        if not 0 <= int(data) <= 9:
            raise ValidationError('Digit must be in range [0, 9].')
        return data

    def clean_digit_4(self):
        data = self.cleaned_data['digit_4']
        if not 0 <= int(data) <= 9:
            raise ValidationError('Digit must be in range [0, 9].')
        return data
