from django import forms
from .models import Project
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['address', 'kWh_consumption', 'escalator']

    def clean_kWh_consumption(self):
        kWh_consumption = self.cleaned_data.get('kWh_consumption')
        if kWh_consumption < 1000 or kWh_consumption > 10000:
            raise forms.ValidationError('kWh consumption must be between 1000 and 10000.')
        return kWh_consumption

    def clean_escalator(self):
        escalator = self.cleaned_data.get('escalator')
        if escalator < 4 or escalator > 10:
            raise forms.ValidationError('Escalator must be between 4% and 10%.')
        return escalator

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')