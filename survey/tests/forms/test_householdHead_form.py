from datetime import datetime, date

from django.test import TestCase

from survey.forms.householdHead import *
from survey.models.households import HouseholdHead, Household


class MockDate(datetime):
    @classmethod
    def now(cls):
        return cls(datetime.now().year, 1, 1)


class HouseholdHeadFormTest(TestCase):
    def setUp(self):
        self.form_data = {
            'surname': 'household',
            'first_name': 'bla',
            'male': 't',
            'date_of_birth': date(2013, 05, 01),
            'level_of_education': 'Primary',
            'occupation': 'Brewing',
            'resident_since_year': '2013',
            'resident_since_month': '5',
            'time_measure': 'Years',
        }

    def test_valid(self):
        hHead_form = HouseholdHeadForm(self.form_data)
        self.assertTrue(hHead_form.is_valid())
        household = Household.objects.create(uid=1)
        hHead_form.instance.household = household
        hHead = hHead_form.save()
        self.failUnless(hHead.id)
        hHead_retrieved = HouseholdHead.objects.get(household=household)
        self.assertEqual(hHead_retrieved, hHead)

    def test_required_fields(self):
        data = self.form_data
        del data['date_of_birth']
        del data['surname']

        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = "This field is required."
        self.assertEquals(hHead_form.errors['date_of_birth'], [message])
        self.assertEquals(hHead_form.errors['surname'], [message])

    def test_resident_since_year(self):
        data = self.form_data

        data['resident_since_year'] = 1929
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = "Ensure this value is greater than or equal to 1930."
        self.assertEquals(hHead_form.errors['resident_since_year'], [message])

        data['resident_since_year'] = 2101
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = "Ensure this value is less than or equal to 2100."
        self.assertEquals(hHead_form.errors['resident_since_year'], [message])

        data['resident_since_year'] = 'not a number'
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = 'Enter a whole number.'
        self.assertEquals(hHead_form.errors['resident_since_year'], [message])

        data['resident_since'] = None
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = 'Enter a whole number.'
        self.assertEquals(hHead_form.errors['resident_since_year'], [message])

    def test_resident_since_month(self):
        data = self.form_data

        data['resident_since_month'] = -1
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = "Select a valid choice. -1 is not one of the available choices."
        self.assertEquals(hHead_form.errors['resident_since_month'], [message])

        data['resident_since_month'] = 13
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = "Select a valid choice. 13 is not one of the available choices."
        self.assertEquals(hHead_form.errors['resident_since_month'], [message])

        data['resident_since_month'] = 'not a number'
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = 'Select a valid choice. not a number is not one of the available choices.'
        self.assertEquals(hHead_form.errors['resident_since_month'], [message])

        data['resident_month'] = None
        hHead_form = HouseholdHeadForm(data)
        self.assertFalse(hHead_form.is_valid())
        message = 'Select a valid choice. not a number is not one of the available choices.'
        self.assertEquals(hHead_form.errors['resident_since_month'], [message])

    def test_resident_since_month_choices(self):
        month_choices = {'selected_text': '', 'selected_value': ''}
        months = [{'value': 1, 'text': 'January'},
                  {'value': 2, 'text': 'February'},
                  {'value': 3, 'text': 'March'},
                  {'value': 4, 'text': 'April'},
                  {'value': 5, 'text': 'May'},
                  {'value': 6, 'text': 'June'},
                  {'value': 7, 'text': 'July'},
                  {'value': 8, 'text': 'August'},
                  {'value': 9, 'text': 'September'},
                  {'value': 10, 'text': 'October'},
                  {'value': 11, 'text': 'November'},
                  {'value': 12, 'text': 'December'}, ]
        month_choices = HouseholdHeadForm.resident_since_month_choices(month_choices)

        self.assertEquals(months, month_choices['choices'])

    def test_resident_since_year_choices(self):
        year_choices = {'selected_text': '', 'selected_value': ''}
        datetime = MockDate

        self.assertEqual(MockDate.now(), datetime(datetime.now().year, 1, 1))

        years = list(xrange(datetime.now().year - 60, datetime.now().year + 1, 1))
        years.reverse()
        year_choices = HouseholdHeadForm.resident_since_year_choices(year_choices)
        self.assertEquals(years, year_choices['choices'])
