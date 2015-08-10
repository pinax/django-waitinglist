from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns(
    "",

    url(r"^list_signup/$", "waitinglist.views.list_signup", name="waitinglist_list_signup"),
    url(r"^ajax_list_signup/$", "waitinglist.views.ajax_list_signup",
        name="waitinglist_ajax_list_signup"),
    url(r"^survey/thanks/$", TemplateView.as_view(template_name="waitinglist/thanks.html"),
        name="waitinglist_thanks"),
    url(r"^survey/(?P<code>.*)/$", "waitinglist.views.survey", name="waitinglist_survey"),
    url(r"^success/$", TemplateView.as_view(template_name="waitinglist/success.html"),
        name="waitinglist_success"),
)
