from django import forms

from .models import Realty, RealtyTypeChoices


class RealtyTypeForm(forms.Form):
    """Form for selecting realty types."""
    realty_type = forms.MultipleChoiceField(
        choices=RealtyTypeChoices.choices,
        widget=forms.CheckboxSelectMultiple()
    )


class RealtyForm(forms.ModelForm):
    """Form for editing (creating or updating) a Realty object."""
    class Meta:
        model = Realty
        fields = ('name', 'realty_type', 'description',
                  'beds_count', 'max_guests_count', 'price_per_night')
