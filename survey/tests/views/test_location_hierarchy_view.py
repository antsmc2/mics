from django.contrib.auth.models import User
from django.test import Client
from rapidsms.contrib.locations.models import LocationType, Location
from survey.forms.location_hierarchy import LocationHierarchyForm
from survey.tests.base_test import BaseTest


class LocationHierarchyTest(BaseTest):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='useless', email='rajni@kant.com', password='I_Suck')
        raj = self.assign_permission_to(User.objects.create_user('Rajni', 'rajni@kant.com', 'I_Rock'),
                                        'can_view_batches')
        self.assign_permission_to(raj, 'can_view_investigators')
        self.client.login(username='Rajni', password='I_Rock')
        country = LocationType.objects.create(name = 'Country', slug = 'country')
        self.uganda = Location.objects.create(name='Uganda', type = country)

    def test_should_render_success_code(self):
        response = self.client.get('/add_location_hierarchy/')
        self.assertEqual(200,response.status_code)

    def test_should_render_template(self):
        response = self.client.get('/add_location_hierarchy/')
        self.assertEqual(200,response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('location_hierarchy/new.html', templates)

    def test_should_render_form_instance(self):
        response = self.client.get('/add_location_hierarchy/')
        self.assertEqual(200,response.status_code)
        self.assertIsInstance(response.context['hierarchy_form'],LocationHierarchyForm)

    def test_should_render_context_data(self):
        response = self.client.get('/add_location_hierarchy/')
        self.assertEqual(200,response.status_code)
        self.assertEqual(response.context['button_label'],"Create Hierarchy")
        self.assertEqual(response.context['id'],"hierarchy-form")

    def test_should_redirect_to_home_page_after_post(self):
        levels_data = {'country': self.uganda.id, 'levels': ['Region']}
        response = self.client.post('/add_location_hierarchy/', data=levels_data)
        self.assertRedirects(response,'/',status_code=302,target_status_code=200,msg_prefix='')

    def test_should_save_location_type_after_post(self):
        levels_data = {'country': self.uganda.id, 'levels': ['Region']}
        response = self.client.post('/add_location_hierarchy/', data=levels_data)
        location_types = LocationType.objects.all()
        self.assertEqual(2, location_types.count())
        location_type_created = LocationType.objects.get(name='Region')
        self.failUnless(location_type_created)

    def test_should_save_location_types_if_multiple_levels_after_post(self):
        levels_data = {'country': self.uganda.id, 'levels': ['Region','District']}
        response = self.client.post('/add_location_hierarchy/', data=levels_data)
        location_types = LocationType.objects.all()
        self.assertEqual(3, location_types.count())
        location_type_created = LocationType.objects.get(name='Region')
        self.failUnless(location_type_created)
        location_type_created = LocationType.objects.get(name='District')
        self.failUnless(location_type_created)