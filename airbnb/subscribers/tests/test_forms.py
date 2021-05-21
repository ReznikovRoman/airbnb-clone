from django.test import SimpleTestCase

from ..forms import SubscriberEmailForm
from ..models import Subscriber


class SubscriberEmailFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """Test that ModelForm uses correct model."""
        form = SubscriberEmailForm()
        self.assertEqual(form._meta.model, Subscriber)

    def test_form_correct_fields(self):
        """Test that ModelForm has correct fields."""
        form = SubscriberEmailForm()
        self.assertEqual(form._meta.fields, ('email',))
