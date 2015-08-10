from django.dispatch import Signal


answered_survey = Signal(providing_args=["instance"])
