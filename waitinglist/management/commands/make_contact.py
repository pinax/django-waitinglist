from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from django.contrib.sites.models import Site

from ...models import WaitingListEntry

from ... import trello


class Command(BaseCommand):

    help = "Contact users in 'To Contact' list on Trello"

    def make_contact(self):
        cards = self.api.cards(self.api.to_contact_list_id)
        for card in cards:
            try:
                entry = WaitingListEntry.objects.filter(initial_contact_sent=False)\
                    .get(trello_card_id=card["id"])
                subject = render_to_string(
                    "waitinglist/email/initial_contact_subject.txt", {"entry": entry})
                message = render_to_string(
                    "waitinglist/email/initial_contact.txt", {"entry": entry})
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [entry.email])
                self.api.move_card(card["id"], self.api.contacted_list_id)
                entry.initial_contact_sent = True
                entry.save()
                print "Sent to {0} ({1}) [Card #{2}]".format(
                    card["name"], card["shortUrl"], card["idShort"])
            except WaitingListEntry.DoesNotExist:
                print "{0} ({1}) has already been sent [Card #{2}]".format(
                    card["name"], card["shortUrl"], card["idShort"])

    def handle(self, *args, **options):
        self.site = Site.objects.get_current()
        self.protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        self.api = trello.Api()
        self.make_contact()
