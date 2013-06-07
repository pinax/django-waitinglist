from django.contrib import admin

from .models import (
    Cohort,
    SignupCodeCohort,
    Survey,
    SurveyAnswer,
    SurveyInstance,
    SurveyQuestion,
    SurveyQuestionChoice,
    UserCohort,
    WaitingListEntry
)


class WaitingListEntryAdmin(admin.ModelAdmin):
    
    list_display = ["email", "created"]
    search_fields = ["email"]


class SignupCodeCohortInline(admin.TabularInline):
    
    model = SignupCodeCohort


class UserCohortInline(admin.TabularInline):
    
    model = UserCohort


class SurveyInstanceAdmin(admin.ModelAdmin):
    
    model = SurveyInstance
    list_display = ["survey", "email", "created"]
    
    def survey(self, obj):
        return obj.survey.label
    
    def email(self, obj):
        return obj.entry.email
    
    def created(self, obj):
        return obj.entry.created


class SurveyAnswerAdmin(admin.ModelAdmin):
    
    model = SurveyAnswer
    list_display = ["survey", "email", "question_label", "value", "value_boolean", "created"]
    
    def survey(self, obj):
        return obj.instance.survey.label
    
    def email(self, obj):
        return obj.instance.entry.email
    
    def question_label(self, obj):
        return obj.question.question


class SurveyQuestionChoiceInline(admin.TabularInline):
    
    model = SurveyQuestionChoice


class SurveyQuestionAdmin(admin.ModelAdmin):
    
    model = SurveyQuestion
    list_display = ["survey", "question", "kind", "required"]
    inlines = [SurveyQuestionChoiceInline]
    
    def survey(self, obj):
        return obj.survey.label


admin.site.register(WaitingListEntry, WaitingListEntryAdmin)
admin.site.register(
    Cohort,
    inlines=[
        SignupCodeCohortInline,
        UserCohortInline,
    ]
)

admin.site.register(
    Survey,
    list_display=["label", "active"]
)
admin.site.register(SurveyAnswer, SurveyAnswerAdmin)
admin.site.register(SurveyInstance, SurveyInstanceAdmin)
admin.site.register(SurveyQuestion, SurveyQuestionAdmin)
