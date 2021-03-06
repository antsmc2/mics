from datetime import date
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from rapidsms.contrib.locations.models import Location, LocationType
from survey.forms.householdMember import HouseholdMemberForm
from survey.models.households import HouseholdMember, HouseholdHead, Household
from survey.models.backend import Backend
from survey.models.investigator import Investigator
from survey.tests.base_test import BaseTest


class HouseholdMemberViewsTest(BaseTest):
    def setUp(self):
        raj = User.objects.create_user('Rajni', 'rajni@kant.com', 'I_Rock')
        some_group = Group.objects.create(name='some group')
        auth_content = ContentType.objects.get_for_model(Permission)
        permission, out = Permission.objects.get_or_create(codename='can_view_households', content_type=auth_content)
        some_group.permissions.add(permission)
        some_group.user_set.add(raj)
        user_without_permission = User.objects.create_user(username='useless', email='rajni@kant.com', password='I_Suck')

        self.client = Client()
        self.client.login(username='Rajni', password='I_Rock')

        country = LocationType.objects.create(name="Country", slug="country")

        uganda = Location.objects.create(name="Uganda", type=country)
        investigator = Investigator.objects.create(name="inv1", location=uganda,
                                                   backend=Backend.objects.create(name='something'))
        self.household = Household.objects.create(investigator=investigator, uid=0)
        HouseholdHead.objects.create(household=self.household, surname="Test", first_name="User", date_of_birth="1980-09-01", male=True,
                                     occupation='Agricultural labor', level_of_education='Primary', resident_since_year=2013, resident_since_month=2)
        self.household_member = HouseholdMember.objects.create(surname='member1', date_of_birth=(date(2013, 8, 30)),
                                                               male=True,
                                                               household=self.household)

    def test_new_should_have_household_member_form_in_response_context_for_get(self):
        response = self.client.get('/households/%d/member/new/' % int(self.household.id))

        self.assertEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('household_member/new.html', templates)

        self.assertIsInstance(response.context['member_form'], HouseholdMemberForm)
        self.assertEqual(response.context['button_label'], 'Create')

    def test_new_should_redirect_on_post(self):
        form_data = {'surname': 'xyz',
                     'date_of_birth': date(1980, 05, 01),
                     'male': True
        }

        response = self.client.post('/households/%d/member/new/' % int(self.household.id), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url='/households/%d/'%(self.household.id), status_code=302, target_status_code=200, msg_prefix='')

    def test_new_should_create_new_member_on_post_who_belongs_to_household_selected(self):
        form_data = {'surname': 'xyz',
                     'date_of_birth': date(1980, 05, 01),
                     'male': True
        }

        response = self.client.post('/households/%d/member/new/' % int(self.household.id), data=form_data)
        self.assertEqual((HouseholdMember.objects.filter(householdhead=None)).count(), 2)
        success_message = 'Household member successfully created.'
        household_member = HouseholdMember.objects.get(surname=form_data['surname'])
        self.failUnless(household_member)
        self.assertEqual(household_member.household, self.household)
        self.assertTrue(success_message in response.cookies['messages'].value)

    def test_should_throw_error_if_a_member_is_being_created_for_does_not_exist_and_redirect_to_households_for_get(
            self):
        response = self.client.get('/households/%d/member/new/' % (int(self.household.id) + 1))

        error_message = "There are  no households currently registered  for this ID."

        self.assertEqual(response.status_code, 302)
        self.assertTrue(error_message in response.cookies['messages'].value)

    def test_should_show_error_if_being_created_for_household_that_does_not_exist_and_redirect_to_households_for_post(
            self):
        form_data = {'surname': 'xyz',
                     'date_of_birth': date(1980, 05, 01),
                     'male': True
        }

        response = self.client.post('/households/%d/member/new/' % (int(self.household.id) + 1), data=form_data)

        error_message = "There are  no households currently registered  for this ID."

        self.assertEqual(response.status_code, 302)
        self.assertTrue(error_message in response.cookies['messages'].value)

    def test_should_have_member_form_in_context(self):
        response = self.client.get(
            '/households/%d/member/%d/edit/' % (int(self.household.id), int(self.household_member.id)))
        self.assertEqual(response.status_code, 200)

        templates = [template.name for template in response.templates]
        self.assertIn('household_member/new.html', templates)

        self.assertIsInstance(response.context['member_form'], HouseholdMemberForm)
        self.assertEqual(response.context['button_label'], 'Save')

    def test_should_have_the_member_information_as_values_on_the_form(self):
        response = self.client.get(
            '/households/%d/member/%d/edit/' % (int(self.household.id), int(self.household_member.id)))

        member_form = response.context['member_form']

        self.assertEqual(member_form.instance.surname, self.household_member.surname)
        self.assertEqual(member_form.instance.date_of_birth, self.household_member.date_of_birth)
        self.assertTrue(member_form.instance.male)

    def test_should_update_member_information_on_post(self):
        form_data = {'surname': 'new_name',
                     'date_of_birth': date(1981, 06, 01),
                     'male': False
        }
        response = self.client.post(
            '/households/%d/member/%d/edit/' % (int(self.household.id), int(self.household_member.id)), data=form_data)

        member = HouseholdMember.objects.filter(surname=self.household_member.surname)
        self.failIf(member)

        updated_member = HouseholdMember.objects.get(id=self.household_member.id)
        self.assertEqual(updated_member.surname,form_data['surname'])
        self.assertEqual(updated_member.date_of_birth,form_data['date_of_birth'])
        self.assertFalse(updated_member.male)
        self.assertRedirects(response, expected_url='/households/%d/'%(self.household.id), status_code=302, target_status_code=200, msg_prefix='')

    def test_should_show_successfully_edited_on_post_if_valid_information(self):
        form_data = {'surname': 'new_name',
                     'date_of_birth': date(1981, 06, 01),
                     'male': False
        }

        response = self.client.post(
            '/households/%d/member/%d/edit/' % (int(self.household.id), int(self.household_member.id)), data=form_data)

        success_message = "Household member successfully edited."

        self.assertTrue(success_message in response.cookies['messages'].value)

    def test_restricted_permissions(self):
        self.assert_restricted_permission_for('/households/%d/member/new/' % int(self.household.id))
        self.assert_restricted_permission_for('/households/%d/member/%d/edit/' % (int(self.household.id), int(self.household_member.id)))        

    def test_should_delete_member_from_houshold(self):
        response = self.client.get(
            '/households/%d/member/%d/delete/' % (int(self.household.id), int(self.household_member.id)))

        self.assertRedirects(response, expected_url='/households/%d/'%(self.household.id), status_code=302, target_status_code=200, msg_prefix='')


        deleted_member = HouseholdMember.objects.filter(id=self.household_member.id)
        self.failIf(deleted_member)

        success_message = "Household member successfully deleted."

        self.assertTrue(success_message in response.cookies['messages'].value)