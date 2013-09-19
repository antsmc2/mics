from django.core.urlresolvers import reverse
from survey.features.page_objects.base import PageObject


class GroupConditionListPage(PageObject):
    url = '/conditions/'

    def validate_fields(self):
        self.validate_fields_present(["Groups Condition List", "Condition", "Attribute", "Value"])


class GroupsListingPage(PageObject):
    url = '/groups/'

    def validate_fields(self):
        self.validate_fields_present(["Groups List", "Order", "Group name", "Actions"])


class AddConditionPage(PageObject):
    url = "/conditions/new/"

class AddGroupPage(PageObject):
    url = '/groups/new/'


class GroupConditionModalPage(PageObject):
    url = ''

    def validate_contents(self):
        self.validate_fields_present(["Value", "Attribute", "Condition", "New Condition"])

    def validate_latest_condition(self, condition):
        self.browser.find_by_value("%s > %s > %s" % (condition.attribute, condition.condition, condition.value))

class GroupDetailsPage(PageObject):

    def __init__(self, browser, group_id):
        self.browser = browser
        self.url = '/groups/' + str(group_id)