from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand

from django.contrib.sites.models import Site

from ...models import WaitingListEntry, SurveyQuestion, SurveyAnswer

from ... import trello


class Command(BaseCommand):

    help = "Export waiting list entries to Trello for use as a simple CRM"

    def export_contacts(self):
        entries = WaitingListEntry.objects.filter(trello_card_id="")
        for entry in entries:
            # 0. Title of card is email address
            title = entry.email.encode("utf-8")
            answers = []
            try:
                qs = entry.surveyinstance.answers.all().order_by("question__pk")
                for answer in qs:
                    if answer.question.kind == SurveyQuestion.BOOLEAN_FIELD \
                       or len(answer.value) > 0:
                        answers.append(answer)
            except:
                answers = []

            description = ""
            if len(answers) > 0:
                list_id = self.api.answered_surveys_list_id
                # 1. Create Markdown for Description
                for answer in answers:
                    description += "#### {0}:\n".format(answer.question.question.encode("utf-8"))
                    if answer.question.kind == SurveyQuestion.BOOLEAN_FIELD:
                        description += "> {0}\n\n".format(answer.value_boolean)
                    else:
                        description += "> {0}\n\n".format(answer.value.encode("utf-8"))
            else:
                list_id = self.api.imported_contacts_list_id
            path = reverse("admin:waitinglist_waitinglistentry_change", args=[entry.pk])
            description += "\n\n-----\n\nID: {0}\n".format(str(entry.pk))
            description += "Admin Link: {0}://{1}{2}\n".format(
                self.protocol, self.site.domain, path)
            description += "Created At: {0}\n".format(str(entry.created))

            # 2. Create the card
            card = self.api.create_card(title, description, list_id)
            # 3. Store the id
            entry.trello_card_id = card["id"]
            entry.save()
            print "Exported {0} onto Card {1}".format(
                entry.email.encode("utf-8"), entry.trello_card_id)

    def export_answers(self):
        questions = SurveyQuestion.objects.filter(trello_list_id="")
        for question in questions:
            question.trello_list_id = self.api.setup_board(question.question)
            question.save()
        answers = SurveyAnswer.objects.filter(trello_card_id="")
        for answer in answers:
            description = "Entry: {0}\n".format(
                self.api.card_short_url(answer.instance.entry.trello_card_id))
            if answer.question.kind == SurveyQuestion.BOOLEAN_FIELD:
                title = str(answer.value_boolean)
            else:
                title = answer.value.encode("utf-8")
            if title.strip() != "":
                card = self.api.create_card(title, description, answer.question.trello_list_id)
                answer.trello_card_id = card["id"]
                answer.save()
                print "Exported Answer {0} on Card {1}".format(answer.pk, answer.trello_card_id)

    def handle(self, *args, **options):
        self.site = Site.objects.get_current()
        self.protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        self.api = trello.Api()
        self.export_contacts()
        self.export_answers()
