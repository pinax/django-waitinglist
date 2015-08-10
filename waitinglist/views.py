import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import WaitingListEntryForm, SurveyForm
from .models import SurveyInstance
from .signals import signed_up


@require_POST
def ajax_list_signup(request):
    form = WaitingListEntryForm(request.POST)
    if form.is_valid():
        entry = form.save()
        signed_up.send(sender=ajax_list_signup, entry=entry)
        try:
            data = {
                "location": reverse("waitinglist_survey", args=[entry.surveyinstance.code])
            }
        except SurveyInstance.DoesNotExist:
            data = {
                "html": render_to_string("waitinglist/_success.html", {
                }, context_instance=RequestContext(request))
            }
    else:
        data = {
            "html": render_to_string("waitinglist/_list_signup.html", {
                "form": form,
            }, context_instance=RequestContext(request))
        }
    return HttpResponse(json.dumps(data), content_type="application/json")


def list_signup(request, post_save_redirect=None):
    if request.method == "POST":
        form = WaitingListEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            signed_up.send(sender=list_signup, entry=entry)
            try:
                post_save_redirect = reverse("waitinglist_survey", args=[entry.surveyinstance.code])
            except SurveyInstance.DoesNotExist:
                pass
            if post_save_redirect is None:
                post_save_redirect = reverse("waitinglist_success")
            if not post_save_redirect.startswith("/"):
                post_save_redirect = reverse(post_save_redirect)
            return redirect(post_save_redirect)
    else:
        form = WaitingListEntryForm()
    ctx = {
        "form": form,
    }
    return render(request, "waitinglist/list_signup.html", ctx)


def survey(request, code):
    instance = get_object_or_404(SurveyInstance, code=code)
    if request.method == "POST":
        form = SurveyForm(request.POST, survey=instance.survey)
        if form.is_valid():
            form.save(instance)
            return redirect("waitinglist_thanks")
    else:
        form = SurveyForm(survey=instance.survey)
    return render(request, "waitinglist/survey.html", {"form": form})
