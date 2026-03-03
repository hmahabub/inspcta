# employees/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import MasterMariner

class MasterMarinerCreateForm(forms.ModelForm):
    class Meta:
        model = MasterMariner
        fields = [
            'name', 'email',
            'nid', 'designation',
            'phone', 'address', 'marital_status',
            'bkash', 'bank_name', 'account_number',
        ]
        widgets = {
            'marital_status': forms.Select(attrs={'class': 'form-control'}),

        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MasterMariner.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email


class MasterMarinerUpdateForm(forms.ModelForm):
    class Meta:
        model = MasterMariner
        fields = [
            'name', 'email',
            'nid', 'designation',
            'phone', 'address', 'marital_status',
            'bkash', 'bank_name', 'account_number',
        ]
        widgets = {
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MasterMariner.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email