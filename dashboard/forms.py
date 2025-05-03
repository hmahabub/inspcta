from django import forms
from .models import PDFTemplate
from django.core.validators import MinValueValidator
from django.utils import timezone



class PDFTemplateCreateForm(forms.ModelForm):
    class Meta:
        model = PDFTemplate
        fields = [
            'isfor', 'src_code', 'is_default'
        ]
        widgets = {
            'src_code': forms.Textarea(attrs={'rows': 3}),
        }