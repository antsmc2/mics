# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
from django.core.cache import cache
from survey.ussd.base import USSDBase


class USSD(USSDBase):

    def __init__(self, investigator, request):
        self.investigator = investigator
        self.request = request.dict()
        self.action = self.ACTIONS['REQUEST']
        self.responseString = ""
        self.household = None
        self.household_member = None
        self.is_registering_household = True
        self.question = None
        self.set_session()
        self.set_household()
        self.set_household_member()
        self.set_current_member_is_done()
        self.set_is_resuming_survey()
        self.clean_investigator_input()

    def set_household(self):
        household = self.get_from_session('HOUSEHOLD')
        if household:
            self.household = household

    def set_household_member(self):
        household_member = self.get_from_session('HOUSEHOLD_MEMBER')

        if household_member:
            self.household_member = household_member


    def set_current_member_is_done(self):
        if self.household_member:
            self.current_member_is_done = self.household_member.survey_completed()

    def set_is_resuming_survey(self):
        try:
            cache_resuming_session = self.get_from_session('IS_RESUMING')
            self.is_resuming_survey = cache_resuming_session
        except:
            pass

    def set_session(self):
        self.session_string = "SESSION-%s-%s" % (self.request['transactionId'], self.__class__.__name__)
        if not cache.get(self.session_string):
            cache.set(self.session_string, self.DEFAULT_SESSION_VARIABLES)

    def get_from_session(self, key):
        return cache.get(self.session_string)[key]

    def set_in_session(self, key, value):
        session = cache.get(self.session_string)
        session[key] = value
        cache.set(self.session_string, session)

    def is_pagination_option(self, answer):
        return answer in getattr(settings, 'USSD_PAGINATION', None).values()

    def is_pagination(self, question, answer):
        pagination = False
        if question.is_multichoice():
            pagination = self.is_pagination_option(answer)
        if not pagination:
            self.set_in_session('PAGE', self.DEFAULT_SESSION_VARIABLES['PAGE'])
        return pagination

    def set_current_page(self, answer):
        current_page = self.get_from_session('PAGE')
        if answer == getattr(settings, 'USSD_PAGINATION', None).get('PREVIOUS'):
            current_page -= 1
        elif answer == getattr(settings, 'USSD_PAGINATION', None).get('NEXT'):
            current_page += 1
        self.set_in_session('PAGE', current_page)

    def question_present_in_cache(self, label):
        return self.question in self.investigator.get_from_cache(label)

    def reanswerable_question(self):
        return self.question_present_in_cache('REANSWER')

    def invalid_answered_question(self):
        return self.question_present_in_cache('INVALID_ANSWER')

    def get_household_list(self):
        page = self.get_from_session('PAGE')
        self.responseString += "%s\n%s" % (self.MESSAGES['HOUSEHOLD_LIST'], self.investigator.households_list(page,registered=False))

    def clean_investigator_input(self):
        if self.is_new_request():
            self.request['ussdRequestString'] = ''

    def select_household(self, answer):
        try:
            answer = int(answer)
            self.household = self.investigator.all_households()[answer - 1]
            self.set_in_session('HOUSEHOLD', self.household)
        except (ValueError, IndexError) as e:
            self.responseString += "INVALID SELECTION: "