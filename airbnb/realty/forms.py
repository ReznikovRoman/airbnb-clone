from django import forms

from .models import Realty, RealtyImage, RealtyTypeChoices
from .constants import (MAX_REALTY_IMAGES_COUNT, MAX_BEDS_COUNT, MAX_GUESTS_COUNT)


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
                  'beds_count', 'max_guests_count', 'price_per_night',
                  'amenities')
        widgets = {
            'amenities': forms.CheckboxSelectMultiple(),
            'beds_count': forms.TextInput(attrs={
                'type': 'number',
                'min': '1',
                'max': str(MAX_BEDS_COUNT),
                'value': '1',
                'class': 'input-number--custom-field',
            }),
            'max_guests_count': forms.TextInput(attrs={
                'type': 'number',
                'min': '1',
                'max': str(MAX_GUESTS_COUNT),
                'value': '1',
                'class': 'input-number--custom-field',
            }),
            'price_per_night': forms.TextInput(attrs={
                'type': 'number',
                'min': 1,
            }),
        }


class RealtyImageForm(forms.ModelForm):
    """Form for creating RealtyImages."""
    class Meta:
        model = RealtyImage
        fields = ('image',)
        widgets = {
            'image': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super(RealtyImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = 'Image'


RealtyImageFormSet = forms.modelformset_factory(
    RealtyImage,
    form=RealtyImageForm,
    can_delete=False,
    max_num=MAX_REALTY_IMAGES_COUNT,
    validate_max=MAX_REALTY_IMAGES_COUNT,
    extra=MAX_REALTY_IMAGES_COUNT,
)
