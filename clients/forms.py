# clients/forms.py
from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name','contact_person', 'email',
            'phone', 'address', 'types', 'tax_id',
            'website', 'notes'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name','contact_person', 'email',
            'phone', 'address', 'types', 'tax_id',
            'website', 'notes'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email



