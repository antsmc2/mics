import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rapidsms.contrib.locations.models import Location, LocationType
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from survey.investigator_configs import *
from survey.models import HouseholdMemberGroup, QuestionModule, BatchQuestionOrder
from survey.models.surveys import Survey
from survey.models.batch import Batch
from survey.forms.batch import BatchForm, BatchQuestionsForm


@login_required
@permission_required('auth.can_view_batches')
def index(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    batches = Batch.objects.filter(survey__id=survey_id)
    if request.is_ajax():
        batches = batches.values('id', 'name').order_by('name')
        json_dump = json.dumps(list(batches), cls=DjangoJSONEncoder)
        return HttpResponse(json_dump, mimetype='application/json')

    context = {'batches': batches, 'survey': survey,
               'request': request, 'batchform': BatchForm(instance=Batch(survey=survey)),
               'action': '/surveys/%s/batches/new/' % survey_id, }
    return render(request, 'batches/index.html',
                  context)


@login_required
@permission_required('auth.can_view_batches')
def show(request, survey_id, batch_id):
    batch = Batch.objects.get(id=batch_id)
    prime_location_type = LocationType.objects.get(name=PRIME_LOCATION_TYPE)
    locations = Location.objects.filter(type=prime_location_type).order_by('name')
    open_locations = Location.objects.filter(id__in=batch.open_locations.values_list('location_id', flat=True))
    context = {'batch': batch,
               'locations': locations,
               'open_locations': open_locations,
               'non_response_active_locations': batch.get_non_response_active_locations()}
    return render(request, 'batches/show.html', context)


@login_required
@permission_required('auth.can_view_batches')
def open(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    location = Location.objects.get(id=request.POST['location_id'])
    other_surveys = batch.other_surveys_with_open_batches_in(location)

    if other_surveys.count() > 0:
        message = "%s has already open batches from survey %s" % (location.name, other_surveys[0].name)
        return HttpResponse(json.dumps(message), content_type="application/json")
    batch.open_for_location(location)
    return HttpResponse(json.dumps(""), content_type="application/json")


@login_required
@permission_required('auth.can_view_batches')
def close(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    location = Location.objects.get(id=request.POST['location_id'])
    batch.close_for_location(location)
    return HttpResponse(json.dumps(""), content_type="application/json")


@login_required
@permission_required('auth.can_view_batches')
def new(request, survey_id):
    batch = Batch(survey=Survey.objects.get(id=survey_id))
    response, batchform = _process_form(request=request, batchform=(BatchForm(instance=batch)), action_str='added')

    context = {'batchform': batchform, 'button_label': "Create", 'id': 'add-batch-form', 'title': 'New Batch',
               'action': '/surveys/%s/batches/new/' % survey_id, 'cancel_url': '/surveys/'}
    return response or render(request, 'batches/new.html', context)


def _process_form(request, batchform, action_str='added'):
    if request.method == 'POST':
        batchform = BatchForm(data=request.POST, instance=batchform.instance)
        if batchform.is_valid():
            batch = batchform.save()
            _add_success_message(request, action_str)
            batch_list_url = '/surveys/%s/batches/' % str(batch.survey.id)
            return HttpResponseRedirect(batch_list_url), batchform
    return None, batchform


@permission_required('auth.can_view_batches')
def edit(request, survey_id, batch_id):
    batch = Batch.objects.get(id=batch_id, survey__id=survey_id)
    response, batchform = _process_form(request=request, batchform=(BatchForm(instance=batch)), action_str='edited')

    context = {'batchform': batchform, 'button_label': "Save", 'id': 'edit-batch-form', 'title': 'New Batch',
               'action': '/surveys/%s/batches/%s/edit/' % (batch.survey.id, batch.id)}
    return response or render(request, 'batches/new.html', context)


def _add_success_message(request, action_str):
    messages.success(request, 'Batch successfully %s.' % action_str)


@permission_required('auth.can_view_batches')
def delete(request, survey_id, batch_id):
    batch = Batch.objects.get(id=batch_id)
    can_be_deleted, message = batch.can_be_deleted()
    if not can_be_deleted:
        messages.error(request, message)
    else:
        batch.delete()
        _add_success_message(request, 'deleted')
    return HttpResponseRedirect('/surveys/%s/batches/' % survey_id)


@permission_required('auth.can_view_batches')
def assign(request, batch_id):
    batch = Batch.objects.get(id=batch_id)

    if batch.is_open():
        error_message = "Questions cannot be assigned to open batch: %s." % batch.name.capitalize()
        messages.error(request, error_message)
        return HttpResponseRedirect("/batches/%s/questions/" % batch_id)

    batch_questions_form = BatchQuestionsForm(batch=batch)

    groups = HouseholdMemberGroup.objects.all().exclude(name='REGISTRATION GROUP')
    batch = Batch.objects.get(id=batch_id)
    if request.method == 'POST':
        batch_question_form = BatchQuestionsForm(batch=batch, data=request.POST, instance=batch)
        if batch_question_form.is_valid():
            batch_question_form.save()
            success_message = "Questions successfully assigned to batch: %s." % batch.name.capitalize()
            messages.success(request, success_message)
            return HttpResponseRedirect("/batches/%s/questions/" % batch_id)
    all_modules = QuestionModule.objects.all()
    context = {'batch_questions_form': batch_questions_form, 'batch': batch,
               'button_label': 'Save', 'id': 'assign-question-to-batch-form', 'groups': groups,
               'modules': all_modules}
    return render(request, 'batches/assign.html',
                  context)


@permission_required('auth.can_view_batches')
def update_orders(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    new_orders = request.POST.getlist('order_information', None)
    if len(new_orders) > 0:
        for new_order in new_orders:
            BatchQuestionOrder.update_question_order(new_order, batch)
        success_message = "Question orders successfully updated for batch: %s." % batch.name.capitalize()
        messages.success(request, success_message)
    else:
        messages.error(request, 'No questions orders were updated.')
    return HttpResponseRedirect("/batches/%s/questions/" % batch_id)


@login_required
def check_name(request, survey_id):
    response = Batch.objects.filter(name=request.GET['name'], survey__id=survey_id).exists()
    return HttpResponse(json.dumps(not response), content_type="application/json")


@permission_required('auth.can_view_batches')
def list_batches(request):
    if request.is_ajax():
        batches = Batch.objects.values('id', 'name').order_by('name')
        json_dump = json.dumps(list(batches), cls=DjangoJSONEncoder)
        return HttpResponse(json_dump, mimetype='application/json')
    return render(request, 'layout.html')


def activate_non_response(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    location = Location.objects.get(id=request.POST['non_response_location_id'])
    if batch.is_open_for(location):
        batch.activate_non_response_for(location)
        return HttpResponse(json.dumps(""), content_type="application/json")
    message = "%s is not open for %s" % (batch.name, location.name)
    return HttpResponse(json.dumps(message), content_type="application/json")


def deactivate_non_response(request, batch_id):
    batch = Batch.objects.get(id=batch_id)
    location = Location.objects.get(id=request.POST['non_response_location_id'])
    if batch.is_open_for(location):
        batch.deactivate_non_response_for(location)
    return HttpResponse(json.dumps(""), content_type="application/json")