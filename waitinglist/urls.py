from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^list_signup/$", "waitinglist.views.list_signup", name="waitinglist_list_signup"),
    url(r"^ajax_list_signup/$", "waitinglist.views.ajax_list_signup", name="waitinglist_ajax_list_signup"),
    url(r"^success/$", direct_to_template, {"template": "waitinglist/success.html"}, name="waitinglist_success"),
    url(r"^survey/(?P<code>.*)/$", "waitinglist.views.survey", name="waitinglist_survey"),
    url(r"^cohorts/$", "waitinglist.views.cohort_list", name="waitinglist_cohort_list"),
    url(r"^cohorts/create/$", "waitinglist.views.cohort_create", name="waitinglist_cohort_create"),
    url(r"^cohorts/cohort/(\d+)/$", "waitinglist.views.cohort_detail", name="waitinglist_cohort_detail"),
    url(r"^cohorts/cohort/(\d+)/add_member/$", "waitinglist.views.cohort_member_add", name="waitinglist_cohort_member_add"),
    url(r"^cohorts/cohort/(\d+)/send_invitations/$", "waitinglist.views.cohort_send_invitations", name="waitinglist_cohort_send_invitations"),
)