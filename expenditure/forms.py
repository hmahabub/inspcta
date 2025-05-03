# expenditure/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import *
from clients.models import Client
from projects.models import Project
from django_select2.forms import ModelSelect2Widget
from django.utils import timezone
from datetime import timedelta

from dal import autocomplete


class RegularExpenditureCreateForm(forms.ModelForm):
    class Meta:
        model = RegularExpenditure
        fields = [
            'project', 'employee','date', 'payment_method', 'receipt_number', 
            'ot_hours', 'ot_rate','conveyance', 'boat_fee', 'fooding_fee', 'hotel_fee', 
            'night_allownce', 'others', 'paid_in_advance'
            
        ]
        widgets = {
            'project': autocomplete.ModelSelect2(
                url='projects:relatedmodel-autocomplete',
                attrs={
                    'data-placeholder': 'Search for a related item...',
                    'data-minimum-input-length': 2,
                },
            ),
            'employee': autocomplete.ModelSelect2(
                url='employees:relatedmodel-autocomplete-r',
                attrs={
                    'data-placeholder': 'Search...',
                    'data-minimum-input-length': 2,
                },
            ), 
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")
        employee = cleaned_data.get("employee")
        date = cleaned_data.get("date")

        if self.instance.pk is None:  # only check on create, not update
            if RegularExpenditure.objects.filter(project=project, employee=employee, date=date).exists():
                raise ValidationError("This employee already has an entry for the same project and date.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_regular=True)



class RegularExpenditureUpdateForm(forms.ModelForm):
    class Meta:
        model = RegularExpenditure
        fields = [
            'project', 'employee','date', 'payment_method', 'receipt_number', 
            'ot_hours', 'ot_rate','conveyance', 'boat_fee', 'fooding_fee', 'hotel_fee', 
            'night_allownce', 'others', 'paid_in_advance'
            
        ]
        widgets = {
            'project': forms.Select(attrs={'readonly': 'True'}),
            'employee': forms.Select(attrs={'readonly': 'True'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }


    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")
        employee = cleaned_data.get("employee")
        date = cleaned_data.get("date")

        if self.instance.pk is None:  # only check on create, not update
            if RegularExpenditure.objects.filter(project=project, employee=employee, date=date).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This employee already has an entry for the same project and date.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_regular=True)

class ProvisionaryExpenditureCreateForm(forms.ModelForm):
    class Meta:
        model = ProvisionaryExpenditure
        fields = [
            'project', 'employee','date', 'payment_method', 'receipt_number',
            'fixed_amount', 
            'ot_hours', 'ot_rate','conveyance', 'boat_fee', 'fooding_fee', 'hotel_fee', 
            'night_allownce', 'others', 'paid_in_advance'
            
        ]
        widgets = {
           'project': autocomplete.ModelSelect2(
                url='projects:relatedmodel-autocomplete',
                attrs={
                    'data-placeholder': 'Search for a related item...',
                    'data-minimum-input-length': 2,
                },
            ),
            'employee': autocomplete.ModelSelect2(
                url='employees:relatedmodel-autocomplete-p',
                attrs={
                    'data-placeholder': 'Search...',
                    'data-minimum-input-length': 2,
                },
            ),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }


    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")
        employee = cleaned_data.get("employee")
        date = cleaned_data.get("date")

        if self.instance.pk is None:  # only check on create, not update
            if ProvisionaryExpenditure.objects.filter(project=project, employee=employee, date=date).exists():
                raise ValidationError("This employee already has an entry for the same project and date.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_regular=False)


class ProvisionaryExpenditureUpdateForm(forms.ModelForm):
    class Meta:
        model = ProvisionaryExpenditure
        fields = [
            'project', 'employee','date', 'payment_method', 'receipt_number',
            'fixed_amount', 
            'ot_hours', 'ot_rate','conveyance', 'boat_fee', 'fooding_fee', 'hotel_fee', 
            'night_allownce', 'others', 'paid_in_advance'
            
        ]
        widgets = {
            'project': forms.Select(attrs={'readonly': 'True'}),
            'employee': forms.Select(attrs={'readonly': 'True'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")
        employee = cleaned_data.get("employee")
        date = cleaned_data.get("date")

        if self.instance.pk is None:  # only check on create, not update
            if ProvisionaryExpenditure.objects.filter(project=project, employee=employee, date=date).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This employee already has an entry for the same project and date.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_regular=False)


class OperationalExpenditureCreateForm(forms.ModelForm):
    class Meta:
        model = OperationalExpenditure
        fields = [
            'project','date', 'payment_method', 'receipt_number',
            'escort', 
            'mariner', 'equipment','speedboat', 'others'
            
        ]
        widgets = {
            'project': autocomplete.ModelSelect2(
                url='projects:relatedmodel-autocomplete',
                attrs={
                    'data-placeholder': 'Search for a related item...',
                    'data-minimum-input-length': 2,
                },
            ),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")

        if self.instance.pk is None:  # only check on create, not update
            if OperationalExpenditure.objects.filter(project=project).exists():
                raise ValidationError("This project already has an operational cost entry")
        return cleaned_data


class OperationalExpenditureUpdateForm(forms.ModelForm):
    class Meta:
        model = OperationalExpenditure
        fields = [
            'project','date', 'payment_method', 'receipt_number',
            'escort', 
            'mariner', 'equipment','speedboat', 'others'
            
        ]
        widgets = {
            'project': forms.Select(attrs={'readonly': 'True'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")

        if self.instance.pk is None:  # only check on create, not update
            if OperationalExpenditure.objects.filter(project=project).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This project already has an operational cost entry for the same date.")
        return cleaned_data