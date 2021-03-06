import json
import re
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import permission_required
from survey.forms.logic import LogicForm
from survey.forms.filters import QuestionFilterForm, MAX_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE, DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE
from survey.models import AnswerRule, BatchQuestionOrder
from survey.models.batch import Batch
from survey.models.question import Question, QuestionOption
from survey.forms.question import QuestionForm
from survey.services.export_questions import ExportQuestionsService
from survey.utils.views_helper import prepend_to_keys, clean_query_params
from survey.views.custom_decorators import not_allowed_when_batch_is_open
from collections import OrderedDict

ADD_LOGIC_ON_OPEN_BATCH_ERROR_MESSAGE = "Logics cannot be added while the batch is open."
ADD_SUBQUESTION_ON_OPEN_BATCH_ERROR_MESSAGE = "Subquestions cannot be added while batch is open."
REMOVE_QUESTION_FROM_OPEN_BATCH_ERROR_MESSAGE = "Question cannot be removed from a batch while the batch is open."


def _get_questions_based_on_filter(batch_id, filter_params):
    filter_params = clean_query_params(filter_params)
    if batch_id:
        filter_params = prepend_to_keys(filter_params, 'question__')
        return BatchQuestionOrder.get_batch_order_specific_questions(batch_id, filter_params)
    return Question.objects.filter(subquestion=False, **filter_params).exclude(group__name='REGISTRATION GROUP')


def _max_number_of_question_per_page(number_sent_in_request):
    max_question_per_page_supplied = number_sent_in_request or 0
    given_max_per_page = min(int(max_question_per_page_supplied), MAX_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE)
    return max(given_max_per_page, DEFAULT_NUMBER_OF_QUESTION_DISPLAYED_PER_PAGE)


def _questions_given(batch_id, request):
    filter_params = {'group__id': request.GET.get('groups', None), 'module__id': request.GET.get('modules', None),
                     'answer_type': request.GET.get('question_types', None)}
    max_per_page = _max_number_of_question_per_page(request.GET.get('number_of_questions_per_page', 0))

    return _get_questions_based_on_filter(batch_id, filter_params), max_per_page


@permission_required('auth.can_view_batches')
def index(request, batch_id):
    batch = Batch.objects.get(id=batch_id) if batch_id else None

    question_filter_form = QuestionFilterForm(data=request.GET)
    questions, max_per_page = _questions_given(batch_id, request)

    if not questions:
        messages.error(request, 'There are no questions associated with this batch yet.')

    question_rules_for_batch = {}

    if batch:
        for question in questions:
            question_rules_for_batch[question] = question.rules_for_batch(batch)

    context = {'questions': questions, 'request': request, 'batch': batch, 'max_question_per_page':max_per_page,
               'question_filter_form': question_filter_form, 'rules_for_batch': question_rules_for_batch}
    return render(request, 'questions/index.html', context)

@permission_required('auth.can_view_batches')
def filter_by_group_and_module(request, batch_id, group_id, module_id):
    filter_params = clean_query_params({'group__id': group_id, 'module__id': module_id})
    questions = Question.objects.filter(**filter_params).exclude(batches__id=batch_id).values('id', 'text', 'answer_type').order_by('text')
    json_dump = json.dumps(list(questions), cls=DjangoJSONEncoder)
    return HttpResponse(json_dump, mimetype='application/json')

@permission_required('auth.can_view_batches')
def list_all_questions(request):
    batch_id = request.GET.get('batch_id', None)

    question_filter_form = QuestionFilterForm(data=request.GET)
    questions, max_per_page = _questions_given(batch_id, request)

    context = {'questions': questions, 'request': request, 'question_filter_form': question_filter_form,
               'rules_for_batch': {}, 'max_question_per_page': max_per_page}
    return render(request, 'questions/index.html', context)


def _sub_question_hash(sub_question):
    return {'id': str(sub_question.id), 'text': sub_question.text}


def __process_sub_question_form(request, questionform, parent_question, action_performed, batch_id=None):
    if questionform.is_valid():
        redirect_url = '/batches/%s/questions/' % batch_id if batch_id else '/questions/'

        sub_question = questionform.save(commit=False)
        sub_question.subquestion = True
        sub_question.parent = parent_question
        sub_question.group = parent_question.group
        sub_question.save()

        if request.is_ajax():
            return HttpResponse(json.dumps(_sub_question_hash(sub_question)))
        else:
            messages.success(request, 'Sub question successfully %s.' % action_performed)
            return HttpResponseRedirect(redirect_url)
    else:
        messages.error(request, 'Sub question not saved.')


