__author__ = 'peter_c_liao'
from django import forms


class TrainForm(forms.Form):
    lat = forms.FloatField()
    long = forms.FloatField()
    heading = forms.FloatField()


class UserForm(forms.Form):
    name = forms.CharField(max_length=60)
    email = forms.CharField(max_length=60)
    user_id = forms.IntegerField()
