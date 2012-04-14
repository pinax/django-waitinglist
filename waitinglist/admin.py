from django.contrib import admin

from waitinglist.models import WaitingListEntry


class WaitingListEntryAdmin(admin.ModelAdmin):
    list_display = ["email", "created"]
    search_fields = ["email"]


admin.site.register(WaitingListEntry, WaitingListEntryAdmin)
