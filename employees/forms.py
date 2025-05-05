# employees/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Employee

class EmployeeCreateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'email',
            'nid', 'department', 'designation', 'is_regular', 'photo',
            'phone', 'address', 'marital_status',
            'bkash', 'bank_name', 'account_number',
            'emergency_contact_person', 'relation_with_the_person',
            'emergency_contact_1'
        ]
        widgets = {
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'relation_with_the_person': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'email',
            'nid', 'department', 'designation', 'is_regular', 'photo',
            'phone', 'address', 'marital_status',
            'bkash', 'bank_name', 'account_number',
            'emergency_contact_person', 'relation_with_the_person',
            'emergency_contact_1'
        ]
        widgets = {
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'relation_with_the_person': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email