@permission_required('auth.can_view_batches')
@not_allowed_when_batch_is_open(message=ADD_SUBQUESTION_ON_OPEN_BATCH_ERROR_MESSAGE,
                                redirect_url_name="batch_questions_page", url_kwargs_keys=['batch_id'])
def new_subquestion(request, question_id, batch_id=None):
    parent_question = Question.objects.get(pk=question_id)
    questionform = QuestionForm(parent_question=parent_question)
    response = None
    if request.method == 'POST':
        questionform = QuestionForm(request.POST, parent_question=parent_question)
        response = __process_sub_question_form(request, questionform, parent_question, 'added', batch_id)
    context = {'questionform': questionform, 'button_label': 'Create', 'id': 'add-sub_question-form',
               'cancel_url': '/questions/', 'parent_question': parent_question, 'class': 'question-form',
               'heading': 'Add SubQuestion'}

    template_name = 'questions/new.html'
    if request.is_ajax():
        template_name = 'questions/_add_question.html'

    return response or render(request, template_name, context)

@permission_required('auth.can_view_batches')
def edit_subquestion(request, question_id, batch_id=None):
    question = Question.objects.get(pk=question_id)
    questionform = QuestionForm(instance=question)
    response = None
    if request.method == 'POST':
        questionform = QuestionForm(request.POST, instance=question)
        response = __process_sub_question_form(request, questionform, question.parent, 'edited', batch_id)
    context = {'questionform': questionform, 'button_label': 'Save', 'id': 'add-sub_question-form',
               'cancel_url': '/questions/', 'parent_question': question.parent, 'class': 'question-form',
               'heading': 'Edit Subquestion'}

    template_name = 'questions/new.html'

    return response or render(request, template_name, context)

def _get_post_values(post_data):
    next_question_key = post_data.get('next_question', None)
    option_key = post_data.get('option', None)
    question_key = post_data.get('validate_with_question', None)
    condition_response = post_data.get('condition', None)
    value_key = post_data.get('value', None)
    value_min_key = post_data.get('min_value', None)
    value_max_key = post_data.get('max_value', None)

    save_data = {'action': post_data['action'],
                 'condition': condition_response or 'EQUALS_OPTION',
                 'next_question': Question.objects.get(id=next_question_key) if next_question_key else None,
                 'validate_with_option': QuestionOption.objects.get(id=option_key) if option_key else None,
                 'validate_with_question': Question.objects.get(id=question_key) if question_key else None
    }
    if value_key:
        save_data['validate_with_value'] = value_key

    if value_min_key:
        save_data['validate_with_min_value'] = value_min_key

    if value_max_key:
        save_data['validate_with_max_value'] = value_max_key

    return save_data

def _rule_exists(question, batch, **kwargs):
    return AnswerRule.objects.filter(question=question, batch=batch, **kwargs).count() > 0


@permission_required('auth.can_view_batches')
@not_allowed_when_batch_is_open(message=ADD_LOGIC_ON_OPEN_BATCH_ERROR_MESSAGE,
                                redirect_url_name="batch_questions_page", url_kwargs_keys=['batch_id'])
def add_logic(request, batch_id, question_id):
    question = Question.objects.get(id=question_id)
    batch = Batch.objects.get(id=batch_id)
    logic_form = LogicForm(question=question, batch=batch)
    response = None
    question_rules_for_batch = {}
    question_rules_for_batch[question] = question.rules_for_batch(batch)

    if request.method == "POST":
        logic_form = LogicForm(data=request.POST, question=question, batch=batch)
        if logic_form.is_valid():
            AnswerRule.objects.create(question=question, batch=batch, **_get_post_values(request.POST))
            messages.success(request, 'Logic successfully added.')
            response = HttpResponseRedirect('/batches/%s/questions/' % batch_id)

    context = {'logic_form': logic_form, 'button_label': 'Save', 'question': question,
               'rules_for_batch': question_rules_for_batch,
               'questionform': QuestionForm(parent_question=question),
               'modal_action': '/questions/%s/sub_questions/new/' % question.id,
               'class': 'question-form', 'batch_id': batch_id, 'batch': batch,
               'cancel_url': '/batches/%s/questions/' % batch_id}
    return response or render(request, "questions/logic.html", context)

@permission_required('auth.can_view_batches')
def new(request):
    response, context = _render_question_view(request)
    return response or render(request, 'questions/new.html', context)


def is_multichoice(request, question_id):
    is_multichoice_type = False
    question_options = []

    try:
        question = Question.objects.get(id=question_id)
        is_multichoice_type = question.is_multichoice()
        if is_multichoice_type:
            all_options = question.options.all().order_by('order')
            for option in all_options:
                question_options.append({'id': option.id, 'text': option.text})

    except Question.DoesNotExist:
        pass

    is_multichoice_question = [{'is_multichoice': is_multichoice_type, 'question_options': question_options}]
    return HttpResponse(json.dumps(is_multichoice_question), mimetype='application/json')

