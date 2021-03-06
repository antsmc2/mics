from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from survey.forms.aboutus_form import AboutUsForm
from survey.models import Survey, AboutUs


def home(request):
    return render(request, 'home/index.html', {'surveys': Survey.objects.all()})


def about(request):
    if AboutUs.objects.count():
        about_us_content = AboutUs.objects.all()[0]
    else:
        about_us_content = AboutUs.objects.create(content="No content available yet !!")

    return render(request, 'home/about.html', {'about_content': about_us_content})


@permission_required('auth.can_view_users')
def edit(request):
    about_us = AboutUs.objects.all()[0]
    about_form = AboutUsForm(instance=about_us)
    if request.method == 'POST':
        about_form = AboutUsForm(instance=about_us, data=request.POST)
        if about_form.is_valid():
            about_form.save()
            message = "About us content successfully updated."
            messages.success(request, message)
            return HttpResponseRedirect("/about/")
    return render(request, 'home/edit.html', {'about_form': about_form})