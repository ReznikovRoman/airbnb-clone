from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    """Form for editing (creating or updating) an Address object."""
    class Meta:
        model = Address
        fields = ('country', 'city', 'street')
