import datetime

from django.utils import timezone

from django.contrib.auth.models import User

from account.models import SignupCode

from waitinglist.models import WaitingListEntry


def stats():
    waiting_list = WaitingListEntry.objects
    return {
        "waiting_list_entries": waiting_list.count(),
        "waitinglist_added_last_seven_days":
            waiting_list.filter(created__gt=timezone.now() - datetime.timedelta(days=7)).count(),
        "waitinglist_added_last_thirty_days":
            waiting_list.filter(created__gt=timezone.now() - datetime.timedelta(days=30)).count(),
        "waiting_list_entries_to_invite":
            waiting_list.exclude(email__in=SignupCode.objects.values("email"))
            .exclude(email__in=User.objects.values("email")).count()
    }
