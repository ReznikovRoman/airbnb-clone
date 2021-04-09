from django import forms
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
        fields = ('email', 'first_name', 'last_name')


class ProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    class Meta:
        model = Profile
        fields = ('profile_image', 'gender', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select a date',
                    'type': 'date'
                },
            ),
        }
