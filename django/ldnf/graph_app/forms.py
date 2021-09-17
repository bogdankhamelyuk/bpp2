from django import forms
from django.forms import ModelForm
from .models import Message

class PressureForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'