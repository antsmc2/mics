import json
from django.test.client import Client
from django.contrib.auth.models import User
from mock import patch
from rapidsms.contrib.locations.models import Location
from survey.forms.logic import LogicForm
from survey.forms.filters import QuestionFilterForm
from survey.models import AnswerRule, QuestionModule, BatchQuestionOrder
from survey.models.batch import Batch
from survey.models.question import Question, QuestionOption

from survey.tests.base_test import BaseTest
from survey.forms.question import QuestionForm
from survey.forms.filters import MAX_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE
from survey.models.householdgroups import HouseholdMemberGroup
from survey.views.questions import _rule_exists, _get_questions_based_on_filter


class QuestionsViews(BaseTest):
    def setUp(self):
        self.client = Client()
        user_without_permission = User.objects.create_user(username='useless', email='rajni@kant.com',
                                                           password='I_Suck')
        raj = self.assign_permission_to(User.objects.create_user('Rajni', 'rajni@kant.com', 'I_Rock'),
                                        'can_view_batches')
        self.client.login(username='Rajni', password='I_Rock')
        self.household_member_group = HouseholdMemberGroup.objects.create(name='Age 4-5', order=1)
        self.module = QuestionModule.objects.create(name="Education")

        self.batch = Batch.objects.create(order=1, name="Batch A")
        self.question_1 = Question.objects.create(text="How many members are there in this household?",
                                                  answer_type=Question.NUMBER, order=1,
                                                  module=self.module, identifier='QQ1')
        self.question_2 = Question.objects.create(text="How many of them are male?",
                                                  answer_type=Question.NUMBER, order=2,
                                                  module=self.module, identifier='QQ2')
        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question_1, order=1)
        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question_2, order=2)

        self.question_1.batches.add(self.batch)
        self.question_2.batches.add(self.batch)

        self.form_data={
            'groups':"All",
            'modules':"All",
            'question_types':"All",
            'number_of_questions_per_page':50
        }

    def test_get_questions_based_on_filter_should_return_all_questions_if_batch_is_none_and_all_other_keys_are_all_or_none(
            self):
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.NUMBER, order=1,
                                             module=QuestionModule.objects.create(name="Economics"))

        params = {'group__id': 'All', 'module__id': 'All', 'answer_type': 'All'}

        questions = _get_questions_based_on_filter(None, params)

        all_questions = [self.question_1, self.question_2, question_3]

        [self.assertIn(question, questions) for question in all_questions]

    def test_get_questions_based_on_filter_should_return_module_specific_questions_if_batch_is_none_and_module_is_specific(
            self):
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.NUMBER, order=1,
                                             module=QuestionModule.objects.create(name="Economics"), identifier='Q3')

        params = {'group__id': 'All', 'module__id': str(self.module.id), 'answer_type': 'All'}

        questions = _get_questions_based_on_filter(None, params)

        all_questions = [self.question_1, self.question_2]

        [self.assertIn(question, questions) for question in all_questions]
        self.assertNotIn(question_3, questions)

    def test_get_questions_based_on_filter_should_return_group_specific_questions_if_batch_is_none_and_group_is_specific(
            self):
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.NUMBER, order=1,
                                             module=QuestionModule.objects.create(name="Economics"),
                                             group=self.household_member_group, identifier='Q3')

        params = {'group__id': str(self.household_member_group.id), 'module__id': 'All', 'answer_type': 'All'}

        questions = _get_questions_based_on_filter(None, params)

        all_questions = [self.question_1, self.question_2]

        [self.assertNotIn(question, questions) for question in all_questions]
        self.assertIn(question_3, questions)

    def test_get_questions_based_on_filter_should_return_answer_type_specific_questions_if_batch_is_none_and_answer_type_is_specific(
            self):
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.MULTICHOICE, order=1,
                                             module=QuestionModule.objects.create(name="Economics"),
                                             group=self.household_member_group, identifier='Q3')

        params = {'group__id': 'All', 'module__id': 'All', 'answer_type': Question.NUMBER}

        questions = _get_questions_based_on_filter(None, params)

        all_questions = [self.question_1, self.question_2]

        [self.assertIn(question, questions) for question in all_questions]
        self.assertNotIn(question_3, questions)

    def test_get_questions_based_on_filter_should_specific_questions_if_where_batch_is_specific_and_the_other_conditions_are_specific(
            self):
        new_module = QuestionModule.objects.create(name="Economics")
        new_batch = Batch.objects.create(name="New Batch")
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.MULTICHOICE, order=1,
                                             module=new_module, group=self.household_member_group, identifier='Q3')

        question_4 = Question.objects.create(text="How many members are there in this household again?",
                                             answer_type=Question.MULTICHOICE, order=3,
                                             module=new_module, group=self.household_member_group, identifier='Q4')
        question_3.batches.add(new_batch)
        BatchQuestionOrder.objects.create(batch=new_batch, question=question_3, order=1)

        params = {'group__id': str(self.household_member_group.id), 'module__id': str(new_module.id),
                  'answer_type': Question.MULTICHOICE}

        questions = _get_questions_based_on_filter(new_batch.id, params)

        all_questions = [self.question_1, self.question_2, question_4]

        [self.assertNotIn(question, questions) for question in all_questions]
        self.assertIn(question_3, questions)

    def test_get_questions_based_on_filter_should_specific_questions_if_where_batch_is_none_and_the_other_conditions_are_specific(
            self):
        new_module = QuestionModule.objects.create(name="Economics")
        new_batch = Batch.objects.create(name="New Batch")
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.MULTICHOICE, order=1,
                                             module=new_module, group=self.household_member_group, identifier='Q3')

        question_4 = Question.objects.create(text="How many members are there in this household again?",
                                             answer_type=Question.MULTICHOICE, order=3,
                                             module=new_module, group=self.household_member_group, identifier='Q4')
        question_3.batches.add(new_batch)
        BatchQuestionOrder.objects.create(batch=new_batch, question=question_3, order=1)

        params = {'group__id': str(self.household_member_group.id), 'module__id': str(new_module.id),
                  'answer_type': Question.MULTICHOICE}

        questions = _get_questions_based_on_filter(None, params)

        all_questions = [self.question_1, self.question_2]

        [self.assertNotIn(question, questions) for question in all_questions]
        self.assertIn(question_3, questions)
        self.assertIn(question_4, questions)

    def test_get_questions_based_on_filter_should_return_batch_specific_questions_if_batch_is_specified(self):
        question_3 = Question.objects.create(text="How many members are there in this household?",
                                             answer_type=Question.NUMBER, order=1,
                                             module=QuestionModule.objects.create(name="Economics"), identifier='Q3')

        params = {'group__id': 'All', 'module__id': 'All', 'answer_type': 'All'}

        questions = _get_questions_based_on_filter(self.batch.id, params)

        all_questions = [self.question_1, self.question_2]

        [self.assertIn(question, questions) for question in all_questions]
        self.assertNotIn(question_3, questions)

    def test_get_index_per_batch(self):
        response = self.client.get('/batches/%d/questions/' % self.batch.id)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertIn(self.question_1, response.context['questions'])
        self.assertIn(self.question_2, response.context['questions'])
        self.assertEqual(self.batch, response.context['batch'])
        self.assertEqual(DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, response.context['max_question_per_page'])
        self.assertIsNotNone(response.context['request'])

    def _convert_to_get_parameters(self, data):
        get_params = "?"
        for key in data.keys():
            get_params +="%s=%s&"%(key, data[key])
        return get_params

    def test_limit_list_size_per_page(self):
        max_question_per_page_supplied = 100
        data = self.form_data.copy()
        data['number_of_questions_per_page'] = max_question_per_page_supplied
        response = self.client.get('/batches/%d/questions/%s'% (self.batch.id, self._convert_to_get_parameters(data)))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(max_question_per_page_supplied, response.context['max_question_per_page'])

    def test_limit_list_size_per_page_cannot_be_greater_than_1000(self):
        max_question_per_page_supplied = 2000
        data = self.form_data.copy()
        data['number_of_questions_per_page'] = max_question_per_page_supplied
        response = self.client.post('/batches/%d/questions/'%self.batch.id, data)

        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, response.context['max_question_per_page'])


    def test_post_index_per_batch(self):
        response = self.client.post('/batches/%d/questions/' % self.batch.id)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertIn(self.question_1, response.context['questions'])
        self.assertIn(self.question_2, response.context['questions'])
        self.assertIsNotNone(response.context['question_filter_form'])
        self.assertIsInstance(response.context['question_filter_form'], QuestionFilterForm)
        self.assertEqual(self.batch, response.context['batch'])
        self.assertIsNotNone(response.context['request'])

    @patch('django.contrib.messages.error')
    def test_no_questions_in_batch(self, mock_error):
        other_batch = Batch.objects.create(order=2, name="Other Batch")
        response = self.client.get('/batches/%d/questions/' % other_batch.id)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertEquals(0, len(response.context['questions']))
        self.assertEqual(other_batch, response.context['batch'])
        self.assertIsNotNone(response.context['request'])
        mock_error.assert_called_once_with(response.context['request'],
                                           'There are no questions associated with this batch yet.')

    def test_add_new_question(self):
        response = self.client.get('/questions/new/')
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/new.html', templates)
        self.assertIsInstance(response.context['questionform'], QuestionForm)

    def test_question_form_is_in_response_request_context(self):
        response = self.client.get('/questions/new/')
        self.assertIsInstance(response.context['questionform'], QuestionForm)
        self.assertEqual(response.context['button_label'], 'Create')
        self.assertEqual(response.context['id'], 'add-question-form')
        self.assertEqual(response.context['class'], 'question-form')

    def test_restricted_permissions(self):
        member_group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        self.assert_restricted_permission_for("/questions/new/")
        self.assert_restricted_permission_for('/batches/%d/questions/' % self.batch.id)
        self.assert_restricted_permission_for('/questions/')
        self.assert_restricted_permission_for(
            '/batches/%d/questions/groups/%d/module/%s/' % (self.batch.id, member_group.id, self.module.id))
        self.assert_restricted_permission_for('/questions/1/edit/')
        self.assert_restricted_permission_for('/batches/2/questions/1/add_logic/')
        self.assert_restricted_permission_for('/questions/1/sub_questions/new/')

    def test_not_allowed_if_batch_is_open(self):
        some_location = Location.objects.create(name="Bukoto")
        self.batch.open_for_location(some_location)
        self.assert_not_allowed_when_batch_is_open("/batches/%d/questions/%d/sub_questions/new/"%(self.batch.id,self.question_1.id),
                                                   expected_redirect_url="/batches/%d/questions/"%self.batch.id,
                                                   expected_message="Subquestions cannot be added while batch is open.")
        self.assert_not_allowed_when_batch_is_open("/batches/%d/questions/%d/remove/"%(self.batch.id,self.question_1.id),
                                                   expected_redirect_url="/batches/%d/questions/"%self.batch.id,
                                                   expected_message="Question cannot be removed from a batch while the batch is open.")

    def test_create_question_number_does_not_create_options(self):
        form_data = {
            'module': self.module.id,
            'text': 'This is a Question',
            'answer_type': Question.NUMBER,
            'identifier': 'ID 1',
            'group': self.household_member_group.id,
            'options': 'some option that should not be created',
        }
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)
        question_options = question[0].options.all()
        self.assertEqual(0, question_options.count())
        success_message = "Question successfully added."
        self.assertTrue(success_message in response.cookies['messages'].value)

    def test_create_question_saves_order_based_on_group_created_for(self):
        form_data = {
            'module': self.module.id,
            'text': "This is a question",
            'identifier': 'ID 21',
            'answer_type': Question.NUMBER,
            'group': self.household_member_group.id,
            'options': ''
        }
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertEqual(1, question[0].order)

        form_data['text'] = 'This is another question'
        form_data['identifier'] = '21'
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertEqual(2, question[0].order)

        new_household_member_group = HouseholdMemberGroup.objects.create(name='Age 15-20', order=2)
        form_data['text'] = 'This is a question in new group'
        form_data['identifier'] = '233'
        form_data['group'] = new_household_member_group.id
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertEqual(1, question[0].order)

    def test_should_retrieve_group_specific_questions_in_context_if_selected_group_key_is_in_request(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q1')

        group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                       answer_type=Question.NUMBER, order=2,
                                                       group=self.household_member_group,
                                                       module=self.module, identifier='Q2')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q3')

        all_group_questions = [group_question, group_question_again]
        another_group_questions = [another_group_question]
        order = 1

        for question in [group_question, group_question_again, another_group_question]:
            question.batches.add(self.batch)
            BatchQuestionOrder.objects.create(batch=self.batch, question=question, order=order)
            order += 1

        response = self.client.get(
            '/batches/%d/questions/?groups=%s' % (self.batch.id, self.household_member_group.id))

        questions = response.context["questions"]

        [self.assertIn(question, questions) for question in all_group_questions]
        [self.assertNotIn(question, questions) for question in another_group_questions]

    def test_post_should_retrieve_questions_for_selected_keys_is_in_request(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q301')

        group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                       answer_type=Question.NUMBER, order=2,
                                                       group=self.household_member_group,
                                                       module=self.module, identifier='Q022')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q013')


        all_group_questions = [group_question, group_question_again]
        another_group_questions = [another_group_question]

        order = 1
        for question in [group_question, group_question_again, another_group_question]:
            question.batches.add(self.batch)
            BatchQuestionOrder.objects.create(batch=self.batch, question=question, order=order)
            order += 1

        filter_form_data = {'groups': self.household_member_group.id, 'module': self.module.id, 'identifier': 'ID 1',
                            'question_types': Question.NUMBER, 'batch_id': self.batch.id}

        response = self.client.post(
            '/batches/%d/questions/?groups=%s' % (self.batch.id, self.household_member_group.id),
            data=filter_form_data)

        questions = response.context["questions"]

        [self.assertIn(question, questions) for question in all_group_questions]
        [self.assertNotIn(question, questions) for question in another_group_questions]

    def test_should_retrieve_all_questions_in_context_if_selected_group_key_is_all_in_request(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q121')

        group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                       answer_type=Question.NUMBER, order=2,
                                                       group=self.household_member_group,
                                                       module=self.module, identifier='Q022')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q053')

        all_group_questions = [group_question, group_question_again, another_group_question]
        counter = 1

        for question in all_group_questions:
            BatchQuestionOrder.objects.create(question=question, batch=self.batch, order=counter)
            question.batches.add(self.batch)
            counter += 1

        response = self.client.get('/batches/%d/questions/?groups=%s' % (self.batch.id, 'all'))

        questions = response.context["questions"]

        [self.assertIn(question, questions) for question in all_group_questions]

    def test_should_retrieve_all_questions_in_context_if_selected_group_key_and_module_are_specific_in_request(self):
        module_group_question = Question.objects.create(text="How many members are there in this household?",
                                                        answer_type=Question.NUMBER, order=1,
                                                        group=self.household_member_group,
                                                        module=self.module, identifier='Q0441')

        module_group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                              answer_type=Question.NUMBER, order=2,
                                                              group=self.household_member_group,
                                                              module=self.module, identifier='Q0262')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q063')
        another_module_question = Question.objects.create(text="What is your name?",
                                                          answer_type=Question.NUMBER, order=2,
                                                          group=self.household_member_group,
                                                          module=QuestionModule.objects.create(name="Economics"),
                                                          identifier='Q0784')

        all_group_module_questions = [module_group_question, module_group_question_again]
        all_excluded_questions = [another_group_question, another_module_question]

        response = self.client.get('/batches/%s/questions/groups/%s/module/%s/' % (
            self.batch.id, self.household_member_group.id, self.module.id))

        questions = json.loads(response.content)

        [self.assertIn(dict(text=question.text, id=question.id, answer_type=question.answer_type), questions) for
         question in all_group_module_questions]
        [self.assertNotIn(dict(text=question.text, id=question.id), questions) for question in
         all_excluded_questions]

    def test_should_retrieve_all_questions_as_data_for_filter_if_all_is_group_id_key_and_module_id_is_specific(self):
        module_question = Question.objects.create(text="How many members are there in this household?",
                                                  answer_type=Question.NUMBER, order=1,
                                                  group=self.household_member_group,
                                                  module=self.module, identifier='Q021')

        module_question_again = Question.objects.create(text="How many women are there in this household?",
                                                        answer_type=Question.NUMBER, order=2,
                                                        group=self.household_member_group,
                                                        module=self.module, identifier='Q082')

        another_module_question = Question.objects.create(text="What is your name?",
                                                          answer_type=Question.NUMBER, order=2,
                                                          group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                    order=2),
                                                          module=QuestionModule.objects.create(name="Economics"),
                                                          identifier='Q083')

        all_module_questions = [module_question, module_question_again]
        questions_that_should_not_appear_in_response = [another_module_question]

        response = self.client.get(
            '/batches/%s/questions/groups/%s/module/%s/' % (self.batch.id, 'all', self.module.id))

        questions = json.loads(response.content)

        [self.assertIn(dict(text=question.text, id=question.id, answer_type=question.answer_type), questions) for
         question in all_module_questions]
        [self.assertNotIn(dict(text=question.text, id=question.id), questions) for question in
         questions_that_should_not_appear_in_response]

    def test_should_retrieve_group_specific_questions_as_data_for_filter_if_group_id_key(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q1')

        group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                       answer_type=Question.NUMBER, order=2,
                                                       group=self.household_member_group,
                                                       module=self.module, identifier='Q2')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q3')

        expected_questions = [group_question, group_question_again]
        questions_that_should_not_appear_in_response = [another_group_question]

        response = self.client.get(
            '/batches/%s/questions/groups/%s/module/%s/' % (self.batch.id, self.household_member_group.id, 'all'))

        questions = json.loads(response.content)

        [self.assertIn(dict(text=question.text, id=question.id, answer_type=question.answer_type), questions) for
         question in expected_questions]
        [self.assertNotIn(dict(text=question.text, id=question.id), questions) for question in
         questions_that_should_not_appear_in_response]

    def test_retrieves_all_questions_data_for_filter_if_module_and_group_key_selected_is_all(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q01')

        group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                       answer_type=Question.NUMBER, order=2,
                                                       group=self.household_member_group,
                                                       module=self.module, identifier='Q02')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q03')

        all_group_questions = [group_question, group_question_again, another_group_question]

        response = self.client.get('/batches/%s/questions/groups/%s/module/%s/' % (self.batch.id, 'all', 'all'))

        questions = json.loads(response.content)

        [self.assertIn(dict(text=question.text, id=question.id, answer_type=question.answer_type), questions) for
         question in all_group_questions]

    def test_retrieves_all_questions_not_in_batch_for_filter_if_module_and_group_key_selected_is_all(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q1')

        group_question_again = Question.objects.create(text="How many women are there in this household?",
                                                       answer_type=Question.NUMBER, order=2,
                                                       group=self.household_member_group,
                                                       module=self.module, identifier='Q2')

        another_group_question = Question.objects.create(text="What is your name?",
                                                         answer_type=Question.NUMBER, order=2,
                                                         group=HouseholdMemberGroup.objects.create(name='Age 6-10',
                                                                                                   order=2),
                                                         module=self.module, identifier='Q3')

        another_group_question.batches.add(self.batch)

        all_group_questions = [group_question, group_question_again]
        excluded_question = [another_group_question]

        response = self.client.get('/batches/%s/questions/groups/%s/module/%s/' % (self.batch.id, 'all', 'all'))

        questions = json.loads(response.content)

        [self.assertIn(dict(text=question.text, id=question.id, answer_type=question.answer_type), questions) for
         question in all_group_questions]
        [self.assertNotIn(dict(text=question.text, id=question.id, answer_type=question.answer_type), questions) for
         question in excluded_question]

    def test_knows_question_is_multichoice_and_returns_in_the_context_value_true(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.MULTICHOICE, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q251')
        option_1 = QuestionOption.objects.create(question=group_question, text="Option 1", order=1)
        option_2 = QuestionOption.objects.create(question=group_question, text="Option 2", order=2)
        option_3 = QuestionOption.objects.create(question=group_question, text="Option 3", order=3)

        all_options = [option_1, option_2, option_3]
        response = self.client.get('/questions/%s/is_multichoice/' % group_question.id)
        response_string = json.loads(response.content)

        self.assertTrue(response_string[0]['is_multichoice'])

        [self.assertIn({'id': option.id, 'text': option.text}, response_string[0]['question_options']) for option in all_options]

    def test_knows_question_is_not_multichoice_and_returns_in_the_context_value_false(self):
        group_question = Question.objects.create(text="How many members are there in this household?",
                                                 answer_type=Question.NUMBER, order=1,
                                                 group=self.household_member_group,
                                                 module=self.module, identifier='Q1111')

        response = self.client.get('/questions/%s/is_multichoice/' % group_question.id)
        response_string = json.loads(response.content)

        self.assertFalse(response_string[0]['is_multichoice'])
        self.assertEqual([], response_string[0]['question_options'])

    def test_knows_in_existent_question_returns_in_the_context_value_false(self):
        non_existent_id = 100
        response = self.client.get('/questions/%s/is_multichoice/' % non_existent_id)
        response_string = json.loads(response.content)

        self.assertFalse(response_string[0]['is_multichoice'])
        self.assertEqual([], response_string[0]['question_options'])

    def test_should_save_options_for_multichoice_questions(self):
        form_data = {
            'module': self.module.id,
            'text': 'This is a Question',
            'identifier': 'ID 1',
            'answer_type': Question.MULTICHOICE,
            'group': self.household_member_group.id,
            'options': ['some question option 1', 'some question option 2'],
        }
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertEqual(1, len(question))
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)
        question_options = question[0].options.all()
        self.assertEqual(2, question_options.count())
        self.assertIn(QuestionOption.objects.get(text=form_data['options'][0]), question_options)
        self.assertIn(QuestionOption.objects.get(text=form_data['options'][1]), question_options)
        option_index = 0
        for option_text in form_data['options']:
            option_index += 1
            self.assertIn(QuestionOption.objects.get(text=option_text), question_options)
            self.assertEqual(option_index,
                             QuestionOption.objects.get(text=form_data['options'][option_index - 1]).order)

    def test_should_not_save_empty_options_on_multichoice_questions(self):
        form_data = {
            'module': self.module.id,
            'text': 'This is a Question',
            'identifier': 'ID 1',
            'answer_type': Question.MULTICHOICE,
            'group': self.household_member_group.id,
            'options': ['some question option 1', '', 'some question option 2', ''],
        }
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertEqual(1, len(question))
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)
        question_options = question[0].options.all()
        self.assertEqual(2, question_options.count())
        self.assertIn(QuestionOption.objects.get(text=form_data['options'][0]), question_options)
        self.assertIn(QuestionOption.objects.get(text=form_data['options'][2]), question_options)

    def test_should_not_save_multichoice_questions_if_no_option_supplied(self):
        form_data = {
            'module': self.module,
            'text': 'This is a Question',
            'identifier': 'ID 1',
            'answer_type': Question.MULTICHOICE,
            'group': self.household_member_group.id,
            'options': '',
        }
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        self.failUnlessEqual(response.status_code, 200)
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)

    def test_should_not_save_options_if_question_not_multichoice_even_if_options_supplied(self):
        form_data = {
            'module': self.module.id,
            'text': 'This is a Question',
            'identifier': 'ID 1',
            'answer_type': Question.TEXT,
            'group': self.household_member_group.id,
            'options': ['some question option 1', 'some question option 2'],
        }
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failUnless(question)
        self.assertEqual(1, len(question))
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)
        question_options = question[0].options.all()
        self.assertEqual(0, question_options.count())

    def test_should_render_json_questions_filtered_by_group(self):
        member_group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question_1 = Question.objects.create(text="question1", answer_type=Question.NUMBER,
                                             group=member_group, module=self.module, identifier='Q1')
        question_2 = Question.objects.create(text="question2", answer_type=Question.NUMBER, module=self.module,
                                             identifier='Q2')
        response = self.client.get(
            '/batches/%d/questions/groups/%d/module/%s/' % (self.batch.id, member_group.id, self.module.id))
        self.failUnlessEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEquals(len(content), 1)

        self.assertEquals(content[0]['id'], question_1.pk)
        self.assertEquals(content[0]['text'], question_1.text)

    def test_get_index_all(self):
        sub_question = Question.objects.create(parent=self.question_1, text="Sub Question 2?",
                                               answer_type=Question.NUMBER, subquestion=True, module=self.module,
                                               identifier='Q121')
        response = self.client.get('/questions/')

        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertIn(self.question_1, response.context['questions'])
        self.assertIn(self.question_2, response.context['questions'])
        self.assertIsNotNone(response.context['question_filter_form'])
        self.assertIsInstance(response.context['question_filter_form'], QuestionFilterForm)
        self.assertNotIn(sub_question, response.context['questions'])
        self.assertEqual(DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, response.context['max_question_per_page'])
        self.assertIsNotNone(response.context['request'])

    def test_get_index_all(self):
        sub_question = Question.objects.create(parent=self.question_1, text="Sub Question 2?",
                                               answer_type=Question.NUMBER, subquestion=True, module=self.module,
                                               identifier='Q122')

        response = self.client.get('/questions/')

        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertIn(self.question_1, response.context['questions'])
        self.assertIn(self.question_2, response.context['questions'])
        self.assertIsNotNone(response.context['question_filter_form'])
        self.assertIsInstance(response.context['question_filter_form'], QuestionFilterForm)
        self.assertNotIn(sub_question, response.context['questions'])
        self.assertEqual(DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, response.context['max_question_per_page'])
        self.assertIsNotNone(response.context['request'])

    def test_limit_list_size_per_page_on_index_alla(self):
        max_question_per_page_supplied = 100
        data = self.form_data.copy()
        data['number_of_questions_per_page'] = max_question_per_page_supplied
        response = self.client.get('/questions/%s' % self._convert_to_get_parameters(data))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(max_question_per_page_supplied, response.context['max_question_per_page'])

    def test_limit_list_size_per_page_cannot_be_greater_than_1000_on_index_all(self):
        max_question_per_page_supplied = 2000
        data = self.form_data.copy()
        data['number_of_questions_per_page'] = max_question_per_page_supplied
        response = self.client.get('/questions/%s' % self._convert_to_get_parameters(data))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(MAX_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, response.context['max_question_per_page'])

    def test_get_index_should_return_questions_matching_get_keys(self):
        question = Question.objects.create(text="Sub Question 2?", answer_type=Question.NUMBER, module=self.module,
                                           identifier='Q09')
        sub_question = Question.objects.create(parent=question, text="Sub Question 2?",
                                               answer_type=Question.NUMBER, subquestion=True, module=self.module,
                                               identifier='Q02')

        module = QuestionModule.objects.create(name="Education")
        member_group = HouseholdMemberGroup.objects.create(name="Education", order=0)
        question_1 = Question.objects.create(text="Sub Question 2?",
                                             answer_type=Question.NUMBER, module=module, group=member_group,
                                             identifier='Q03')
        question_2 = Question.objects.create(text="Sub Question 2?",
                                             answer_type=Question.NUMBER, module=module, group=member_group,
                                             identifier='Q04')
        self.batch.questions.add(question_1)
        self.batch.questions.add(question_2)
        BatchQuestionOrder.objects.create(batch=self.batch, question=question_1, order=1)
        BatchQuestionOrder.objects.create(batch=self.batch, question=question_2, order=2)

        expected_questions = [question_1, question_2]
        excluded_questions = [sub_question, question]

        filter_form_data = {'groups': member_group.id, 'modules': module.id, 'identifier': 'ID 1',
                            'question_types': Question.NUMBER, 'batch_id': self.batch.id,
                            'number_of_questions_per_page':50}

        response = self.client.get('/questions/%s' % self._convert_to_get_parameters(filter_form_data))
        [self.assertIn(expected_question, response.context['questions']) for expected_question in expected_questions]
        [self.assertNotIn(excluded_question, response.context['questions']) for excluded_question in excluded_questions]

    def test_filter_question_list_pagination(self):
        for i in range(25):
            Question.objects.create(text="%d" % i, answer_type=Question.NUMBER, order=i, module=self.module, identifier='Q%d'% i)


        module = QuestionModule.objects.create(name="Education")
        different_module_question = Question.objects.create(text="haha", answer_type=Question.NUMBER, module=module,
                                           identifier='Q09')

        filter_form_data = {'modules': self.module.id,
                            'question_types': Question.NUMBER, 'batch_id': self.batch.id,
                            'number_of_questions_per_page':20}

        response = self.client.get('/questions/%spage=2' % self._convert_to_get_parameters(filter_form_data))
        [self.assertEqual(self.module, question.module) for question in  response.context['questions'] ]
        self.assertNotIn(different_module_question, response.context['questions'])

    def test_add_new_subquestion(self):
        group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question = Question.objects.create(text="some qn?", group=group, order=1, module=self.module, identifier='Q22')
        response = self.client.get('/questions/%d/sub_questions/new/' % question.id)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/new.html', templates)
        self.assertIsInstance(response.context['questionform'], QuestionForm)
        self.assertEqual(response.context['button_label'], 'Create')
        self.assertEqual(response.context['id'], 'add-sub_question-form')
        self.assertEqual(response.context['parent_question'], question)
        self.assertEqual(response.context['heading'], "Add SubQuestion")
        self.assertEqual(response.context['class'], 'question-form')

    def test_post_sub_question(self):
        group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question = Question.objects.create(text="some qn?", group=group, order=1, module=self.module, identifier='Q20202')
        subquestion_form_data = {
            'module': self.module.id,
            'text': 'This is a Question',
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': group.id,
            'options': 'some option that should not be created'
        }
        response = self.client.post('/questions/%d/sub_questions/new/' % int(question.id), data=subquestion_form_data)
        saved_sub_question = Question.objects.filter(text=subquestion_form_data['text'])
        self.failUnless(saved_sub_question)
        self.assertEquals(saved_sub_question[0].parent, question)
        self.assertEquals(saved_sub_question[0].group, question.group)
        self.assertIsNone(saved_sub_question[0].order)
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)

    def test_post_sub_question_knows_to_strip_strange_characters(self):
        group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question = Question.objects.create(text="some qn?", group=group, order=1, identifier='Q031')
        subquestion_form_data = {
            'module': self.module.id,
            'text': "This is a *!#'; Question",
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': group.id,
            'options': 'some option that should not be created'
        }

        modified_text = "This is a Question"

        response = self.client.post('/questions/%d/sub_questions/new/' % int(question.id), data=subquestion_form_data)
        saved_sub_question = Question.objects.filter().latest('created')
        self.assertNotEqual(saved_sub_question.text, subquestion_form_data['text'])
        self.assertEquals(saved_sub_question.text, modified_text)

    def test_should_filter_questions_in_a_group_that_does_not_belong_to_the_batch(self):
        group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question = Question.objects.create(text="some qn?", group=group, order=1, module=self.module, identifier='Q1')
        question.batches.add(self.batch)
        question_1 = Question.objects.create(text="some qn1?", group=group, order=2, module=self.module, identifier='Q2')
        question_2 = Question.objects.create(text="some qn2?", group=group, order=3, module=self.module, identifier='Q3')
        response = self.client.get('/batches/%s/questions/groups/%s/module/%s/' % (self.batch.id, group.id, 'all'))
        self.assertEqual(response.status_code, 200)
        parsed_response = json.loads(response.content)
        self.assertEqual(2, len(parsed_response))
        self.assertFalse(question.text in [item['text'] for item in parsed_response])
        self.assertTrue(question_2.text in [item['text'] for item in parsed_response])
        self.assertTrue(question_1.text in [item['text'] for item in parsed_response])

    def test_returns_added_options_when_form_has_error(self):
        too_long_to_be_accepted_question = 'Get all the apps and games you love on Nexus 4 - with over\
        titles to choose from on Google Play, s something for everyone. Find the most popular free and \
        paid apps, explore hand-picked collections'
        option_1 = 'some question option 1'
        option_2 = 'some question option 2'

        form_data = {
            'module': self.module.id,
            'order': self.question_1.order,
            'text': too_long_to_be_accepted_question,
            'identifier': 'ID 1',
            'answer_type': Question.TEXT,
            'group': '',
            'options': [option_1, option_2],
        }

        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        response = self.client.post('/questions/new/', data=form_data)
        question = Question.objects.filter(text=form_data['text'])
        self.failIf(question)
        self.assertEqual(response.status_code, 200)
        self.assertIn(option_1, response.context['options'])
        self.assertIn(option_2, response.context['options'])

    def test_should_display_form_on_edit_question(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, module=self.module, identifier='Q1')
        question.batches.add(self.batch)
        response = self.client.get('/questions/%d/edit/' % question.id)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/new.html', templates)
        self.assertIsInstance(response.context['questionform'], QuestionForm)
        self.assertEqual(response.context['button_label'], 'Save')
        self.assertEqual(response.context['id'], 'add-question-form')

    def test_should_display_options_on_edit_multichoice_question(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group,
                                           answer_type=Question.MULTICHOICE, module=self.module, identifier='Q1')
        question.batches.add(self.batch)
        question_option = QuestionOption.objects.create(text="question option text 1", question=question)
        question_option_2 = QuestionOption.objects.create(text="question option text 2", question=question)
        response = self.client.get('/questions/%d/edit/' % question.id)
        self.assertEqual(2, len(response.context['options']))
        self.assertIn(question_option.text, response.context['options'])
        self.assertIn(question_option_2.text, response.context['options'])

    def test_empty_options_and_or_duplicates_should_be_removed_on_edit_multichoice_question(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, answer_type=Question.MULTICHOICE,
                                           module=self.module, identifier='Q123')
        question.batches.add(self.batch)
        question_option = QuestionOption.objects.create(text="question option text 1", question=question)
        question_option_2 = QuestionOption.objects.create(text="question option text 2", question=question)

        form_data = {
            'module': self.module.id,
            'text': '',
            'identifier': 'ID 1',
            'answer_type': Question.MULTICHOICE,
            'group': group.id,
            'options': ['', question_option.text, '', question_option_2.text, '', question_option_2.text]
        }

        form_data1 = form_data.copy()
        del form_data1['options']
        self.failIf(Question.objects.filter(**form_data1))
        response = self.client.post('/questions/%d/edit/' % question.id, data=form_data)
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(Question.objects.filter(**form_data1))
        self.assertEqual(2, len(response.context['options']))
        self.assertIn(question_option.text, response.context['options'])
        self.assertIn(question_option_2.text, response.context['options'])

    def test_should_strip_special_characters_from_options(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, answer_type=Question.MULTICHOICE,
                                           identifier='Q1')
        question.batches.add(self.batch)

        option_1 = "option 1"
        option_2 = "option 2"
        option_3 = "dont know"
        form_data = {
            'module': self.module.id,
            'text': '',
            'identifier': 'ID 1',
            'answer_type': Question.MULTICHOICE,
            'group': group.id,
            'options': [option_1, "option ! 2", "don't know"]
        }

        all_options = [option_1, option_2, option_3]
        response = self.client.post('/questions/new/', data=form_data)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(3, len(response.context['options']))
        [self.assertIn(option, response.context['options']) for option in all_options]

    def test_should_save_on_post_edit_question(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, identifier='Q1')
        question.batches.add(self.batch)
        form_data = {
            'module': self.module.id,
            'text': 'This is a Question',
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.household_member_group.id
        }

        self.failIf(Question.objects.filter(**form_data))
        response = self.client.post('/questions/%d/edit/' % question.id, data=form_data)
        saved_question = Question.objects.filter(**form_data)
        self.failUnless(saved_question)
        self.assertEqual(1, saved_question.count())
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)
        success_message = "Question successfully edited."
        self.assertTrue(success_message in response.cookies['messages'].value)

    def test_should_update_options_order_and_text_on_edit_of_mutlichoice_question(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, answer_type=Question.MULTICHOICE,
                                           identifier='Q1')
        question_option = QuestionOption.objects.create(text="question option text 1", question=question, order=1)
        question_option_2 = QuestionOption.objects.create(text="question option text 2", question=question, order=2)
        question.batches.add(self.batch)
        form_data = {
            'module': self.module.id,
            'text': 'I edited this question',
            'identifier': 'ID 1',
            'answer_type': Question.MULTICHOICE,
            'group': group.id,
            'options': [question_option_2.text, 'hahaha', question_option.text]
        }

        form_data1 = form_data.copy()
        del form_data1['options']
        self.failIf(Question.objects.filter(**form_data1))
        response = self.client.post('/questions/%d/edit/' % question.id, data=form_data)
        self.assertRedirects(response, expected_url='/questions/', status_code=302, target_status_code=200)
        retrieved_question = Question.objects.filter(**form_data1)
        self.assertEqual(1, retrieved_question.count())
        options = retrieved_question[0].options.all()
        self.assertEqual(3, options.count())
        self.failUnless(QuestionOption.objects.filter(text=question_option_2.text, order=1, question=question))
        self.failUnless(QuestionOption.objects.filter(text="hahaha", order=2, question=question))
        self.failUnless(QuestionOption.objects.filter(text=question_option.text, order=3, question=question))

    def test_should_not_save_on_post_edit_question_failure(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, identifier='Q1')
        question.batches.add(self.batch)
        form_data = {
            'module': self.module.id,
            'text': '',
            'identifier': 'ID 1',
            'answer_type': Question.TEXT,
            'group': self.household_member_group.id
        }

        self.failIf(Question.objects.filter(**form_data))
        response = self.client.post('/questions/%d/edit/' % question.id, data=form_data)
        self.failUnlessEqual(response.status_code, 200)
        saved_question = Question.objects.filter(**form_data)
        self.failIf(saved_question)
        error_message = 'Question was not edited.'
        self.assertTrue(error_message, response.context['messages'])

    def test_should_throw_error_if_editing_non_question_survey(self):
        response = self.client.get('/questions/11/edit/')
        self.assertRedirects(response, '/questions/', status_code=302, target_status_code=200, msg_prefix='')
        error_message = "Question does not exist."
        self.assertIn(error_message, response.cookies['messages'].value)

    def test_should_delete_question(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, identifier='Q1')
        question.batches.add(self.batch)
        self.failUnless(question)

        response = self.client.get('/questions/%d/delete/' % question.id, )
        self.failIf(Question.objects.filter(id=question.id))

        self.assertRedirects(response, '/questions/', status_code=302, target_status_code=200, msg_prefix='')
        success_message = "Question successfully deleted."
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_should_throw_error_when_trying_to_delete_non_existent_question(self):
        non_existing_id = 222222
        response = self.client.get('/questions/%d/delete/' % non_existing_id)
        self.assertRedirects(response, '/questions/', status_code=302, target_status_code=200, msg_prefix='')
        error_message = "Question / Subquestion does not exist."
        self.assertIn(error_message, response.cookies['messages'].value)

    def test_delete_shows_question_successfully_deleted_if_question_is_being_deleted(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, identifier='Q122')
        question.batches.add(self.batch)
        response = self.client.get('/questions/%d/delete/' % question.id)

        success_message = 'Question successfully deleted.'
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_delete_shows_sub_question_successfully_deleted_if_sub_question_is_being_deleted(self):
        group = HouseholdMemberGroup.objects.create(name="group", order=33)
        question = Question.objects.create(text="question text", group=group, identifier='Q12')
        sub_question = Question.objects.create(parent=question, text="sub question text", subquestion=True, group=group)
        question.batches.add(self.batch)
        response = self.client.get('/questions/%d/delete/' % sub_question.id)

        success_message = 'Sub question successfully deleted.'
        self.assertIn(success_message, response.cookies['messages'].value)


