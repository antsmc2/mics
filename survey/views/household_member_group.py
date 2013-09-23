import json
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from survey.models.householdgroups import HouseholdMemberGroup, GroupCondition

from survey.forms.group_condition import GroupConditionForm
from survey.forms.household_member_group import HouseholdMemberGroupForm
from survey.views.views_helper import contains_key


@permission_required('auth.can_view_household_groups')
def conditions(request):
    conditions = GroupCondition.objects.all().order_by('condition')
    return render(request, 'household_member_groups/conditions/index.html',
                  {'conditions': conditions, 'add_condition_url': 'new_group_condition', 'request': request})


@permission_required('auth.can_view_investigators')
def index(request):
    groups = HouseholdMemberGroup.objects.all().order_by('order')
    return render(request, 'household_member_groups/index.html', {'groups': groups, 'request': request})


def _get_conditions_hash():
    condition = GroupCondition.objects.all().latest('created')
    return {'id': condition.id,
            'value': "%s > %s > %s" % (condition.attribute, condition.condition, condition.value)}


@permission_required('auth.can_view_household_groups')
def add_condition(request):
    response = None
    condition_form = GroupConditionForm()

    if request.is_ajax():
        condition_form = GroupConditionForm(data=request.POST)
        _process_condition_form(request, condition_form)
        conditions = _get_conditions_hash()
        return HttpResponse(json.dumps(conditions), mimetype='application/json')

    elif request.method == 'POST':
        condition_form = GroupConditionForm(data=request.POST)
        response = _process_condition_form(request, condition_form)

    context = {'button_label': 'Save',
               'title': 'New condition',
               'id': 'add-condition-form',
               'action': '/conditions/new/',
               'request': request,
               'condition_form': condition_form}

    return response or render(request, 'household_member_groups/conditions/new.html', context)


def has_valid_condition(data):
    if contains_key(data, 'conditions'):
        corresponding_condition = GroupCondition.objects.filter(id=int(data['conditions']))
        return corresponding_condition
    return False


def _process_condition_form(request, condition_form):
    if condition_form.is_valid():
        condition_form.save()
        messages.success(request, 'Condition successfully added.')
        redirect_url = '/conditions/'
    else:
        print condition_form.errors
        redirect_url = '/conditions/new/'
    return HttpResponseRedirect(redirect_url)


def _process_groupform(request, group_form):

    if group_form.is_valid() and has_valid_condition(request.POST):
        group_form.save()
        messages.success(request, 'Group successfully added.')
        return HttpResponseRedirect("/groups/")


@permission_required('auth.can_view_household_groups')
def add_group(request):
    params = request.POST
    response = None
    group_form = HouseholdMemberGroupForm(initial={'order':HouseholdMemberGroup.max_order()+1})

    if request.method == 'POST':
        group_form = HouseholdMemberGroupForm(params)
        response = _process_groupform(request, group_form)
    context = {'groups_form': group_form,
               'conditions': GroupCondition.objects.all(),
               'title': "New Group",
               'button_label': 'Save',
               'id': 'add_group_form',
               'action': "/groups/new/",
               'condition_form': GroupConditionForm(),
               'condition_title': "New Condition"}

    return response or render(request, 'household_member_groups/new.html', context)


@permission_required('auth.can_view_household_groups')
def details(request, group_id):
    conditions = GroupCondition.objects.filter(groups__id=group_id)
    if not conditions.exists():
        messages.error(request, "No conditions in this group.")
        return HttpResponseRedirect("/groups/")
    return render(request, "household_member_groups/conditions/index.html",
                  {'conditions': conditions, 'add_condition_url': 'new_condition_for_group', 'group_id': group_id})


@permission_required('auth.can_view_household_groups')
def add_group_condition(request,group_id):
    condition_form = GroupConditionForm()
    if request.method == 'POST':
        condition_form = GroupConditionForm(data=request.POST)
        if condition_form.is_valid():
            try:
                group = HouseholdMemberGroup.objects.get(id=group_id)
                condition = condition_form.save()
                condition.groups.add(group)
                condition.save()
                messages.success(request, "Condition successfully added.")
                redirect_url = '/groups/%s/' % group_id
            except ObjectDoesNotExist:
                messages.error(request, "Group does not exist.")
                redirect_url = '/groups/'
            return HttpResponseRedirect(redirect_url)

    context = {'button_label': 'Save',
               'title': 'New condition',
               'id': 'add-condition-to-group-form',
               'action': '/groups/%s/conditions/new/' % group_id,
               'request': request,
               'condition_form': condition_form}
    return render(request, 'household_member_groups/conditions/new.html', context)