from django.test import TestCase
from survey.forms.location_details import LocationDetailsForm


class LocationDetailsFormTest(TestCase):
    def test_should_know_the_fields(self):
        details_form = LocationDetailsForm()

        fields = ['required', 'has_code', 'code','levels']
        [self.assertIn(field, details_form.fields) for field in fields]

    def test_should_be_valid_if_all_fields_given(self):
        data={
            'levels': 'Region',
            'required':True,
            'has_code':True,
            'code': 'some_code'
        }

        details_form = LocationDetailsForm(data=data)
        self.assertTrue(details_form.is_valid())

    def test_should_be_invalid_if_levels_is_blank(self):
        data={
            'levels': '',
            'required':True,
            'has_code':True,
            'code': 'some_code'
        }

        details_form = LocationDetailsForm(data=data)
        self.assertFalse(details_form.is_valid())