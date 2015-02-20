# -*- coding: utf-8 -*-
from django_genericfilters.views import FilteredListView, ListView
from django.utils.decorators import method_decorator
from survey.models import ODKSubmission
from django.contrib.auth.decorators import login_required, permission_required


#@login_required
#@permission_required('auth.can_view_aggregates')
class ODKSubmissionListView(ListView):
    # Normal ListView options
    template_name = 'odk/submission_list.html'
    context_object_name = 'submissions'
    model = ODKSubmission
#    search_fields = ['investigator__name', 'survey__name', 'household__uid', 'form_id', 'instance_id']

	@method_decorator(permission_required('auth.can_view_aggregates'))
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ODKSubmissionListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ODKSubmissionListView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['request'] = self.request
        return context



submission_list_view = ODKSubmissionListView.as_view()