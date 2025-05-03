# Projects/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Project
from clients.models import Client
from django_select2.forms import ModelSelect2Widget
from django.utils import timezone
from datetime import timedelta


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_number', 'vessel_name',
            'client', 'starting', 'ending', 'actual_end', 'status',
            
        ]
        widgets = {
            'project_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_project_number(self):
        project_number = self.cleaned_data.get('project_number')
        if Project.objects.filter(project_number=project_number).exists():
            raise ValidationError("This project_number is already in use.")
        return project_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Only for creation
            today = timezone.now().date()
            one_month = today + timedelta(days=30)
            self.fields['starting'].initial = today
            self.fields['ending'].initial = one_month


            current_year = timezone.now().year % 100
            year_prefix = f"{current_year:02d}IBL"
            count = Project.objects.filter(project_number__startswith=year_prefix).count() + 1
            next_code = f"{year_prefix}{count:04d}"
            self.fields['project_number'].initial = next_code
            self.fields['project_number'].disabled = True


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_number', 'vessel_name',
            'client', 'starting', 'ending', 'actual_end', 'status',
            
        ]
        widgets = {
            'project_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'client': ModelSelect2Widget(
                model=Client,
                search_fields=['name__icontains']
                ),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_project_number(self):
        project_number = self.cleaned_data.get('project_number')
        if Project.objects.filter(project_number=project_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This project_number is already in use.")
        return project_number