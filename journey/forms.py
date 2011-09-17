from django import forms
from django.core.exceptions import ValidationError


from datetime import datetime

class JourneyForm(forms.Form):
    """Journey main edit form"""
    people_name = forms.CharField(max_length=200)
    people_count = forms.IntegerField()
    vehicle_name = forms.CharField(max_length=200, required=False)
    vehicle_seats = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        journey = kwargs.pop("journey", None)
        super(JourneyForm, self).__init__(*args, **kwargs)

class NewJourneyForm(forms.Form):
    """Journey creation form"""
    title = forms.CharField(max_length=200)
    from_addr = forms.CharField(max_length=1000, required=False)
    to_addr = forms.CharField(max_length=1000,  required=False)
    meeting_addr = forms.CharField(max_length=1000, required=False)
    date = forms.CharField(max_length=200, required = False)

    def __init__(self, *args, **kwargs):
        journey = kwargs.pop("journey", None)
        super(NewJourneyForm, self).__init__(*args, **kwargs)
