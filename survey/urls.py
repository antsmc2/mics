
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import TemplateView
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'survey.views.home_page.home', name='home_page'),
    url(r'^about/$', 'survey.views.home_page.about', name='about_page'),
    url(r'^locations/hierarchy/add/$', 'survey.views.location_hierarchy.add', name='add_location_hierarchy'),
    url(r'^locations/upload/$', 'survey.views.location_hierarchy.upload', name='upload_locations'),
    url(r'^locations/(?P<location_id>\d+)/children', 'survey.views.locations.children', name='get_location_children'),
    url(r'^investigators/$', 'survey.views.investigator.list_investigators', name="investigators_page"),
    url(r'^investigators/new/$', 'survey.views.investigator.new_investigator', name="new_investigator_page"),
    url(r'^investigators/(?P<investigator_id>\d+)/$', 'survey.views.investigator.show_investigator', name="show_investigator_page"),
    url(r'^investigators/(?P<investigator_id>\d+)/block/$', 'survey.views.investigator.block_investigator', name="block_investigator_page"),
    url(r'^investigators/(?P<investigator_id>\d+)/unblock/$', 'survey.views.investigator.unblock_investigator', name="unblock_investigator_page"),
    url(r'^investigators/(?P<investigator_id>\d+)/edit/$', 'survey.views.investigator.edit_investigator', name="edit_investigator_page"),
    url(r'^investigators/locations', 'survey.views.investigator.get_locations', name="locations_autocomplete"),
    url(r'^investigators/check_mobile_number', 'survey.views.investigator.check_mobile_number', name="check_mobile_number"),
    url(r'^ussd/simulator', permission_required('auth.can_view_batches')(TemplateView.as_view(template_name="ussd/simulator.html")), name='simulator_page'),
    url(r'^ussd', 'survey.views.ussd.ussd', name="ussd"),
    url(r'^households/$', 'survey.views.household.list_households', name="list_household_page"),
    url(r'^households/(?P<household_id>\d+)/$', 'survey.views.household.view_household', name="view_household_page"),
    url(r'^households/(?P<household_id>\d+)/edit/$', 'survey.views.household.edit_household', name="edit_household_page"),
    url(r'^households/new/$', 'survey.views.household.new', name="new_household_page"),
    url(r'^households/investigators', 'survey.views.household.get_investigators', name='load_investigators'),
    url(r'^households/(?P<household_id>\d+)/member/new/$', 'survey.views.household_member.new', name='new_household_member_page'),
    url(r'^households/(?P<household_id>\d+)/member/(?P<member_id>\d+)/edit/$', 'survey.views.household_member.edit', name='edit_household_member_page'),
    url(r'^households/(?P<household_id>\d+)/member/(?P<member_id>\d+)/delete/$', 'survey.views.household_member.delete', name='delete_household_member_page'),
    url(r'^aggregates/status', 'survey.views.aggregates.status', name='aggregates_status'),
    url(r'^aggregates/spreadsheet_report', 'survey.views.excel.download', name='excel_report'),
    url(r'^aggregates/download_spreadsheet', 'survey.views.excel.list', name='download_excel'),
    url(r'^investigator_report/', 'survey.views.excel.investigator_report', name='investigator_report_page'),
    url(r'^completed_investigators/download/', 'survey.views.excel.completed_investigator', name='download_investigator_excel'),
    url(r'^survey_completion/', 'survey.views.survey_completion.show', name='survey_completion_rates'),
    url(r'^survey/(?P<survey_id>\d+)/completion/json/$', 'survey.views.survey_completion.completion_json', name='survey_completion_json'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='login_page'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout_page'),
    url(r'^accounts/reset_password/$', 'django.contrib.auth.views.password_change',
        {'template_name': 'accounts/reset_password.html', 'post_change_redirect': '/accounts/reset_password/done/',
         'password_change_form': PasswordChangeForm}, name='password_change'),
    url(r'^accounts/reset_password/done/$', TemplateView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    url(r'^bulk_sms$', 'survey.views.bulk_sms.view', name='bulk_sms'),
    url(r'^bulk_sms/send$', 'survey.views.bulk_sms.send', name='send_bulk_sms'),
    url(r'^users/$', 'survey.views.users.index', name='users_index'),
    url(r'^users/new/$', 'survey.views.users.new', name='new_user_page'),
    url(r'^users/(?P<user_id>\d+)/edit/$', 'survey.views.users.edit', name='users_edit'),
    url(r'^batches/(?P<batch_id>\d+)/assign_questions/$', 'survey.views.batch.assign', name='assign_questions_page'),
    url(r'^batches/(?P<batch_id>\d+)/update_question_orders/$', 'survey.views.batch.update_orders', name='update_question_order_page'),
    url(r'^batches/(?P<batch_id>\d+)/questions/$', 'survey.views.questions.index', name='batch_questions_page'),
    url(r'^batches/(?P<batch_id>\d+)/open_to$', 'survey.views.batch.open', name='batch_open_page'),
    url(r'^batches/(?P<batch_id>\d+)/close_to$', 'survey.views.batch.close', name='batch_close_page'),
    url(r'^batches/(?P<batch_id>\d+)/formulae/(?P<formula_id>\d+)/$', 'survey.views.formula.show', name='formula_show_page'),
    url(r'^batches/(?P<batch_id>\w+)/questions/groups/(?P<group_id>\w+)/module/(?P<module_id>\w+)/', 'survey.views.questions.filter_by_group_and_module',name='list_questions_in_agroup'),
    url(r'^batches/(?P<batch_id>\d+)/questions/(?P<question_id>\d+)/add_logic/$', 'survey.views.questions.add_logic', name='add_question_logic_page'),
    url(r'^batches/(?P<batch_id>\d+)/questions/delete_logic/(?P<answer_rule_id>\d+)/$', 'survey.views.questions.delete_logic', name='delete_question_logic_page'),
    url(r'^batches/(?P<batch_id>\d+)/questions/(?P<question_id>\d+)/questions_json/$', 'survey.views.questions.get_questions_for_batch', name='batch_questions_json_page'),
    url(r'^batches/(?P<batch_id>\d+)/questions/(?P<question_id>\d+)/sub_questions/new/$', 'survey.views.questions.new_subquestion', name='add_batch_subquestion_page'),
    url(r'^batches/(?P<batch_id>\d+)/questions/(?P<question_id>\d+)/sub_questions/edit/$', 'survey.views.questions.edit_subquestion', name='edit_batch_subquestion_page'),
    url(r'^groups/(?P<group_id>\d+)/$', 'survey.views.household_member_group.details', name='household_member_groups_details'),
    url(r'^groups/(?P<group_id>\d+)/conditions/new/$', 'survey.views.household_member_group.add_group_condition', name='new_condition_for_group'),
    url(r'^groups/$', 'survey.views.household_member_group.index', name='household_member_groups_page'),
    url(r'^groups/new/$', 'survey.views.household_member_group.add_group', name='new_household_member_groups_page'),
    url(r'^groups/(?P<group_id>\d+)/edit/$', 'survey.views.household_member_group.edit_group', name='household_member_groups_edit'),
    url(r'^groups/(?P<group_id>\d+)/delete/$', 'survey.views.household_member_group.delete_group', name='household_member_groups_delete'),
    url(r'^conditions/$', 'survey.views.household_member_group.conditions', name='show_group_condition'),
    url(r'^conditions/new/$', 'survey.views.household_member_group.add_condition', name='new_group_condition'),
    url(r'^conditions/(?P<condition_id>\d+)/delete/$', 'survey.views.household_member_group.delete_condition', name='delete_condition_page'),
    url(r'^surveys/$', 'survey.views.surveys.index', name='survey_list_page'),
    url(r'^surveys/new/$', 'survey.views.surveys.new', name='new_survey_page'),
    url(r'^surveys/(?P<survey_id>\d+)/edit/$', 'survey.views.surveys.edit', name='edit_survey_page'),
    url(r'^surveys/(?P<survey_id>\d+)/delete/$', 'survey.views.surveys.delete', name='delete_survey'),
    url(r'^surveys/(?P<survey_id>\d+)/batches/$', 'survey.views.batch.index', name='batch_index_page'),
    url(r'^surveys/(?P<survey_id>\d+)/batches/new/$', 'survey.views.batch.new', name='new_batch_page'),
    url(r'^surveys/(?P<survey_id>\d+)/batches/(?P<batch_id>\d+)/$', 'survey.views.batch.show', name='batch_show_page'),
    url(r'^surveys/(?P<survey_id>\d+)/batches/(?P<batch_id>\d+)/edit/$', 'survey.views.batch.edit', name='batch_edit_page'),
    url(r'^surveys/(?P<survey_id>\d+)/batches/(?P<batch_id>\d+)/delete/$', 'survey.views.batch.delete', name='delete_batch'),
    url(r'^surveys/(?P<survey_id>\d+)/batches/check_name/$', 'survey.views.batch.check_name'),
    url(r'^questions/$', 'survey.views.questions.list_all_questions', name='list_all_questions'),
    url(r'^questions/new/$', 'survey.views.questions.new', name='new_question_page'),
    url(r'^questions/(?P<question_id>\d+)/sub_questions/new/$', 'survey.views.questions.new_subquestion', name='add_subquestion_page'),
    url(r'^questions/(?P<question_id>\d+)/sub_questions/edit/$', 'survey.views.questions.edit_subquestion', name='edit_subquestion_page'),
    url(r'^questions/(?P<question_id>\d+)/edit/$', 'survey.views.questions.edit', name='edit_question_page'),
    url(r'^questions/(?P<question_id>\d+)/sub_questions_json/$', 'survey.views.questions.get_sub_questions_for_question', name='questions_subquestion_json_page'),
    url(r'^questions/(?P<question_id>\d+)/delete/$', 'survey.views.questions.delete', name='delete_question_page'),
    url(r'^batches/$', 'survey.views.batch.list_batches'),
    url(r'^batches/(?P<batch_id>\d+)/questions/(?P<question_id>\d+)/delete/$', 'survey.views.questions.delete', name='delete_batch_question_page'),
    url(r'^batches/(?P<batch_id>\d+)/questions/(?P<question_id>\d+)/remove/$', 'survey.views.questions.remove', name='remove_question_page'),
    url(r'^modules/new/$', 'survey.views.question_module.new', name='new_question_module_page'),
    url(r'^modules/$', 'survey.views.question_module.index', name='question_module_listing_page'),
    url(r'^modules/(?P<module_id>\d+)/delete/$', 'survey.views.question_module.delete', name='delete_question_module_page'),
    url(r'^modules/(?P<module_id>\d+)/edit/$', 'survey.views.question_module.edit', name='edit_question_module_page'),
    url(r'^indicators/new/$', 'survey.views.indicators.new', name='new_indicator_page'),
    url(r'^indicators/$', 'survey.views.indicators.index', name='list_indicator_page')
)

if not settings.PRODUCTION:
    urlpatterns += (
        url(r'^api/create_investigator', 'survey.views.api.create_investigator', name='create_investigator'),
        url(r'^api/delete_investigator', 'survey.views.api.delete_investigator', name='delete_investigator'),
    )