from rapidsms.contrib.locations.models import LocationType, Location
from survey.models.location_type_details import LocationTypeDetails
from survey.tests.base_test import BaseTest


class LocationTypeDetailsTest(BaseTest):
    def test_fields(self):
        location_type_details = LocationTypeDetails()
        fields = [str(item.attname) for item in location_type_details._meta.fields]
        self.assertEqual(9, len(fields))
        for field in ['id', 'created', 'modified', 'location_type_id', 'required', 'has_code', 'length_of_code',
                      'country_id', 'order']:
            self.assertIn(field, fields)

    def test_store(self):
        country = LocationType.objects.create(name='country', slug='country')
        location_type_details = LocationTypeDetails.objects.create(required=True, has_code=False, location_type=country,
                                                                   order=0)
        self.failUnless(location_type_details.id)

    def test_should_return_location_type_objects_ordered_by_order(self):
        country = LocationType.objects.create(name='country', slug='country')
        location_type_details = LocationTypeDetails.objects.create(required=True, has_code=False, location_type=country)
        district = LocationType.objects.create(name='district', slug='district')
        location_type_details_1 = LocationTypeDetails.objects.create(required=True, has_code=False,
                                                                     location_type=district)
        county = LocationType.objects.create(name='county', slug='county')
        location_type_details_1 = LocationTypeDetails.objects.create(required=True, has_code=False,
                                                                     location_type=county)
        ordered_types = LocationTypeDetails.get_ordered_types()
        self.assertEqual(country, ordered_types[0])
        self.assertEqual(district, ordered_types[1])
        self.assertEqual(county, ordered_types[2])

    def test_should_save_with_auto_incremented_order(self):
        country = LocationType.objects.create(name='country', slug='country')
        country_details = LocationTypeDetails.objects.create(required=True, has_code=False, location_type=country)
        self.assertEqual(1, country_details.order)
        district = LocationType.objects.create(name='district', slug='district')
        data = {
            'required': True,
            'has_code': False,
            'location_type': district,
        }
        location_type_details = LocationTypeDetails(**data)
        location_type_details.save()
        self.assertEqual(2, location_type_details.order)

    def test_shouldnot_update_order_if_editing(self):
        district = LocationType.objects.create(name='district', slug='district')
        detail = LocationTypeDetails.objects.create(required=True, has_code=False,
                                                                     location_type=district)

        detail2 = LocationTypeDetails.objects.create(required=False, has_code=True,
                                                                     location_type=district)

        self.assertEquals(1, detail.order)
        detail.has_code = True
        detail.save()
        self.assertEquals(1, detail.order)

    def test_should_return_the_country_in_use(self):
        self.assertIsNone(LocationTypeDetails.the_country())

        uganda = Location.objects.create(name="Uganda")
        a_type = LocationType.objects.create(name="country", slug="country")
        LocationTypeDetails.objects.create(location_type=a_type, country=uganda)

        self.assertEqual(uganda, LocationTypeDetails.the_country())