__author__ = 'peter_c_liao'
from django import forms


class TrainForm(forms.Form):
    lat1 = forms.FloatField()
    long1 = forms.FloatField()
    lat2 = forms.FloatField()
    long2 = forms.FloatField()