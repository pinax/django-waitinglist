from django.test import TestCase

from .forms import SurveyForm
from .models import (
    Survey,
    SurveyQuestion,
    WaitingListEntry
)


class SurveyTests(TestCase):
    
    def setUp(self):
        self.survey = Survey.objects.create(
            label="My Test Survey"
        )
        self.entry = WaitingListEntry.objects.create(email="pinax@awesome.com")
        self.ice_cream_question = self.survey.questions.create(
            question="What is your favorite ice cream flavor?",
            kind=SurveyQuestion.TEXT_FIELD,
            help_text="(e.g. Vanilla, Strawberry, Chocolate)",
            required=True
        )
        self.summer_question = self.survey.questions.create(
            question="What did you do last summer?",
            kind=SurveyQuestion.TEXT_AREA,
            required=False
        )
        self.season_question = self.survey.questions.create(
            question="What is your favorite season?",
            kind=SurveyQuestion.RADIO_CHOICES,
            required=True
        )
        self.spring = self.season_question.choices.create(
            label="Spring"
        )
        self.summer = self.season_question.choices.create(
            label="Summer"
        )
        self.fall = self.season_question.choices.create(
            label="Fall"
        )
        self.winter = self.season_question.choices.create(
            label="Winter"
        )
        self.city_question = self.survey.questions.create(
            question="Select all the cities you have visited",
            kind=SurveyQuestion.CHECKBOX_FIELD,
            required=True
        )
        self.boston = self.city_question.choices.create(
            label="Boston"
        )
        self.denver = self.city_question.choices.create(
            label="Denver"
        )
        self.nashville = self.city_question.choices.create(
            label="Nashville"
        )
        self.danville = self.city_question.choices.create(
            label="Danville"
        )
        self.golf_question = self.survey.questions.create(
            question="Do you like golf?",
            kind=SurveyQuestion.BOOLEAN_FIELD,
            required=True
        )
    
    def test_create_second_survey(self):
        Survey.objects.create(label="Another test survey")
        self.assertEquals(Survey.objects.count(), 2)
        self.assertEquals(Survey.objects.filter(active=False).count(), 1)
        self.assertEquals(Survey.objects.filter(active=True).count(), 1)
    
    def test_survey_form_creation(self):
        form = SurveyForm(survey=self.survey)
        self.assertTrue(len(form.fields), 5)
    
    def test_survey_form_invalid(self):
        form = SurveyForm(
            data={
                self.ice_cream_question.name: "Strawberry"
            },
            survey=self.survey
        )
        self.assertFalse(form.is_valid())
    
    def test_survey_form_valid(self):
        form = SurveyForm(
            data={
                self.ice_cream_question.name: "Strawberry",
                self.summer_question.name: "Swam in the lake",
                self.season_question.name: self.summer.pk,
                self.city_question.name: [self.nashville.pk],
                self.golf_question.name: True
            },
            survey=self.survey
        )
        self.assertTrue(form.is_valid())
    
    def test_survey_form_save(self):
        form = SurveyForm(
            data={
                self.ice_cream_question.name: "Strawberry",
                self.summer_question.name: "Swam in the lake",
                self.season_question.name: self.summer.pk,
                self.city_question.name: [self.nashville.pk, self.boston.pk],
                self.golf_question.name: True
            },
            survey=self.survey
        )
        self.assertTrue(form.is_valid())
        form.save(self.entry.surveyinstance)
        answers = self.entry.surveyinstance.answers.all()
        self.assertEquals(answers.count(), 5)
        self.assertEquals(answers.get(question=self.ice_cream_question).value, "Strawberry")
        self.assertEquals(answers.get(question=self.summer_question).value, "Swam in the lake")
        self.assertEquals(answers.get(question=self.season_question).value, self.summer.label)
        self.assertTrue(
            self.nashville.label in answers.get(question=self.city_question).value
        )
        self.assertTrue(
            self.boston.label in answers.get(question=self.city_question).value
        )
        self.assertTrue(answers.get(question=self.golf_question).value_boolean)