class LogicViewTest(BaseTest):
    def setUp(self):
        self.client = Client()
        self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                  'can_view_batches')
        self.client.login(username='User', password='password')

        self.module = QuestionModule.objects.create(name="Education")

        self.batch = Batch.objects.create(order=1)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1,
                                                module=self.module, identifier='Q1')
        self.question_2 = Question.objects.create(text="Question 2?",
                                                  answer_type=Question.NUMBER, order=2,
                                                  module=self.module, identifier='Q2')

        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question, order=1)
        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question_2, order=2)

        self.question.batches.add(self.batch)
        self.question_2.batches.add(self.batch)

    def test_knows_questions_have_all_rules_for_batch_when_sent_in_context(self):
        answer_rule = AnswerRule.objects.create(batch=self.batch, question=self.question,
                                                action=AnswerRule.ACTIONS['END_INTERVIEW'],
                                                condition=AnswerRule.CONDITIONS['EQUALS'],
                                                validate_with_value=0)

        answer_rule_2 = AnswerRule.objects.create(batch=self.batch, question=self.question,
                                                  action=AnswerRule.ACTIONS['REANSWER'],
                                                  condition=AnswerRule.CONDITIONS['EQUALS'],
                                                  validate_with_value=1)
        all_rules = [answer_rule, answer_rule_2]

        response = self.client.get('/batches/%s/questions/' % self.batch.pk)
        all_questions = response.context['questions']
        self.assertEqual(2, len(all_questions))
        self.assertIn(self.question, all_questions)
        rule_question = Question.objects.get(id=self.question.id)

        all_question_batch_rules = response.context['rules_for_batch']
        self.assertEqual(2, len(all_question_batch_rules))
        self.assertEqual(2, len(all_question_batch_rules[rule_question]))
        [self.assertIn(rule, all_question_batch_rules[rule_question]) for rule in all_rules]
        self.assertIsNotNone(response.context['question_filter_form'])
        self.assertIsInstance(response.context['question_filter_form'], QuestionFilterForm)

    def test_views_add_logic_get_has_logic_form_in_context_and_has_success_response(self):
        answer_rule_2 = AnswerRule.objects.create(batch=self.batch, question=self.question,
                                                  action=AnswerRule.ACTIONS['REANSWER'],
                                                  condition=AnswerRule.CONDITIONS['EQUALS'],
                                                  validate_with_value=1)
        response = self.client.get('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, self.question.pk))

        self.assertIsInstance(response.context['logic_form'], LogicForm)
        self.assertEqual(response.context['button_label'], 'Save')
        self.assertEqual(response.context['batch'], self.batch)
        self.assertIn(answer_rule_2, response.context['rules_for_batch'].get(self.question, None))
        self.assertEqual(response.context['batch_id'], str(self.batch.id))
        self.assertEqual(response.context['cancel_url'], '/batches/%s/questions/' % self.batch.pk)
        self.assertEqual(200, response.status_code)

    def test_views_add_logic_get_has_question_in_context(self):
        response = self.client.get('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, self.question.pk))
        action = '/questions/%s/sub_questions/new/' % self.question.pk

        self.assertIsInstance(response.context['question'], Question)
        self.assertEqual(response.context['question'], self.question)
        self.assertEqual(response.context['modal_action'], action)
        self.assertIsInstance(response.context['questionform'], QuestionForm)
        self.assertEqual(response.context['class'], 'question-form')
        self.assertEqual(200, response.status_code)

    def test_views_add_logic_returns_rule_already_exists_if_simmilar_rule_exists_on_the_question_and_batch(self):
        AnswerRule.objects.create(batch=self.batch, question=self.question,
                                  action=AnswerRule.ACTIONS['REANSWER'],
                                  condition=AnswerRule.CONDITIONS['EQUALS'],
                                  validate_with_value=1)

        form_data = {'condition': AnswerRule.CONDITIONS['EQUALS'],
                     'attribute': 'value',
                     'value': '1',
                     'action': AnswerRule.ACTIONS['REANSWER']
        }

        response = self.client.post('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, self.question.pk),
                                    data=form_data)
        self.failIf(AnswerRule.objects.filter(condition=form_data['condition'], validate_with_value=form_data['value'],
                                              action=form_data['action'],
                                              question=self.question, batch=self.batch).count() > 1)
        self.assertEqual(200, response.status_code)
        error_message = 'Rule on this value with EQUALS criteria already exists.'
        self.assertIn(error_message, str(response))

    def test_knows_rule_exist_when_same_rule_conditions_sent(self):
        answer_rule_data = {'condition': AnswerRule.CONDITIONS['EQUALS'],
                            'validate_with_value': '1',
                            'action': AnswerRule.ACTIONS['REANSWER']
        }
        self.assertFalse(_rule_exists(self.question, self.batch, **answer_rule_data))

        AnswerRule.objects.create(batch=self.batch, question=self.question,
                                  action=AnswerRule.ACTIONS['REANSWER'],
                                  condition=AnswerRule.CONDITIONS['EQUALS'],
                                  validate_with_value=1)
        self.assertTrue(_rule_exists(self.question, self.batch, **answer_rule_data))

    def test_views_saves_answer_rule_on_post_if_all_values_are_selected(self):
        form_data = {'condition': 'EQUALS',
                     'attribute': 'value',
                     'value': 0,
                     'action': 'SKIP_TO',
                     'next_question': self.question_2.pk}

        response = self.client.post('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, self.question.pk),
                                    data=form_data)
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.pk, status_code=302,
                             target_status_code=200)
        success_message = 'Logic successfully added.'
        self.assertIn(success_message, response.cookies['messages'].value)
        answer_rules = AnswerRule.objects.filter()

        self.failUnless(answer_rules)

        answer_rule = answer_rules[0]

        self.assertEqual(self.question, answer_rule.question)
        self.assertEqual(form_data['action'], answer_rule.action)
        self.assertEqual(form_data['condition'], answer_rule.condition)
        self.assertEqual(self.question_2, answer_rule.next_question)
        self.assertEqual(self.batch, answer_rule.batch)
        self.assertEqual(form_data['value'], answer_rule.validate_with_value)
        self.assertIsNone(answer_rule.validate_with_question)
        self.assertIsNone(answer_rule.validate_with_option)

    def test_views_saves_answer_rule_for_between_criteria_on_post_if_all_values_are_selected(self):
        form_data = {'condition': 'BETWEEN',
                     'attribute': 'value',
                     'min_value': 0,
                     'max_value': 10,
                     'action': 'SKIP_TO',
                     'next_question': self.question_2.pk}

        response = self.client.post('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, self.question.pk),
                                    data=form_data)
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.pk, status_code=302,
                             target_status_code=200)
        success_message = 'Logic successfully added.'
        self.assertIn(success_message, response.cookies['messages'].value)
        answer_rules = AnswerRule.objects.filter()

        self.failUnless(answer_rules)

        answer_rule = answer_rules[0]

        self.assertEqual(self.question, answer_rule.question)
        self.assertEqual(form_data['action'], answer_rule.action)
        self.assertEqual(form_data['condition'], answer_rule.condition)
        self.assertEqual(self.question_2, answer_rule.next_question)
        self.assertEqual(self.batch, answer_rule.batch)
        self.assertEqual(form_data['min_value'], answer_rule.validate_with_min_value)
        self.assertEqual(form_data['max_value'], answer_rule.validate_with_max_value)
        self.assertIsNone(answer_rule.validate_with_question)
        self.assertIsNone(answer_rule.validate_with_option)
        self.assertIsNone(answer_rule.validate_with_value)

    def test_views_saves_answer_rule_for_sub_question_on_post_if_all_values_are_selected(self):
        sub_question1 = Question.objects.create(text="sub question1", answer_type=Question.NUMBER, subquestion=True,
                                                parent=self.question, module=self.module, identifier='Q4')
        sub_question1.batches.add(self.batch)

        form_data = {'condition': 'EQUALS',
                     'attribute': 'value',
                     'value': 0,
                     'action': 'ASK_SUBQUESTION',
                     'next_question': sub_question1.pk}

        response = self.client.post('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, self.question.pk),
                                    data=form_data)
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.pk, status_code=302,
                             target_status_code=200)
        success_message = 'Logic successfully added.'
        self.assertIn(success_message, response.cookies['messages'].value)
        answer_rules = AnswerRule.objects.filter()

        self.failUnless(answer_rules)

        answer_rule = answer_rules[0]

        self.assertEqual(self.question, answer_rule.question)
        self.assertEqual(form_data['action'], answer_rule.action)
        self.assertEqual(form_data['condition'], answer_rule.condition)
        self.assertEqual(sub_question1, answer_rule.next_question)
        self.assertEqual(self.batch, answer_rule.batch)
        self.assertEqual(form_data['value'], answer_rule.validate_with_value)
        self.assertIsNone(answer_rule.validate_with_question)
        self.assertIsNone(answer_rule.validate_with_option)

    def test_views_saves_answer_rule_on_post_if_all_values_are_selected_on_multichoice_question(self):
        question_with_option = Question.objects.create(text="MultiChoice Question 1?",
                                                       answer_type=Question.MULTICHOICE, order=3,
                                                       module=self.module, identifier='Q211')
        question_with_option.batches.add(self.batch)
        question_option_1 = QuestionOption.objects.create(question=question_with_option, text="Option 1", order=1)
        QuestionOption.objects.create(question=question_with_option, text="Option 2", order=2)
        QuestionOption.objects.create(question=question_with_option, text="Option 3", order=3)

        form_data = {'condition': 'EQUALS_OPTION',
                     'attribute': 'option',
                     'option': question_option_1.id,
                     'action': 'END_INTERVIEW',
        }

        response = self.client.post('/batches/%s/questions/%s/add_logic/' % (self.batch.pk, question_with_option.pk),
                                    data=form_data)
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.pk, status_code=302,
                             target_status_code=200)
        answer_rules = AnswerRule.objects.filter()

        self.failUnless(answer_rules)

        answer_rule = answer_rules[0]

        self.assertEqual(question_with_option, answer_rule.question)
        self.assertEqual(self.batch, answer_rule.batch)
        self.assertEqual(form_data['action'], answer_rule.action)
        self.assertEqual(form_data['condition'], answer_rule.condition)
        self.assertEqual(form_data['option'], answer_rule.validate_with_option.id)
        self.assertIsNone(answer_rule.next_question)
        self.assertIsNone(answer_rule.validate_with_question)
        self.assertIsNone(answer_rule.validate_with_value)

class QuestionJsonDataDumpTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')
        self.module = QuestionModule.objects.create(name="Education")

        self.batch = Batch.objects.create(order=1)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1,
                                                module=self.module, identifier='Q1')

        self.sub_question_1 = Question.objects.create(parent=self.question, text="Sub Question 1?",
                                                      answer_type=Question.NUMBER, subquestion=True,
                                                      module=self.module, identifier='Q22')
        self.sub_question_2 = Question.objects.create(parent=self.question, text="Sub Question 2?",
                                                      answer_type=Question.NUMBER, subquestion=True,
                                                      module=self.module, identifier='Q323')

        self.question_2 = Question.objects.create(text="Question 2?",
                                                  answer_type=Question.NUMBER, order=2,
                                                  module=self.module, identifier='Q23')
        self.question_3 = Question.objects.create(text="Question 3?",
                                                  answer_type=Question.NUMBER, order=3,
                                                  module=self.module, identifier='Q31')

        self.question.batches.add(self.batch)
        self.sub_question_1.batches.add(self.batch)
        self.sub_question_2.batches.add(self.batch)
        self.question_2.batches.add(self.batch)
        self.question_3.batches.add(self.batch)

    def test_returns_data_dump_of_questions_in_batch_excluding_the_current_selected_question(self):
        response = self.client.get('/batches/%s/questions/%s/questions_json/' % (self.batch.pk, self.question.pk),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.failUnlessEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response)
        self.assertIn(dict(id=str(self.question_2.id), text=self.question_2.text), json_response)
        self.assertNotIn(dict(id=str(self.question.id), text=self.question.text), json_response)
        self.assertNotIn(dict(id=str(self.sub_question_1.id), text=self.sub_question_1.text), json_response)
        self.assertNotIn(dict(id=str(self.sub_question_2.id), text=self.sub_question_2.text), json_response)

    def test_returns_data_dump_of_sub_questions_infor_selected_question(self):
        response = self.client.get('/questions/%s/sub_questions_json/' % self.question.pk,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.failUnlessEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response)
        self.assertIn(dict(id=str(self.sub_question_1.id), text=self.sub_question_1.text), json_response)
        self.assertIn(dict(id=str(self.sub_question_2.id), text=self.sub_question_2.text), json_response)

        self.assertNotIn(dict(id=str(self.question_2.id), text=self.question_2.text), json_response)
        self.assertNotIn(dict(id=str(self.question.id), text=self.question.text), json_response)

class AddQuestionFromModalTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')

        self.module = QuestionModule.objects.create(name="Health")
        self.batch = Batch.objects.create(order=1)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1,
                                                module=self.module, identifier='Q1')
        self.question.batches.add(self.batch)

    def test_knows_how_to_add_sub_question_from_ajax_call(self):
        member_group = HouseholdMemberGroup.objects.create(name="Test Group", order=1)
        data = {'module': self.module.id,
                'text': 'hritik  question',
                'identifier': 'ID 1',
                'answer_type': Question.NUMBER,
                'group': member_group.id
        }

        response = self.client.post('/questions/%s/sub_questions/new/' % self.question.pk, data=data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        sub_question = self.question.get_subquestions().latest('created')

        self.failUnlessEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response)
        self.assertEqual(dict(id=str(sub_question.id), text=sub_question.text), json_response)

class AddSubQuestionTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')
        self.module = QuestionModule.objects.create(name="Education")

        self.batch = Batch.objects.create(order=1)
        self.group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1,
                                                group=self.group, module=self.module, identifier='Q1')
        self.question.batches.add(self.batch)

    def test_should_not_allow_to_add_same_sub_question_under_one_question(self):
        sub_question = Question.objects.create(text="this is a sub question", answer_type=Question.NUMBER,
                                               subquestion=True, parent=self.question, group=self.group,
                                               identifier='Q11')
        sub_question.batches.add(self.batch)
        subquestion_form_data = {
            'module': self.module.id,
            'text': sub_question.text,
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.group.id,
            'option': ''
        }
        response = self.client.post('/questions/%d/sub_questions/new/' % int(self.question.id),
                                    data=subquestion_form_data)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/new.html', templates)
        self.assertIsInstance(response.context['questionform'], QuestionForm)
        self.assertIsNotNone(response.context['questionform'].errors)

    def test_add_sub_question_redirects_to_master_questions_if_batch_is_not_present(self):
        subquestion_form_data = {
            'module': self.module.id,
            'text': "this is a new sub question",
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.group.id,
            'option': ''
        }
        expected_url = '/questions/'
        response = self.client.post('/questions/%d/sub_questions/new/' % int(self.question.id),
                                    data=subquestion_form_data)

        self.assertRedirects(response, expected_url, 302, 200)

    def test_add_sub_question_redirects_to_batch_questions_if_batch_is_present(self):
        subquestion_form_data = {
            'module': self.module.id,
            'text': "this is a new sub question",
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.group.id,
            'option': ''
        }
        expected_url = '/batches/%s/questions/' % self.batch.id
        response = self.client.post(
            '/batches/%s/questions/%d/sub_questions/new/' % (self.batch.id, int(self.question.id)),
            data=subquestion_form_data)

        self.assertRedirects(response, expected_url, 302, 200)

class EditSubQuestionTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')

        self.module = QuestionModule.objects.create(name="Education")
        self.batch = Batch.objects.create(order=1)
        self.group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1, group=self.group,
                                                module=self.module, identifier='Q1')
        self.sub_question = Question.objects.create(text="this is a sub question", answer_type=Question.NUMBER,
                                                    subquestion=True, parent=self.question,
                                                    group=self.group, module=self.module, identifier='Q12')

        self.question.batches.add(self.batch)

    def test_should_get_edit_subquestion(self):
        response = self.client.get('/questions/%d/sub_questions/edit/' % int(self.sub_question.id))
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/new.html', templates)
        self.assertIsInstance(response.context['questionform'], QuestionForm)
        self.assertEqual(response.context['heading'], "Edit Subquestion")
        self.assertEqual(self.sub_question.text, response.context['questionform'].initial['text'])
        self.assertEqual(self.sub_question.answer_type, response.context['questionform'].initial['answer_type'])
        self.assertEqual(self.sub_question.group.id, response.context['questionform'].initial['group'])
        self.assertIsNotNone(response.context['questionform'].errors)

    def test_should_post_edit_subquestion(self):
        subquestion_form_data = {
            'module': self.module.id,
            'text': "Edited subquestion text",
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.group.id
        }
        expected_url = '/questions/'
        self.failIf(Question.objects.filter(**subquestion_form_data))
        response = self.client.post('/questions/%d/sub_questions/edit/' % int(self.sub_question.id),
                                    data=subquestion_form_data)
        edited_sub_question = Question.objects.filter(**subquestion_form_data)
        self.failUnless(edited_sub_question)
        self.failIf(Question.objects.filter(text=self.sub_question.text, answer_type=Question.NUMBER,
                                            subquestion=True, parent=self.question))
        success_message = "Sub question successfully edited."
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_edit_sub_question_redirects_to_master_questions_if_batch_is_not_present(self):
        subquestion_form_data = {
            'module': self.module.id,
            'text': "edited text for subqn",
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.group.id
        }
        expected_url = '/questions/'
        response = self.client.post('/questions/%d/sub_questions/edit/' % int(self.sub_question.id),
                                    data=subquestion_form_data)

        self.assertRedirects(response, expected_url, 302, 200)

    def test_edit_sub_question_redirects_to_batch_questions_if_batch_is_not_present(self):
        subquestion_form_data = {
            'module': self.module.id,
            'text': "edited text for subqn",
            'identifier': 'ID 1',
            'answer_type': Question.NUMBER,
            'group': self.group.id
        }
        expected_url = '/batches/%s/questions/' % self.batch.id
        response = self.client.post(
            '/batches/%s/questions/%s/sub_questions/edit/' % (self.batch.id, self.sub_question.id),
            data=subquestion_form_data)

        self.assertRedirects(response, expected_url, 302, 200)

    def test_restricted_permissions_for_edit_sub_questions(self):
        self.assert_restricted_permission_for(
            '/batches/%s/questions/%s/sub_questions/edit/' % (self.batch.id, self.sub_question.id))
        self.assert_restricted_permission_for('/questions/%d/sub_questions/edit/' % self.sub_question.id)

