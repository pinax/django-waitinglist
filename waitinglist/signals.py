from django.dispatch import Signal


signed_up = Signal(providing_args=["entry"])
answered_survey = Signal(providing_args=["instance"])
