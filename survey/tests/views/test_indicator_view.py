from django.contrib.auth.models import User
from django.test import Client
from survey.forms.indicator import IndicatorForm
from survey.forms.filters import IndicatorFilterForm
from survey.models import QuestionModule, Batch, Indicator, Survey
from survey.tests.base_test import BaseTest


class IndicatorViewTest(BaseTest):
    def setUp(self):
        self.client = Client()
        self.module = QuestionModule.objects.create(name="Health")
        self.survey = Survey.objects.create(name="Health survey")
        self.batch = Batch.objects.create(name="Health", survey=self.survey)

        self.form_data = {'module': self.module.id,
                          'name': 'Health',
                          'description': 'some description',
                          'measure': '%',
                          'batch': self.batch.id,
                          'survey':self.survey.id}

        User.objects.create_user(username='useless', email='rajni@kant.com', password='I_Suck')
        raj = self.assign_permission_to(User.objects.create_user('Rajni', 'rajni@kant.com', 'I_Rock'),
                                        'can_view_batches')
        self.assign_permission_to(raj, 'can_view_investigators')
        self.client.login(username='Rajni', password='I_Rock')

    def test_get_new_indicator(self):
        response = self.client.get('/indicators/new/')
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('indicator/new.html', templates)
        self.assertIsNotNone(response.context['indicator_form'])
        self.assertIsInstance(response.context['indicator_form'], IndicatorForm)
        self.assertEqual(response.context['title'], "Add Indicator")
        self.assertEqual(response.context['button_label'], "Save")
        self.assertEqual(response.context['action'], "/indicators/new/")

    def test_post_indicator_creates_an_indicator_and_returns_success(self):
        data = self.form_data.copy()
        del data['survey']
        self.failIf(Indicator.objects.filter(**data))
        response = self.client.post('/indicators/new/', data=self.form_data)
        self.failUnless(Indicator.objects.filter(**data))
        self.assertRedirects(response, "/indicators/", 302, 200)
        success_message = "Indicator successfully created."
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_permission_for_question_modules(self):
        self.assert_restricted_permission_for('/indicators/')
        self.assert_restricted_permission_for('/indicators/new/')

    def test_get_indicator_index(self):
        another_form_data = self.form_data.copy()
        another_form_data['name'] = 'Education'
        another_form_data['module'] = self.module
        another_form_data['batch'] = self.batch
        del another_form_data['survey']

        education_indicator = Indicator.objects.create(**another_form_data)
        response = self.client.get('/indicators/')
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('indicator/index.html', templates)
        self.assertIsInstance(response.context['indicator_filter_form'], IndicatorFilterForm)
        self.assertIn(education_indicator, response.context['indicators'])

    def test_post_filter_indicators_by_survey(self):
        survey = Survey.objects.create(name='survey')
        batch_s = Batch.objects.create(name='batch survey', survey = survey)
        batch = Batch.objects.create(name='batch s')
        module = QuestionModule.objects.create(name="module")
        indicator_s = Indicator.objects.create(name='ITN', module=module, batch=batch_s)
        indicator = Indicator.objects.create(name='ITN1', module=module, batch=batch)

        response = self.client.post('/indicators/', data={'survey':survey.id, 'batch': 'All', 'module': 'All'})
        self.failUnlessEqual(response.status_code, 200)
        self.assertIsInstance(response.context['indicator_filter_form'], IndicatorFilterForm)
        self.assertEqual(1, len(response.context['indicators']))
        self.assertIn(indicator_s, response.context['indicators'])
        self.assertNotIn(indicator, response.context['indicators'])

    def test_post_filter_indicators_by_batch(self):
        survey = Survey.objects.create(name='survey')
        batch_s = Batch.objects.create(name='batch survey', survey = survey)
        batch_s2 = Batch.objects.create(name='batch survey 2', survey = survey)
        batch = Batch.objects.create(name='batch s')
        module = QuestionModule.objects.create(name="module")
        indicator_s = Indicator.objects.create(name='ITN', module=module, batch=batch_s)
        indicator_s2 = Indicator.objects.create(name='ITNs2', module=module, batch=batch_s2)
        indicator = Indicator.objects.create(name='ITN1', module=module, batch=batch)

        response = self.client.post('/indicators/', data={'survey':survey.id, 'batch': batch_s.id, 'module': 'All'})
        self.failUnlessEqual(response.status_code, 200)
        self.assertIsInstance(response.context['indicator_filter_form'], IndicatorFilterForm)
        self.assertIn(indicator_s, response.context['indicators'])
        self.assertEqual(1, len(response.context['indicators']))
        self.assertNotIn(indicator_s2, response.context['indicators'])
        self.assertNotIn(indicator, response.context['indicators'])

    def test_should_get_all_indicators_in_a_given_module_when_module_is_given(self):

        survey = Survey.objects.create(name='survey')
        batch_s = Batch.objects.create(name='batch survey', survey = survey)
        module = QuestionModule.objects.create(name="module")
        module_1 = QuestionModule.objects.create(name="module")

        indicator_1 = Indicator.objects.create(name="indicator name 1", description="rajni indicator 1", measure='Percentage',
                                         module=module, batch=batch_s)
        indicator_2 = Indicator.objects.create(name="indicator name 1", description="rajni indicator 1", measure='Percentage',
                                         module=module_1, batch=batch_s)

        response = self.client.post('/indicators/', data={'survey': 'All', 'batch': 'All', 'module': module.id})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context['indicators']))
        self.assertIn(indicator_1, response.context['indicators'])
        self.assertNotIn(indicator_2, response.context['indicators'])

    def test_should_get_all_indicators_in_a_given_module_when_module_and_batch_is_given(self):

        survey = Survey.objects.create(name='survey')
        batch_s = Batch.objects.create(name='batch survey', survey = survey)
        module = QuestionModule.objects.create(name="module")
        module_1 = QuestionModule.objects.create(name="module")

        indicator_1 = Indicator.objects.create(name="indicator name 1", description="rajni indicator 1", measure='Percentage',
                                         module=module, batch=batch_s)
        indicator_2 = Indicator.objects.create(name="indicator name 1", description="rajni indicator 1", measure='Percentage',
                                         module=module_1, batch=batch_s)

        response = self.client.post('/indicators/', data={'survey': 'All', 'batch': batch_s.id, 'module': module.id})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context['indicators']))
        self.assertIn(indicator_1, response.context['indicators'])
        self.assertNotIn(indicator_2, response.context['indicators'])

    def test_should_get_all_indicators_in_a_given_module_when_all_are_given(self):
        survey = Survey.objects.create(name='survey')
        batch_s = Batch.objects.create(name='batch survey', survey=survey)
        module = QuestionModule.objects.create(name="module")
        module_1 = QuestionModule.objects.create(name="module")

        indicator_1 = Indicator.objects.create(name="indicator name 1", description="rajni indicator 1", measure='Percentage',
                                         module=module, batch=batch_s)
        indicator_2 = Indicator.objects.create(name="indicator name 1", description="rajni indicator 1", measure='Percentage',
                                         module=module_1, batch=batch_s)

        response = self.client.post('/indicators/', data={'survey': survey.id, 'batch': batch_s.id, 'module': module.id})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context['indicators']))
        self.assertIn(indicator_1, response.context['indicators'])
        self.assertNotIn(indicator_2, response.context['indicators'])