from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns("",
    url(r"^list_signup/$", "waitinglist.views.list_signup", name="waitinglist_list_signup"),
    url(r"^ajax_list_signup/$", "waitinglist.views.ajax_list_signup", name="waitinglist_ajax_list_signup"),
    url(r"^survey/thanks/$", TemplateView.as_view(template_name="waitinglist/thanks.html"), name="waitinglist_thanks"),
    url(r"^survey/(?P<code>.*)/$", "waitinglist.views.survey", name="waitinglist_survey"),
    url(r"^success/$", TemplateView.as_view(template_name="waitinglist/success.html"), name="waitinglist_success"),
    url(r"^cohorts/$", "waitinglist.views.cohort_list", name="waitinglist_cohort_list"),
    url(r"^cohorts/create/$", "waitinglist.views.cohort_create", name="waitinglist_cohort_create"),
    url(r"^cohorts/cohort/(\d+)/$", "waitinglist.views.cohort_detail", name="waitinglist_cohort_detail"),
    url(r"^cohorts/cohort/(\d+)/add_member/$", "waitinglist.views.cohort_member_add", name="waitinglist_cohort_member_add"),
    url(r"^cohorts/cohort/(\d+)/send_invitations/$", "waitinglist.views.cohort_send_invitations", name="waitinglist_cohort_send_invitations"),
)
