# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from time import sleep
from survey.features.page_objects.base import PageObject
from survey.investigator_configs import COUNTRY_PHONE_CODE
from rapidsms.contrib.locations.models import Location
from lettuce.django import django_url



class NewInvestigatorPage(PageObject):
    url = "/investigators/new"

    def valid_page(self):
        fields = ['name', 'mobile_number', 'confirm_mobile_number', 'male', 'age', 'backend']
        for field in fields:
            assert self.browser.is_element_present_by_name(field)
        assert self.browser.find_by_css("span.add-on")[0].text == COUNTRY_PHONE_CODE

    def get_investigator_values(self):
        return self.values

    def fill_valid_values(self):
        self.browser.find_by_id("location-value").value = Location.objects.create(name="Uganda").id
        self.values = {
            'name': self.random_text('Investigator Name'),
            'mobile_number': "987654321",
            'confirm_mobile_number': "987654321",
            'male': 't',
            'age': '25',
            'level_of_education': 'Primary',
            'language': 'Luo',
        }
        self.browser.fill_form(self.values)
        kampala = Location.objects.get(name="Kampala")
        kampala_county = Location.objects.get(name="Kampala County")
        script = '$("#location-district").val(%s);$("#location-district").trigger("liszt:updated").chosen().change()' % kampala.id
        self.browser.execute_script(script)
        sleep(3)
        script = '$("#location-county").val(%s);$("#location-county").trigger("liszt:updated").chosen().change()' % kampala_county.id
        self.browser.execute_script(script)

    def submit(self):
        self.browser.find_by_css("form button").first.click()


class InvestigatorsListPage(PageObject):
    url = '/investigators/'

    def validate_fields(self):
        assert self.browser.is_text_present('Investigators List')
        assert self.browser.is_text_present('Name')
        assert self.browser.is_text_present('Mobile Number')
        assert self.browser.is_text_present('Action')

    def validate_pagination(self):
        self.browser.click_link_by_text("2")

    def validate_presence_of_investigator(self, values):
        assert self.browser.is_text_present(values['name'])
        assert self.browser.is_text_present(values['mobile_number'])

    def no_registered_invesitgators(self):
        assert self.browser.is_text_present("There are no investigators currently registered for this location.")

    def visit_investigator(self, investigator):
        self.browser.click_link_by_text(investigator.name)


class FilteredInvestigatorsListPage(InvestigatorsListPage):
    def __init__(self, browser, location_id):
        self.browser = browser
        self.url = '/investigators/?location=' + str(location_id)

    def no_registered_invesitgators(self):
        assert self.browser.is_text_present("There are no investigators currently registered for this county.")


class EditInvestigatorPage(PageObject):
    def __init__(self, browser, investigator):
        self.browser = browser
        self.investigator = investigator
        self.url = '/investigators/' + str(investigator.id) + '/edit/'

    def validate_edit_investigator_url(self):
        assert self.browser.url == django_url(self.url)

    def change_name_of_investigator(self):
        self.values = {
            'name': 'Updated Name',
            'mobile_number': self.investigator.mobile_number,
            'confirm_mobile_number': self.investigator.mobile_number,
            'male': self.investigator.male,
            'age': self.investigator.age,
            'level_of_education': self.investigator.level_of_education,
            'language': self.investigator.language,
            'location': self.investigator.location,
            }
        self.browser.fill_form(self.values)

    def submit(self):
        self.browser.find_by_css("form button").first.click()


    def assert_user_saved_sucessfully(self):
        self.is_text_present("User successfully edited.")


class InvestigatorDetailsPage(PageObject):
    def __init__(self, browser, investigator):
        self.browser = browser
        self.investigator = investigator
        self.url = '/investigators/' + str(investigator.id) + '/'

    def validate_page_content(self):
        details = {
            'Name': self.investigator.name,
            'Mobile Number': self.investigator.mobile_number,
            'Age': str(self.investigator.age),
            'Sex': 'Male' if self.investigator.male else 'Female',
            'Highest Level of Education': self.investigator.level_of_education,
            'Preferred Language of Communication': self.investigator.language,
            'Country': 'Uganda',
            'City': 'Kampala',
        }
        for label, text in details.items():
            self.is_text_present(label)
            self.is_text_present(text)

    def validate_navigation_links(self):
        assert self.browser.find_link_by_text(' Back')
        assert self.browser.find_link_by_text(' Actions')

    def validate_back_link(self):
        self.browser.find_link_by_href(django_url(InvestigatorsListPage.url))

    def validate_detail_page_url(self):
        assert self.browser.url == django_url(self.url)

    def validate_successful_edited_message(self):
        self.is_text_present("Investigator successfully edited.")