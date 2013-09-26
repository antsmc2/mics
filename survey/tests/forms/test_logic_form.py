from django.test import TestCase
from survey.forms.logic import LogicForm
from survey.models import Question, Batch, QuestionOption, AnswerRule


class LogicFormTest(TestCase):
    def test_knows_the_fields_in_form(self):
        logic_form = LogicForm()

        fields = ['condition', 'attribute', 'option', 'value', 'validate_with_question', 'action', 'next_question']
        [self.assertIn(field, logic_form.fields) for field in fields]

    def test_does_not_have_value_and_validate_question_if_question_has_options(self):
        fields = ['value', 'validate_with_question']
        batch = Batch.objects.create(order=1)
        question_with_option = Question.objects.create(batch=batch, text="Question 1?",
                                                       answer_type=Question.MULTICHOICE, order=1)

        logic_form = LogicForm(question=question_with_option)
        [self.assertNotIn(field, logic_form.fields) for field in fields]

    def test_does_not_have_option_if_question_does_not_have_options(self):
        field = 'option'
        batch = Batch.objects.create(order=1)
        question_without_option = Question.objects.create(batch=batch, text="Question 1?",
                                                       answer_type=Question.NUMBER, order=1)

        logic_form = LogicForm(question=question_without_option)
        self.assertNotIn(field, logic_form.fields)

    def test_choice_of_attribute_is_value_and_validate_with_question_if_question_does_not_have_options(self):
        batch = Batch.objects.create(order=1)
        question_without_option = Question.objects.create(batch=batch, text="Question 1?",
                                                          answer_type=Question.NUMBER, order=1)
        attribute_choices = [('value', 'Value'), ('validate_with_question', "Question")]
        logic_form = LogicForm(question=question_without_option)
        self.assertEqual(2, len(logic_form.fields['attribute'].choices))
        [self.assertIn(attribute_choice, logic_form.fields['attribute'].choices) for attribute_choice in attribute_choices]

    def test_choice_of_attribute_is_option_if_question_has_options(self):
        batch = Batch.objects.create(order=1)
        question_with_option = Question.objects.create(batch=batch, text="Question 1?",
                                                       answer_type=Question.MULTICHOICE, order=1)

        attribute_choice = ('option', 'Option')
        logic_form = LogicForm(question=question_with_option)
        self.assertEqual(1, len(logic_form.fields['attribute'].choices))
        self.assertIn(attribute_choice, logic_form.fields['attribute'].choices)

    def test_label_of_condition_has_question_text(self):
        field = 'condition'
        batch = Batch.objects.create(order=1)
        question_without_option = Question.objects.create(batch=batch, text="Question 1?",
                                                          answer_type=Question.NUMBER, order=1)

        logic_form = LogicForm(question=question_without_option)
        self.assertIn(question_without_option.text, logic_form.fields[field].label)

    def test_option_field_is_prepopulatad_with_question_options_if_selected_question_is_multi_choice(self):
        field = 'option'
        batch = Batch.objects.create(order=1)
        question_with_option = Question.objects.create(batch=batch, text="Question 1?",
                                                       answer_type=Question.MULTICHOICE, order=1)
        question_option_1 = QuestionOption.objects.create(question=question_with_option, text="Option 1", order=1)
        question_option_2 = QuestionOption.objects.create(question=question_with_option, text="Option 2", order=2)
        question_option_3 = QuestionOption.objects.create(question=question_with_option, text="Option 3", order=3)

        logic_form = LogicForm(question=question_with_option)
        all_options = [question_option_1, question_option_2, question_option_3]
        option_choices = logic_form.fields[field].choices

        self.assertEqual(3, len(option_choices))
        [self.assertIn((question_option.id, question_option.text), option_choices) for question_option in all_options]

    def test_action_field_has_all_actions_on_load_irrespective_of_question(self):
        field = 'action'
        logic_form = LogicForm()
        skip_to = ('SKIP_TO', 'JUMP TO')
        end_interview = ('END_INTERVIEW', 'END INTERVIEW')
        reconfirm = ('REANSWER', 'REANSWER')
        ask_subquestion = ('ASK_SUBQUESTION', 'ASK SUBQUESTION')

        all_actions = [skip_to, end_interview, reconfirm, ask_subquestion]
        action_choices = logic_form.fields[field].choices
        self.assertEqual(4, len(action_choices))
        [self.assertIn(action, action_choices) for action in all_actions]

    def test_choices_for_condition_field_knows_equals_option_is_choice_if_multichoice(self):
        choices_returned = LogicForm().choices_for_condition_field(is_multichoice=True)

        self.assertEqual(1,len(choices_returned))
        self.assertIn(('EQUALS_OPTION', 'EQUALS_OPTION'), choices_returned)
        self.assertNotIn(('EQUALS', 'EQUALS'), choices_returned)

    def test_choices_for_condition_field_does_not_know_equals_option_is_choice_if_not_multichoice(self):
        choices_returned = LogicForm().choices_for_condition_field(is_multichoice=False)

        self.assertEqual(5,len(choices_returned))
        self.assertNotIn(('EQUALS_OPTION', 'EQUALS_OPTION'), choices_returned)

    def test_condition_field_should_have_equals_option_if_multichoice_question(self):
        field = 'condition'
        batch = Batch.objects.create(order=1)
        question_with_option = Question.objects.create(batch=batch, text="Question 1?",
                                                       answer_type=Question.MULTICHOICE, order=1)

        logic_form = LogicForm(question=question_with_option)

        self.assertEqual(1,len(logic_form.fields[field].choices))
        self.assertIn(('EQUALS_OPTION', 'EQUALS_OPTION'), logic_form.fields[field].choices)
        self.assertNotIn(('EQUALS', 'EQUALS'), logic_form.fields[field].choices)

    def test_condition_field_should_not_have_equals_option_if_not_multichoice_question(self):
        field = 'condition'
        batch = Batch.objects.create(order=1)
        question_without_option = Question.objects.create(batch=batch, text="Question 1?",
                                                       answer_type=Question.NUMBER, order=1)

        logic_form = LogicForm(question=question_without_option)

        self.assertEqual(5, len(logic_form.fields[field].choices))
        self.assertNotIn(('EQUALS_OPTION', 'EQUALS_OPTION'), logic_form.fields[field].choices)