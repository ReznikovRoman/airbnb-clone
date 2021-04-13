from django import forms

from .models import Subscriber


class SubscriberEmailForm(forms.ModelForm):
    """Form for creating new Subscriber with the given email."""
    class Meta:
        model = Subscriber
        fields = ('email',)
