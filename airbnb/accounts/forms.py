from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Profile


class SignUpForm(UserCreationForm):
    """Form for signing up/creating new account."""
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Email address'


class AdminCustomUserChangeForm(UserChangeForm):
    """Form for editing CustomUser (used on the admin panel)."""
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')


class UserInfoForm(forms.ModelForm):
    """Form for editing user info."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    class Meta:
        model = Profile
        fields = ('gender', 'date_of_birth')
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


class ProfileDescriptionForm(forms.ModelForm):
    """Form for editing user description ('about me' section)."""
    class Meta:
        model = Profile
        fields = ('description',)
