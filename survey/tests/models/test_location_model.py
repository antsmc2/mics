# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.test import TestCase
from rapidsms.contrib.locations.models import LocationType, Location
from survey.models import LocationAutoComplete


class LocationTest(TestCase):
    def test_store(self):
        country = LocationType.objects.create(name='Country', slug='country')
        district = LocationType.objects.create(name='District', slug='district')
        county = LocationType.objects.create(name='County', slug='county')
        subcounty = LocationType.objects.create(name='Subcounty', slug='subcounty')
        parish = LocationType.objects.create(name='Parish', slug='parish')
        village = LocationType.objects.create(name='Village', slug='village')
        uganda = Location.objects.create(name="Uganda", type=country)
        kampala = Location.objects.create(name="Kampala", type=district, tree_parent=uganda)
        some_county = Location.objects.create(name="County", type=county, tree_parent=kampala)
        some_sub_county = Location.objects.create(name="Subcounty", type=subcounty, tree_parent=some_county)
        some_parish = Location.objects.create(name="Parish", type=parish, tree_parent=some_sub_county)
        some_village = Location.objects.create(name="Village", type=village, tree_parent=some_parish)

        u = Location.objects.get(type__name='Country', name='Uganda')
        report_locations = u.get_descendants(include_self=True).all()
        self.assertEqual(len(report_locations), 6)
        self.assertIn(uganda, report_locations)
        self.assertIn(kampala, report_locations)
        self.assertIn(some_county, report_locations)
        self.assertIn(some_sub_county, report_locations)
        self.assertIn(some_parish, report_locations)
        self.assertIn(some_village, report_locations)


class LocationAutoCompleteTest(TestCase):
    def test_store(self):
        self.assertEqual(len(LocationAutoComplete.objects.all()), 0)
        uganda = Location.objects.create(name="Uganda")
        self.assertEqual(len(LocationAutoComplete.objects.all()), 1)
        self.assertEqual(uganda.auto_complete_text(), "Uganda")
        self.assertEqual(LocationAutoComplete.objects.all()[0].text, "Uganda")

        kampala = Location.objects.create(name="Kampala", tree_parent=uganda)
        self.assertEqual(kampala.auto_complete_text(), "Uganda > Kampala")

        soroti = Location.objects.create(name="Soroti", tree_parent=kampala)
        self.assertEqual(soroti.auto_complete_text(), "Uganda > Kampala > Soroti")

        kampala.name = "Kampala Changed"
        kampala.save()
        self.assertEqual(kampala.auto_complete_text(), "Uganda > Kampala Changed")

        soroti = Location.objects.get(name="Soroti")
        self.assertEqual(soroti.auto_complete_text(), "Uganda > Kampala Changed > Soroti")