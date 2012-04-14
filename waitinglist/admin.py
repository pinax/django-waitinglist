from django.contrib import admin

from waitinglist.models import WaitingListEntry
from waitinglist.models import SignupCodeCohort, UserCohort, Cohort


class WaitingListEntryAdmin(admin.ModelAdmin):
    
    list_display = ["email", "created"]
    search_fields = ["email"]


class SignupCodeCohortInline(admin.TabularInline):
    
    model = SignupCodeCohort


class UserCohortInline(admin.TabularInline):
    
    model = UserCohort


admin.site.register(WaitingListEntry, WaitingListEntryAdmin)
admin.site.register(Cohort,
    inlines = [
        SignupCodeCohortInline,
        UserCohortInline,
    ]
)
