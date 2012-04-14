from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render, redirect

from waitinglist.forms import WaitingListEntryForm


def list_signup(request, post_save_redirect=None):
    if request.method == "POST":
        form = WaitingListEntryForm(request.POST)
        if form.is_valid():
            form.save()
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
