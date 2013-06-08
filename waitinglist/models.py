import collections
import hashlib

from django import forms
from django.conf import settings
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from account.models import SignupCode, SignupCodeResult
from account.signals import user_signed_up


SURVEY_SECRET = getattr(settings, "WAITINGLIST_SURVEY_SECRET", settings.SECRET_KEY)


class WaitingListEntry(models.Model):
    
    email = models.EmailField(_("email address"), unique=True)
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False)
    
    class Meta:
        verbose_name = _("waiting list entry")
        verbose_name_plural = _("waiting list entries")


@receiver(post_save, sender=WaitingListEntry)
def handle_waitinglistentry_save(sender, **kwargs):
    if kwargs.get("created"):
        try:
            survey = Survey.objects.get(active=True)
            SurveyInstance.objects.create(
                survey=survey,
                entry=kwargs.get("instance")
            )
        except Survey.DoesNotExist:
            pass


class Survey(models.Model):
    
    label = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.label
    
    def save(self, *args, **kwargs):
        if self.active:
            Survey.objects.filter(active=True).update(active=False)
        return super(Survey, self).save(*args, **kwargs)


class SurveyInstance(models.Model):
    
    survey = models.ForeignKey(Survey, related_name="instances")
    entry = models.OneToOneField(WaitingListEntry)
    code = models.CharField(max_length=200, unique=True)
    
    def generate_hash(self):
        return hashlib.md5(self.entry.email + SURVEY_SECRET).hexdigest()
    
    def save(self, *args, **kwargs):
        self.code = self.generate_hash()
        return super(SurveyInstance, self).save(*args, **kwargs)


class SurveyQuestion(models.Model):
    
    TEXT_FIELD = 0
    TEXT_AREA = 1
    RADIO_CHOICES = 2
    CHECKBOX_FIELD = 3
    BOOLEAN_FIELD = 4
    
    FIELD_TYPE_CHOICES = [
        (TEXT_FIELD, "text field"),
        (TEXT_AREA, "textarea"),
        (RADIO_CHOICES, "radio choices"),
        (CHECKBOX_FIELD, "checkbox field (can select multiple answers"),
        (BOOLEAN_FIELD, "boolean field")
    ]
    
    survey = models.ForeignKey(Survey, related_name="questions")
    question = models.TextField()
    kind = models.IntegerField(choices=FIELD_TYPE_CHOICES)
    help_text = models.TextField(blank=True)
    ordinal = models.IntegerField(blank=True)
    required = models.BooleanField()
    
    class Meta:
        unique_together = [
            ("survey", "question")
        ]
        ordering = ["ordinal"]
    
    @property
    def name(self):
        return slugify(self.question)
    
    def form_field(self):
        kwargs = dict(
            label=self.question,
            help_text=self.help_text,
            required=self.required
        )
        field_class = forms.CharField
        
        if self.kind == SurveyQuestion.TEXT_AREA:
            kwargs.update({"widget": forms.Textarea()})
        elif self.kind == SurveyQuestion.RADIO_CHOICES:
            field_class = forms.ModelChoiceField
            kwargs.update({"widget": forms.RadioSelect(), "queryset": self.choices.all()})
        elif self.kind == SurveyQuestion.CHECKBOX_FIELD:
            field_class = forms.ModelMultipleChoiceField
            kwargs.update({"widget": forms.CheckboxSelectMultiple(), "queryset": self.choices.all()})
        elif self.kind == SurveyQuestion.BOOLEAN_FIELD:
            field_class = forms.BooleanField
        
        return field_class(**kwargs)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            max_ordinal = self.survey.questions.aggregate(
                Max("ordinal")
            )["ordinal__max"] or 0
            self.ordinal = max_ordinal + 1
        return super(SurveyQuestion, self).save(*args, **kwargs)


class SurveyQuestionChoice(models.Model):
    question = models.ForeignKey(SurveyQuestion, related_name="choices")
    label = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.label


class SurveyAnswer(models.Model):
    
    instance = models.ForeignKey(SurveyInstance, related_name="answers")
    question = models.ForeignKey(SurveyQuestion, related_name="answers")
    value = models.TextField(blank=True)
    value_boolean = models.NullBooleanField(blank=True)
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False)


Member = collections.namedtuple("Member", ["email", "signup_code", "user", "invited"])


class Cohort(models.Model):
    
    name = models.CharField(_("name"), max_length=35)
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False)
    
    def members(self):
        members = []
        for scc in self.signupcodecohort_set.select_related():
            try:
                scr = SignupCodeResult.objects.get(signup_code=scc.signup_code_id)
            except SignupCodeResult.DoesNotExist:
                user = None
            else:
                user = scr.user
            members.append(
                Member(
                    scc.signup_code.email,
                    scc.signup_code,
                    user,
                    bool(scc.signup_code.sent)
                )
            )
        return members
    
    def member_counts(self):
        members = self.members()
        return {
            "total": len(members),
            "users": len([m for m in members if m.user is not None]),
            "pending": len([m.signup_code for m in members if not m.invited]),
        }
    
    def send_invitations(self):
        for sc in [m.signup_code for m in self.members() if not m.invited]:
            sc.send()
    
    def __unicode__(self):
        return self.name


class SignupCodeCohort(models.Model):
    """
    fetch cohort of a given signup code
        SignupCodeCohort.objects.select_related("cohort").get(signup_code__code="abc").cohort
        
    list of people waiting NOT on the site already or invited
        WaitingListEntry.objects.exclude(email__in=SignupCode.objects.values("email")).exclude(email__in=User.objects.values("email"))
    """
    signup_code = models.OneToOneField(SignupCode)
    cohort = models.ForeignKey(Cohort)


class UserCohort(models.Model):
    """
    Upon signup we create an instance of this model associating the new user and their cohort
    """
    user = models.OneToOneField(User)
    cohort = models.ForeignKey(Cohort)


@receiver(user_signed_up)
def handle_user_signup(sender, **kwargs):
    signup_code = kwargs["form"].cleaned_data["code"]
    # fetch the cohort for the signup code
    qs = SignupCodeCohort.objects.select_related("cohort")
    try:
        cohort = qs.get(signup_code__code=signup_code).cohort
        # create a UserCohort for user association to a cohort
        UserCohort.objects.create(user=kwargs["user"], cohort=cohort)
    except SignupCodeCohort.DoesNotExist:
        pass
