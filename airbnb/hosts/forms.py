from django import forms

from .models import RealtyHost

# TODO: complete Host forms


class HostDetailsForm(forms.ModelForm):
    """Temporary Host details form for issue-4.2"""
    class Meta:
        model = RealtyHost
        fields = ('description', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select a date',
                    'type': 'date'
                },
            ),
        }