class DeleteLogicViewsTest(BaseTest):
    def setUp(self):
        self.client = Client()
        self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                  'can_view_batches')
        self.client.login(username='User', password='password')

        self.batch = Batch.objects.create(order=1)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1, identifier='Q1')
        self.question.batches.add(self.batch)
        self.answer_rule = AnswerRule.objects.create(question=self.question, condition=AnswerRule.CONDITIONS['EQUALS'],
                                                     action=AnswerRule.ACTIONS['END_INTERVIEW'], validate_with_value=0)

    def test_restricted_permissions_for_delete_question(self):
        self.assert_restricted_permission_for(
            '/batches/%s/questions/delete_logic/%s/' % (self.batch.id, self.question.id))

    def test_knows_how_to_delete_logic_given_valid_question_id_and_logic_id(self):
        response = self.client.get(
            '/batches/%s/questions/delete_logic/%d/' % (int(self.batch.id), int(self.answer_rule.id)))
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.id, 302, 200)
        self.failIf(AnswerRule.objects.filter(id=self.answer_rule.id))

class RemoveQuestionFromBatchTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')

        self.batch = Batch.objects.create(order=1)
        self.batch_2 = Batch.objects.create(order=2)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1, identifier='Q1')
        self.question.batches.add(self.batch)
        self.question.batches.add(self.batch_2)

        BatchQuestionOrder.objects.create(question=self.question, batch=self.batch, order=1)
        BatchQuestionOrder.objects.create(question=self.question, batch=self.batch_2, order=1)

    def test_should_remove_question_from_batch_when_remove_url_is_called(self):
        response = self.client.get('/batches/%s/questions/%s/remove/' % (int(self.batch.id), int(self.question.id)))
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.id, 302, 200)

        updated_question = Question.objects.filter(id=self.question.id)
        self.failUnless(updated_question)
        self.assertEqual(1, len(updated_question[0].batches.all()))
        self.assertIn(self.batch_2, updated_question[0].batches.all())
        success_message = 'Question successfully removed from %s.' % self.batch.name
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_should_delete_all_logic_associated_with_question_and_batch_when_removed_from_batch(self):
        group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question = Question.objects.create(text="some qn?", group=group, order=3, identifier='Q3')
        BatchQuestionOrder.objects.create(question=self.question, batch=self.batch, order=1)

        answer_rule = AnswerRule.objects.create(batch=self.batch, question=self.question,
                                                action=AnswerRule.ACTIONS['SKIP_TO'],
                                                condition=AnswerRule.CONDITIONS['EQUALS'],
                                                validate_with_value=0, next_question=question)
        response = self.client.get('/batches/%s/questions/%s/remove/' % (int(self.batch.id), int(self.question.id)))
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.id, 302, 200)
        updated_question = Question.objects.filter(id=self.question.id)
        self.failUnless(updated_question)
        self.assertEqual(1, len(updated_question[0].batches.all()))
        self.assertIn(self.batch_2, updated_question[0].batches.all())
        success_message = 'Question successfully removed from %s.' % self.batch.name
        self.assertIn(success_message, response.cookies['messages'].value)
        update_answer_rule = AnswerRule.objects.filter(question=self.question, next_question=question,
                                                       id=answer_rule.id)
        self.assertEqual(0, len(updated_question[0].rule.all()))
        self.assertEqual(0, len(update_answer_rule))

    def test_should_retain_logic_attached_to_the_question_in_other_batches(self):
        batch = Batch.objects.create(name="Another Batch", order=2)
        group = HouseholdMemberGroup.objects.create(name="0 to 6 years", order=0)
        question = Question.objects.create(text="some qn?", group=group, order=3, identifier='Q3')
        AnswerRule.objects.create(batch=self.batch, question=self.question,
                                  action=AnswerRule.ACTIONS['SKIP_TO'],
                                  condition=AnswerRule.CONDITIONS['EQUALS'],
                                  validate_with_value=0, next_question=question)
        answer_rule_two = AnswerRule.objects.create(batch=batch, question=self.question,
                                                    action=AnswerRule.ACTIONS['END_INTERVIEW'],
                                                    condition=AnswerRule.CONDITIONS['EQUALS'],
                                                    validate_with_value=0)
        answer_rule_three = AnswerRule.objects.create(batch=self.batch_2, question=self.question,
                                                      action=AnswerRule.ACTIONS['END_INTERVIEW'],
                                                      condition=AnswerRule.CONDITIONS['EQUALS'],
                                                      validate_with_value=0)

        self.question.batches.add(batch)

        response = self.client.get('/batches/%s/questions/%s/remove/' % (int(self.batch.id), int(self.question.id)))
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.id, 302, 200)
        updated_question = Question.objects.filter(id=self.question.id)
        self.failUnless(updated_question)
        self.assertIn(self.question, batch.questions.all())
        self.assertEqual(self.question, answer_rule_two.question)
        self.assertEqual(batch, answer_rule_two.batch)
        self.assertEqual(self.batch_2, answer_rule_three.batch)
        self.assertEqual(self.question, answer_rule_three.question)

    def test_restricted_permissions(self):
        self.assert_restricted_permission_for('/batches/%d/questions/%s/remove/' % (self.batch.id, self.question.id))

class DeleteSubQuestionFromBatchTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')

        self.batch = Batch.objects.create(order=1)
        self.batch_2 = Batch.objects.create(order=2)
        self.question = Question.objects.create(text="Question 1?",
                                                answer_type=Question.NUMBER, order=1, identifier='Q1')
        self.question.batches.add(self.batch)
        self.question.batches.add(self.batch_2)
        self.subquestion = Question.objects.create(text="Sub Question 1?", parent=self.question, subquestion=True,
                                                   answer_type=Question.NUMBER, identifier='Q13')

    def test_should_delete_subquestion_and_redirect_to_batch_question_lists_if_batch_id_supplied(self):
        response = self.client.get('/batches/%s/questions/%s/delete/' % (int(self.batch.id), int(self.subquestion.id)))
        self.assertRedirects(response, '/batches/%s/questions/' % self.batch.id, 302, 200)

        success_message = 'Sub question successfully deleted.'
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_should_delete_subquestion_and_redirect_to_master_question_lists_if_no_batch_id_supplied(self):
        response = self.client.get('/questions/%s/delete/' % (int(self.subquestion.id)))
        self.assertRedirects(response, '/questions/', 302, 200)

        success_message = 'Sub question successfully deleted.'
        self.assertIn(success_message, response.cookies['messages'].value)

    def test_restricted_permissions(self):
        self.assert_restricted_permission_for('/batches/%d/questions/%s/delete/' % (self.batch.id, self.subquestion.id))
        self.assert_restricted_permission_for('/questions/%s/delete/' % (self.subquestion.id))


class ExportAllQuestionsTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')

        self.member_group = HouseholdMemberGroup.objects.create(name="old people", order=0)
        self.question1 = Question.objects.create(text="Question 1?", group=self.member_group,
                                                answer_type=Question.NUMBER, order=1, identifier='Q1')
        self.question2 = Question.objects.create(text="Question 2?", group=self.member_group,
                                                answer_type=Question.TEXT, order=2, identifier='Q2')
        self.question3 = Question.objects.create(text="Question 3?", group=self.member_group,
                                                answer_type=Question.MULTICHOICE, order=3, identifier='Q3')
        self.option1 = QuestionOption.objects.create(question=self.question3, text="option1", order=1)
        self.option2 = QuestionOption.objects.create(question=self.question3, text="option2", order=2)
        self.option3 = QuestionOption.objects.create(question=self.question3, text="option3", order=3)

        self.headings = "Question Text; Group; Answer Type; Options"
        self.url = '/questions/export/'

    def test_GET_should_redirect_to_referer_url_upon_success(self):
        referer_url = '/questions/'
        meta = {'HTTP_REFERER': referer_url}
        response = self.client.get(self.url, data={}, **meta)
        self.assertRedirects(response, referer_url)

    def test_downloaded_questions_file(self):
        file_name = "all_questions.csv"

        response = self.client.post(self.url, data={})

        self.assertEquals(response.get('Content-Type'), "text/csv")
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename="%s"' % file_name)


        question1 = "%s; %s; %s" %(self.question1.text, self.question1.group.name, self.question1.answer_type.upper())
        question2 = "%s; %s; %s" %(self.question2.text, self.question2.group.name, self.question2.answer_type.upper())
        question3_1 = "%s; %s; %s; %s" %(self.question3.text, self.question3.group.name,
                                         self.question3.answer_type.upper(), self.option1.text)
        question3_2 = "; ; ; %s" %(self.option2.text)
        question3_3 = "; ; ; %s" %(self.option3.text)
        contents = "%s\r\n%s\r\n%s\r\n%s\r\n%s\r\n%s" % (self.headings, question1, question2, question3_1, question3_2, question3_3)
        self.assertEquals(contents, response.content)

    def test_restricted_permissions(self):
        self.assert_restricted_permission_for(self.url)


class ExportBatchQuestionsTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_with_permission = self.assign_permission_to(User.objects.create_user('User', 'user@test.com', 'password'),
                                                         'can_view_batches')
        self.client.login(username='User', password='password')

        self.member_group = HouseholdMemberGroup.objects.create(name="old people", order=0)
        self.question1 = Question.objects.create(text="Question 1?", group=self.member_group,
                                                answer_type=Question.NUMBER, order=1, identifier='Q1')
        self.question2 = Question.objects.create(text="Question 2?", group=self.member_group,
                                                answer_type=Question.TEXT, order=2, identifier='Q2')
        self.question3 = Question.objects.create(text="Question 3?", group=self.member_group,
                                                answer_type=Question.MULTICHOICE, order=3, identifier='Q3')
        self.option1 = QuestionOption.objects.create(question=self.question3, text="option1", order=1)
        self.option2 = QuestionOption.objects.create(question=self.question3, text="option2", order=2)
        self.option3 = QuestionOption.objects.create(question=self.question3, text="option3", order=3)

        self.batch = Batch.objects.create(name="batch", order=0)
        self.batch.questions.add(self.question1, self.question2, self.question3)

        self.headings = "Question Text; Group; Answer Type; Options"
        self.url = '/batches/%d/questions/export/'%self.batch.id

    def test_GET_should_redirect_to_referer_url_upon_success(self):
        referer_url = '/batches/%d/questions/'%self.batch.id
        meta = {'HTTP_REFERER': referer_url}
        response = self.client.get(self.url, data={}, **meta)
        self.assertRedirects(response, referer_url)

    def test_downloaded_questions_file(self):
        self.create_questions_not_in_batch()

        file_name = "%s_questions.csv"%self.batch.name

        response = self.client.post(self.url, data={})

        self.assertEquals(response.get('Content-Type'), "text/csv")
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename="%s"' % file_name)


        question1 = "%s; %s; %s" %(self.question1.text, self.question1.group.name, self.question1.answer_type.upper())
        question2 = "%s; %s; %s" %(self.question2.text, self.question2.group.name, self.question2.answer_type.upper())
        question3_1 = "%s; %s; %s; %s" %(self.question3.text, self.question3.group.name,
                                         self.question3.answer_type.upper(), self.option1.text)
        question3_2 = "; ; ; %s" %(self.option2.text)
        question3_3 = "; ; ; %s" %(self.option3.text)
        contents = "%s\r\n%s\r\n%s\r\n%s\r\n%s\r\n%s" % (self.headings, question1, question2, question3_1, question3_2, question3_3)
        self.assertEquals(contents, response.content)

    def test_restricted_permissions(self):
        self.assert_restricted_permission_for(self.url)
