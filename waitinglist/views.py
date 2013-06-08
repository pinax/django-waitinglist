import json

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from django.contrib.auth.models import User

from account.models import SignupCode

from .forms import WaitingListEntryForm, CohortCreate, SurveyForm
from .models import WaitingListEntry, Cohort, SignupCodeCohort, SurveyInstance
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
                },  context_instance=RequestContext(request))
            }
    else:
        data = {
            "html": render_to_string("waitinglist/_list_signup.html", {
                "form": form,
            },  context_instance=RequestContext(request))
        }
    return HttpResponse(json.dumps(data), mimetype="application/json")


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


def cohort_list(request):
    
    if not request.user.is_staff:
        raise Http404()
    
    ctx = {
        "cohorts": Cohort.objects.order_by("-created")
    }
    return render(request, "cohorts/cohort_list.html", ctx)


def cohort_create(request):
    
    if not request.user.is_staff:
        raise Http404()
    
    if request.method == "POST":
        form = CohortCreate(request.POST)
        
        if form.is_valid():
            cohort = form.save()
            return redirect("waitinglist_cohort_detail", cohort.id)
    else:
        form = CohortCreate()
    
    ctx = {
        "form": form,
    }
    return render(request, "cohorts/cohort_create.html", ctx)


def cohort_detail(request, pk):
    
    if not request.user.is_staff:
        raise Http404()
    
    cohort = get_object_or_404(Cohort, pk=pk)
    
    # people who are NOT invited or on the site already
    waiting_list = WaitingListEntry.objects.exclude(
        email__in=SignupCode.objects.values("email")
    ).exclude(
        email__in=User.objects.values("email")
    )
    
    ctx = {
        "cohort": cohort,
        "waiting_list": waiting_list,
    }
    return render(request, "cohorts/cohort_detail.html", ctx)


def cohort_member_add(request, pk):
    
    if not request.user.is_staff:
        raise Http404()
    
    cohort = Cohort.objects.get(pk=pk)
    
    if "invite_next" in request.POST:
        try:
            N = int(request.POST["invite_next"])
        except ValueError:
            return redirect("waitinglist_cohort_detail", cohort.id)
        # people who are NOT invited or on the site already
        waiting_list = WaitingListEntry.objects.exclude(
            email__in=SignupCode.objects.values("email")
        ).exclude(
            email__in=User.objects.values("email")
        )
        emails = waiting_list.values_list("email", flat=True)[:N]
    else:
        email = request.POST["email"].strip()
        if email:
            emails = [email]
        else:
            emails = []
    
    for email in emails:
        if not SignupCode.objects.filter(email=email).exists():
            signup_code = SignupCode.create(email=email, max_uses=1, expiry=730)
            signup_code.save()
            SignupCodeCohort.objects.create(signup_code=signup_code, cohort=cohort)
    
    return redirect("waitinglist_cohort_detail", cohort.id)


def cohort_send_invitations(request, pk):
    
    if not request.user.is_staff:
        raise Http404()
    
    cohort = Cohort.objects.get(pk=pk)
    cohort.send_invitations()
    
    return redirect("waitinglist_cohort_detail", cohort.id)
