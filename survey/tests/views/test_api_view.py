from django.test import TestCase
from django.test.client import Client
from rapidsms.contrib.locations.models import Location
from survey.models import EnumerationArea
from survey.models.batch import Batch
from survey.models.investigator import Investigator


class TestApi(TestCase):
    def setUp(self):
        self.client = Client()
        self.location = Location.objects.create(name="Kampala")
        batch = Batch.objects.create(name="Batch", order = 1)
        batch.open_for_location(self.location)

    def test_create_investigator(self):
        self.assertEquals(Investigator.objects.count(), 0)
        mobile_number = '123456789'
        response = self.client.get("/api/create_investigator", data={'mobile_number': mobile_number})
        self.failUnlessEqual(response.status_code, 200)
        investigator = Investigator.objects.all()[0]
        self.assertEquals(investigator.households.count(), 1)
        self.assertEquals(investigator.location, self.location)

    def test_delete_investigator(self):
        self.ea = EnumerationArea.objects.create(name="EA2")
        self.ea.locations.add(self.location)

        investigator = Investigator.objects.create(name="investigator name", mobile_number="123456789", ea=self.ea)
        self.assertEquals(Investigator.objects.count(), 1)
        response = self.client.get("/api/delete_investigator", data={'mobile_number': investigator.mobile_number})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(Investigator.objects.count(), 0)