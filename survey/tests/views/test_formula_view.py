from django.contrib.auth.models import User
from survey.forms.formula import FormulaForm
from survey.models import Survey, Batch, QuestionModule, Indicator, Formula, HouseholdMemberGroup, Question, BatchQuestionOrder, QuestionOption
from survey.tests.base_test import BaseTest
from django.test.client import Client


class IndicatorFormulaViewsTest(BaseTest):
    def setUp(self):
        self.client = Client()
        user_without_permission = User.objects.create_user(username='useless', email='rajni@kant.com',
                                                           password='I_Suck')
        raj = self.assign_permission_to(User.objects.create_user('Rajni', 'rajni@kant.com', 'I_Rock'),
                                        'can_view_batches')
        raj = self.assign_permission_to(raj, 'can_view_investigators')

        self.client.login(username='Rajni', password='I_Rock')
        self.survey = Survey.objects.create(name='survey name', description='survey descrpition', type=False,
                                            sample_size=10)
        self.batch = Batch.objects.create(order=1, name="Batch A", survey=self.survey)
        self.module = QuestionModule.objects.create(name='Education', description='Educational Module')
        self.indicator = Indicator.objects.create(name='Test Indicator', measure=Indicator.MEASURE_CHOICES[0][1],
                                             module=self.module, description="Indicator 1", batch=self.batch)

        self.group = HouseholdMemberGroup.objects.create(name="Females", order=1)

        self.question_1 = Question.objects.create(group=self.group, text="Question 1?", module=self.module, answer_type=Question.NUMBER,
                                             order=1)
        self.question_2 = Question.objects.create(group=self.group, text="Question 2?", module=self.module, answer_type=Question.NUMBER,
                                             order=2)
        self.question_3 = Question.objects.create(group=self.group, text="Question 3?", module=self.module, answer_type=Question.NUMBER,
                                             order=3)

        self.question_1.batches.add(self.batch)
        self.question_2.batches.add(self.batch)
        self.question_3.batches.add(self.batch)

        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question_1, order=1)
        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question_2, order=2)
        BatchQuestionOrder.objects.create(batch=self.batch, question=self.question_3, order=3)

        self.existing_formula = Formula.objects.create(numerator=self.question_1, denominator=self.question_2,
                                                       indicator=self.indicator)

    def test_get_new(self):
        response = self.client.get('/indicators/%s/formula/new/' % self.indicator.id)
        self.failUnlessEqual(response.status_code, 200)
        templates = [template.name for template in response.templates]
        self.assertIn('formula/new.html', templates)
        self.assertEquals('/indicators/%s/formula/new/' % self.indicator.id, response.context['action'])
        self.assertEquals('/indicators/', response.context['cancel_url'])
        self.assertEquals(self.indicator, response.context['indicator'])
        self.assertEquals('Formula for Indicator %s' % self.indicator.name, response.context['title'])
        self.assertEquals('Create', response.context['button_label'])
        self.assertIn(self.existing_formula, response.context['existing_formula'])
        self.assertIsInstance(response.context['formula_form'], FormulaForm)

    def test_get_knows_to_throw_error_message_if_indicator_does_not_exist(self):
        response = self.client.get('/indicators/%s/formula/new/' % 200)

        message = "The indicator requested does not exist."

        self.failUnlessEqual(response.status_code, 302)
        self.assertRedirects(response, '/indicators/', 302, 200)
        self.assertIn(message, response.cookies['messages'].value)

    def test_post_new_for_percentage_indicator(self):
        data = {'numerator': self.question_1.id,
                'denominator': self.question_3.id,
                'denominator_type': 'QUESTION'}

        new_formula_url = '/indicators/%s/formula/new/' % self.indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % self.indicator.name

        self.assertIn(message, response.content)
        self.failUnless(Formula.objects.filter(numerator=self.question_1, denominator=self.question_3,
                                               indicator=self.indicator))

    def test_post_new_for_percentage_indicator_with_multichoice_denominator_question(self):
        multichoice_question = Question.objects.create(group=self.group, text="Question 4?", module=self.module,
                                                  answer_type=Question.MULTICHOICE, order=4)

        option_1 = QuestionOption.objects.create(question=multichoice_question, text='Yes', order=1)
        option_2 = QuestionOption.objects.create(question=multichoice_question, text='No', order=2)
        option_3 = QuestionOption.objects.create(question=multichoice_question, text='Maybe', order=3)
        option_4 = QuestionOption.objects.create(question=multichoice_question, text='Not Known', order=4)

        data = {'numerator': self.question_1.id,
                'denominator': multichoice_question.id,
                'denominator_options': [option_1.id, option_2.id, option_3.id, option_4.id],
                'denominator_type': 'QUESTION'}

        all_formula_options = [option_1, option_2, option_3, option_4]

        multichoice_question.batches.add(self.batch)
        BatchQuestionOrder.objects.create(batch=self.batch, question=multichoice_question, order=4)

        new_formula_url = '/indicators/%s/formula/new/' % self.indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % self.indicator.name

        self.assertIn(message, response.content)
        saved_formula = Formula.objects.filter(numerator=self.question_1, denominator=multichoice_question,
                                               indicator=self.indicator)
        saved_formula_question_options = saved_formula[0].denominator_options.all()

        self.failUnless(saved_formula)
        [self.assertIn(option, saved_formula_question_options) for option in all_formula_options]

    def test_post_new_for_percentage_indicator_with_multichoice_numerator_question(self):
        multichoice_question = Question.objects.create(group=self.group, text="Question 4?", module=self.module,
                                                  answer_type=Question.MULTICHOICE, order=4)

        option_1 = QuestionOption.objects.create(question=multichoice_question, text='Yes', order=1)
        option_2 = QuestionOption.objects.create(question=multichoice_question, text='No', order=2)
        option_3 = QuestionOption.objects.create(question=multichoice_question, text='Maybe', order=3)
        option_4 = QuestionOption.objects.create(question=multichoice_question, text='Not Known', order=4)

        data = {'numerator': multichoice_question.id,
                'denominator': self.question_2.id,
                'numerator_options': [option_1.id, option_2.id, option_3.id, option_4.id],
                'denominator_type': 'QUESTION'}

        all_formula_options = [option_1, option_2, option_3, option_4]

        multichoice_question.batches.add(self.batch)
        BatchQuestionOrder.objects.create(batch=self.batch, question=multichoice_question, order=4)

        new_formula_url = '/indicators/%s/formula/new/' % self.indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % self.indicator.name

        self.assertIn(message, response.content)
        saved_formula = Formula.objects.filter(numerator=multichoice_question, denominator=self.question_2,
                                               indicator=self.indicator)

        saved_formula_question_options = saved_formula[0].numerator_options.all()

        self.failUnless(saved_formula)
        [self.assertIn(option, saved_formula_question_options) for option in all_formula_options]

    def test_post_new_for_percentage_indicator_with_multichoice_numerator_and_denominator_question(self):
        multichoice_question = Question.objects.create(group=self.group, text="Question 4?", module=self.module,
                                                  answer_type=Question.MULTICHOICE, order=4)

        option_1 = QuestionOption.objects.create(question=multichoice_question, text='Yes', order=1)
        option_2 = QuestionOption.objects.create(question=multichoice_question, text='No', order=2)
        option_3 = QuestionOption.objects.create(question=multichoice_question, text='Maybe', order=3)
        option_4 = QuestionOption.objects.create(question=multichoice_question, text='Not Known', order=4)

        data = {'numerator': multichoice_question.id,
                'denominator': multichoice_question.id,
                'numerator_options': [option_1.id, option_2.id],
                'denominator_options': [option_1.id, option_2.id, option_3.id, option_4.id],
                'denominator_type': 'QUESTION'}

        all_numerator_formula_options = [option_1, option_2]
        excluded_numerator_formula_options = [option_3, option_4]
        all_denominator_formula_options = [option_1, option_2, option_3, option_4]

        multichoice_question.batches.add(self.batch)
        BatchQuestionOrder.objects.create(batch=self.batch, question=multichoice_question, order=4)

        new_formula_url = '/indicators/%s/formula/new/' % self.indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % self.indicator.name

        self.assertIn(message, response.content)
        saved_formula = Formula.objects.filter(numerator=multichoice_question, denominator=multichoice_question,
                                               indicator=self.indicator)

        saved_numerator_question_options = saved_formula[0].numerator_options.all()
        saved_denominator_question_options = saved_formula[0].denominator_options.all()

        self.failUnless(saved_formula)
        [self.assertIn(option, saved_numerator_question_options) for option in all_numerator_formula_options]
        [self.assertNotIn(option, saved_numerator_question_options) for option in excluded_numerator_formula_options]
        [self.assertIn(option, saved_denominator_question_options) for option in all_denominator_formula_options]

    def test_post_new_for_count_indicator(self):
        data = {'count': self.question_2.id,
                'denominator_type': 'QUESTION'}

        count_indicator = Indicator.objects.create(name='Test Indicator', measure=Indicator.MEASURE_CHOICES[1][1],
                                             module=self.module, description="Indicator 1", batch=self.batch)

        new_formula_url = '/indicators/%s/formula/new/' % count_indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % count_indicator.name

        self.assertIn(message, response.content)
        self.failUnless(Formula.objects.filter(count=self.question_2, indicator=count_indicator))

    def test_post_new_for_count_indicator_with_group_as_count_option(self):
        data = {'groups': self.group.id,
                'denominator_type': 'GROUP'}

        count_indicator = Indicator.objects.create(name='Test Indicator', measure=Indicator.MEASURE_CHOICES[1][1],
                                             module=self.module, description="Indicator 1", batch=self.batch)

        new_formula_url = '/indicators/%s/formula/new/' % count_indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % count_indicator.name

        self.assertIn(message, response.content)
        saved_formula = Formula.objects.filter(groups=self.group, indicator=count_indicator)

        self.failUnless(saved_formula)
        self.assertEqual(self.group, saved_formula[0].groups)
        self.assertIsNone(saved_formula[0].count)
        self.assertIsNone(saved_formula[0].numerator)
        self.assertIsNone(saved_formula[0].denominator)
        self.assertEqual(0, len(saved_formula[0].numerator_options.all()))
        self.assertEqual(0, len(saved_formula[0].denominator_options.all()))

    def test_post_new_for_count_indicator_with_multichoice_count_question(self):
        multichoice_question = Question.objects.create(group=self.group, text="Question 4?", module=self.module,
                                                  answer_type=Question.MULTICHOICE, order=4)

        option_1 = QuestionOption.objects.create(question=multichoice_question, text='Yes', order=1)
        option_2 = QuestionOption.objects.create(question=multichoice_question, text='No', order=2)
        option_3 = QuestionOption.objects.create(question=multichoice_question, text='Maybe', order=3)
        option_4 = QuestionOption.objects.create(question=multichoice_question, text='Not Known', order=4)

        count_indicator = Indicator.objects.create(name='Test Indicator', measure=Indicator.MEASURE_CHOICES[1][1],
                                             module=self.module, description="Indicator 1", batch=self.batch)

        data = {'count': multichoice_question.id,
                'denominator_options': [option_1.id, option_2.id, option_3.id, option_4.id],
                'denominator_type': 'QUESTION'}

        all_formula_options = [option_1, option_2, option_3, option_4]

        multichoice_question.batches.add(self.batch)
        BatchQuestionOrder.objects.create(batch=self.batch, question=multichoice_question, order=4)

        new_formula_url = '/indicators/%s/formula/new/' % count_indicator.id
        response = self.client.post(new_formula_url, data=data)
        message = "Formula successfully added to indicator %s." % self.indicator.name

        self.assertIn(message, response.content)
        saved_formula = Formula.objects.filter(count=multichoice_question, indicator=count_indicator)

        self.failUnless(saved_formula)
        saved_formula_question_options = saved_formula[0].denominator_options.all()

        [self.assertIn(option, saved_formula_question_options) for option in all_formula_options]

    def test_delete_removes_formula_and_redirects_to_new_formula_page_with_success_message(self):
        delete_url = '/indicators/%s/formula/%s/delete/' % (self.indicator.id, self.existing_formula.id)
        response = self.client.get(delete_url)

        redirect_url = '/indicators/%s/formula/new/' % self.indicator.id

        self.failIf(Formula.objects.filter(numerator=self.question_1, denominator=self.question_2,
                                                       indicator=self.indicator))
        self.assertIn("Formula successfully deleted.", response.cookies['messages'].value)
        self.assertRedirects(response, redirect_url, 302, 200)

    def test_delete_removes_formula_and_redirects_to_new_formula_page_with_error_message_if_non_existent_formula(self):
        non_existent_formula = '200'
        delete_url = '/indicators/%s/formula/%s/delete/' % (self.indicator.id, non_existent_formula)
        response = self.client.get(delete_url)

        redirect_url = '/indicators/%s/formula/new/' % self.indicator.id
        self.assertIn("Formula for indicator does not exist.", response.cookies['messages'].value)
        self.assertRedirects(response, redirect_url, 302, 200)

    def test_permissions_required(self):
        delete_url = '/indicators/%s/formula/%s/delete/' % (self.indicator.id, self.existing_formula.id)
        self.assert_restricted_permission_for(delete_url)