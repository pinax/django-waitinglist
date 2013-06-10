from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from django.contrib.sites.models import Site

from ...models import WaitingListEntry, Survey


class Command(BaseCommand):
    
    help = "Email links to survey instances for those that never saw a survey"
    
    def handle(self, *args, **options):
        survey = Survey.objects.get(active=True)
        entries = WaitingListEntry.objects.filter(surveyinstance__isnull=True)
        
        for entry in entries:
            instance = survey.instances.create(entry=entry)
            site = Site.objects.get_current()
            protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
            ctx = {
                "instance": instance,
                "site": site,
                "protocol": protocol,
            }
            subject = render_to_string("waitinglist/survey_invite_subject.txt", ctx)
            subject = subject.strip()
            message = render_to_string("waitinglist/survey_invite_body.txt", ctx)
            EmailMessage(
                subject,
                message,
                to=[entry.email],
                from_email=settings.WAITINGLIST_SURVEY_INVITE_FROM_EMAIL
            ).send()
