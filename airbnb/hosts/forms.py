from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import RealtyHost


# TODO: complete Host forms
# TODO: Fields from custom user model (AbstractUser, another milestone)


class UserEditForm(forms.ModelForm):
    """Temporary form for updating User's details"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class HostDetailsForm(forms.ModelForm):
    """Temporary Host details form."""
    user = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = RealtyHost
        fields = ('user', 'description', 'date_of_birth')
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


RealtyHostInlineFormSet = forms.inlineformset_factory(
    User,
    RealtyHost,
    form=HostDetailsForm,
    extra=1,
    max_num=1,
    validate_max=1,
    can_delete=False,
)
