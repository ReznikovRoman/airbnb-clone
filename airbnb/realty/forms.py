from django import forms

from .models import RealtyTypeChoices


class RealtyTypeForm(forms.Form):
    """Form for selecting realty types"""
    realty_type = forms.MultipleChoiceField(
        choices=RealtyTypeChoices.choices,
        widget=forms.CheckboxSelectMultiple()
    )
