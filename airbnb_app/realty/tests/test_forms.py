from django.forms import CheckboxSelectMultiple, FileInput, Textarea
from django.test import SimpleTestCase

from ..constants import MAX_REALTY_IMAGES_COUNT
from ..forms import (
    REALTY_FORM_WIDGETS, RealtyDescriptionForm, RealtyForm, RealtyGeneralInfoForm, RealtyImageForm, RealtyImageFormSet,
    RealtyTypeForm,
)
from ..models import Realty, RealtyImage, RealtyTypeChoices


class RealtyTypeFormTests(SimpleTestCase):
    def test_realty_type_field_params(self):
        """Test that `realty_type` field has all required parameters."""
        form = RealtyTypeForm()
        realty_type_field = form.fields['realty_type']

        self.assertEqual(realty_type_field.choices, RealtyTypeChoices.choices)
        self.assertIsInstance(realty_type_field.widget, CheckboxSelectMultiple)


class RealtyFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """Test that ModelForm uses a correct model."""
        form = RealtyForm()
        self.assertEqual(form._meta.model, Realty)

    def test_form_correct_fields(self):
        """Test that ModelForm has correct fields."""
        form = RealtyForm()
        self.assertTupleEqual(
            form._meta.fields,
            ('name', 'realty_type', 'beds_count', 'max_guests_count', 'price_per_night', 'amenities', 'description'),
        )

    def test_form_correct_widgets(self):
        """Test that ModelForm has correct widgets."""
        form = RealtyForm()
        self.assertDictEqual(
            form._meta.widgets,
            REALTY_FORM_WIDGETS,
        )


class RealtyImageFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """Test that ModelForm uses a correct model."""
        form = RealtyImageForm()
        self.assertEqual(form._meta.model, RealtyImage)

    def test_form_correct_fields(self):
        """Test that ModelForm has correct fields."""
        form = RealtyImageForm()
        self.assertTupleEqual(
            form._meta.fields,
            ('image',),
        )

    def test_form_correct_widgets(self):
        """Test that ModelForm has correct widgets."""
        form = RealtyImageForm()
        self.assertIsInstance(form._meta.widgets['image'], FileInput)

    def test_image_field_params(self):
        """Test that `image` field has all required parameters."""
        form = RealtyImageForm()
        image_field = form.fields['image']
        self.assertEqual(image_field.label, 'Image')


class RealtyGeneralInfoFormTests(SimpleTestCase):
    def test_form_correct_model(self):
        """Test that ModelForm uses a correct model."""
        form = RealtyGeneralInfoForm()
        self.assertEqual(form._meta.model, Realty)

    def test_form_correct_fields(self):
        """Test that ModelForm has correct fields."""
        form = RealtyGeneralInfoForm()
        self.assertTupleEqual(
            form._meta.fields,
            ('name', 'realty_type', 'beds_count', 'max_guests_count', 'price_per_night', 'amenities'),
        )

    def test_form_correct_widgets(self):
        """Test that ModelForm has correct widgets."""
        form = RealtyGeneralInfoForm()
        self.assertDictEqual(
            form._meta.widgets,
            REALTY_FORM_WIDGETS,
        )


class RealtyDescriptionFormTests(SimpleTestCase):
    def test_description_field_params(self):
        """Test that `description` field has all required parameters."""
        form = RealtyDescriptionForm()
        description_field = form.fields['description']

        self.assertEqual(description_field.label, 'Describe your realty')
        self.assertIsInstance(description_field.widget, Textarea)


class RealtyImageFormSetTests(SimpleTestCase):
    def test_formset_correct_model(self):
        """Test that Model Formset has a correct model."""
        form = RealtyImageFormSet()
        self.assertEqual(form.model, RealtyImage)

    def test_formset_params(self):
        """Test that Model Formset has all required parameters."""
        form = RealtyImageFormSet()

        self.assertFalse(form.can_delete)
        self.assertEqual(form.max_num, MAX_REALTY_IMAGES_COUNT)
        self.assertTrue(form.validate_max)
        self.assertEqual(form.extra, MAX_REALTY_IMAGES_COUNT)