@permission_required('auth.can_view_batches')
def edit(request, question_id):
    question = Question.objects.filter(id=question_id)
    if not question:
        messages.error(request, "Question does not exist.")
        return HttpResponseRedirect('/questions/')
    response, context = _render_question_view(request, question[0])
    return response or render(request, 'questions/new.html', context)

@permission_required('auth.can_view_batches')
def delete(request, question_id, batch_id=None):
    question = Question.objects.filter(pk=question_id)
    redirect_url = '/batches/%s/questions/' % batch_id if batch_id else '/questions/'
    if question:
        success_message = "%s successfully deleted."
        messages.success(request, success_message % ("Sub question" if question[0].subquestion else "Question"))
    else:
        messages.error(request, "Question / Subquestion does not exist.")
    question.delete()
    return HttpResponseRedirect(redirect_url)


def _process_question_form(request, options, response, instance=None):
    question_form = QuestionForm(data=request.POST, instance=instance)
    action_str = 'edit' if instance else 'add'
    if question_form.is_valid():
        question_form.save(**request.POST)
        messages.success(request, 'Question successfully %sed.' % action_str)
        response = HttpResponseRedirect('/questions/')
    else:
        messages.error(request, 'Question was not %sed.' % action_str)
        options = dict(request.POST).get('options', None)
    return response, options, question_form


def _render_question_view(request, instance=None):
    question_form = QuestionForm(instance=instance)
    button_label = 'Create'
    options = None
    response = None
    if instance:
        button_label = 'Save'
        options = instance.options.all()
        options = [option.text for option in options] if options else None

    if request.method == 'POST':
        response, options, question_form = _process_question_form(request, options, response, instance)

    context = {'button_label': button_label,
               'id': 'add-question-form',
               'request': request,
               'class': 'question-form',
               'cancel_url': '/questions/',
               'questionform': question_form}

    if options:
        options = filter(lambda text: text.strip(), list(OrderedDict.fromkeys(options)))
        options = map(lambda option: re.sub("[%s]" % Question.IGNORED_CHARACTERS, '', option), options)
        context['options'] = map(lambda option: re.sub("  ", ' ', option), options)

    return response, context

def _create_question_hash_response(questions):
    questions_to_display = map(lambda question: {'id': str(question.id), 'text': question.text}, questions)
    return HttpResponse(json.dumps(questions_to_display), mimetype='application/json')

def get_questions_for_batch(request, batch_id, question_id):
    batch = Batch.objects.get(id=batch_id)
    questions = batch.questions.filter(subquestion=False).exclude(id=question_id)
    return _create_question_hash_response(questions)

def get_sub_questions_for_question(request, question_id):
    question = Question.objects.get(id=question_id)
    return _create_question_hash_response(question.get_subquestions())

@permission_required('auth.can_view_batches')
def delete_logic(request, batch_id, answer_rule_id):
    rule = AnswerRule.objects.get(id=answer_rule_id)
    rule.delete()
    messages.success(request, "Logic successfully deleted.")
    return HttpResponseRedirect('/batches/%s/questions/' % batch_id)


@permission_required('auth.can_view_batches')
@not_allowed_when_batch_is_open(message=REMOVE_QUESTION_FROM_OPEN_BATCH_ERROR_MESSAGE,
                                redirect_url_name="batch_questions_page", url_kwargs_keys=['batch_id'])
def remove(request, batch_id, question_id):
    batch = Batch.objects.get(id=batch_id)
    question = Question.objects.get(id=question_id, batches__id=batch_id)
    AnswerRule.objects.filter(question=question, batch=batch).delete()
    question.de_associate_from(batch)
    messages.success(request, "Question successfully removed from %s." % batch.name)
    return HttpResponseRedirect('/batches/%s/questions/' % batch_id)

@permission_required('auth.can_view_batches')
def export_all_questions(request):
    return _export_questions(request)

@permission_required('auth.can_view_batches')
def export_batch_questions(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    return _export_questions(request, batch)


def _export_questions(request, batch=None):
    filename = '%s_questions' % batch.name if batch else 'all_questions'
    if request.method == 'POST':
        formatted_responses = ExportQuestionsService(batch).formatted_responses()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename
        response.write("\r\n".join(formatted_responses))
        return response

    referrer_url = request.META.get('HTTP_REFERER', None)
    return HttpResponseRedirect(referrer_url)

