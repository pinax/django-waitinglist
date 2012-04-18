import datetime

from django.utils import timezone

from django.contrib.auth.models import User

from account.models import SignupCode

from waitinglist.models import WaitingListEntry


def stats():
    return {
        "waiting_list_entries": WaitingListEntry.objects.count(),
        "waitinglist_added_last_seven_days": WaitingListEntry.objects.filter(created__gt=timezone.now() - datetime.timedelta(days=7)).count(),
        "waitinglist_added_last_thirty_days": WaitingListEntry.objects.filter(created__gt=timezone.now() - datetime.timedelta(days=30)).count(),
        "waiting_list_entries_to_invite": WaitingListEntry.objects.exclude(email__in=SignupCode.objects.values("email")).exclude(email__in=User.objects.values("email")).count()
    }
