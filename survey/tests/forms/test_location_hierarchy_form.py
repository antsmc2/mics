from django.template.defaultfilters import slugify
from django.test.testcases import TestCase
from rapidsms.contrib.locations.models import Location, LocationType
from survey.forms.location_hierarchy import LocationHierarchyForm


class LocationHierarchyFormTest(TestCase):
    def setUp(self):
        country = LocationType.objects.create(name='country',slug=slugify('country'))
        self.uganda = Location.objects.create(type=country, name='Uganda')

    def test_knows_the_fields_in_form(self):
        hierarchy_form = LocationHierarchyForm()

        fields = ['country']
        [self.assertIn(field, hierarchy_form.fields) for field in fields]

    def test_should_populate_countries_name(self):
        hierarchy_form = LocationHierarchyForm()

        field = 'country'
        all_countries = Location.objects.filter(type__name='country')
        country_choices = hierarchy_form.fields[field].choices

        [self.assertIn((country_option.id, country_option.name), country_choices) for country_option in all_countries]

    def test_should_populate_countries_name_case_insensitive(self):
        LocationType.objects.all().delete()
        Location.objects.all().delete()
        country_1 = LocationType.objects.create(name='Country',slug=slugify('Country'))
        some_country = Location.objects.create(type=country_1, name='some_country')

        field = 'country'
        hierarchy_form = LocationHierarchyForm()
        all_countries = Location.objects.filter(type__name='country')
        country_choices = hierarchy_form.fields[field].choices

        [self.assertIn((country_option.id, country_option.name), country_choices) for country_option in all_countries]
        self.assertIn((some_country.id, some_country.name), country_choices)