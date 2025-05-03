# LV/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import LV, MV
from django.utils import timezone

class LVForm(forms.ModelForm):
    class Meta:
        model = LV
        exclude = ['created_at', 'updated_at']

    def clean_vessel_name(self):
        vessel_name = self.cleaned_data.get('vessel_name')
        if LV.objects.filter(vessel_name=vessel_name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This vessel_name is already in use.")
        return vessel_name


class MVForm(forms.ModelForm):
    class Meta:
        model = MV
        exclude = ['created_at', 'updated_at']
        widgets = {
            'l_vessel': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.related_pk = kwargs.pop('pk', None)
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Only for creation
            today = timezone.now().date()
            self.fields['date'].initial = today
            self.fields['l_vessel'].initial = LV.objects.get(pk=self.related_pk)
            self.fields['l_vessel'].disabled = True
        else:
            self.fields['l_vessel'].disabled = True