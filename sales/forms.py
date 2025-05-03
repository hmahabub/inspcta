from django import forms
from .models import Sale, Task
from django.utils import timezone
from dal import autocomplete

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['project', 'invoice_no', 'invoice_date', 'report_no', 'report_date', 'currency',
        'job_order_no', 'shipper', 'buyer', 'cargo', 'bl_qtn', 'ins_qtn', 'date_of_ins', 'plc_of_ins', 
        'recieved_amount'

        ]
        widgets = {
            'project': autocomplete.ModelSelect2(
                url='projects:relatedmodel-autocomplete',
                attrs={
                    'data-placeholder': 'Search for a related item...',
                    'data-minimum-input-length': 2,
                },
            ),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'invoice_no' : forms.TextInput(attrs={'readonly':'readonly'}),
            'report_no' : forms.TextInput(attrs={'readonly':'readonly'}),
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:  # Only for creation
            today = timezone.now().date()
            self.fields['invoice_date'].initial = today
            self.fields['report_date'].initial = today

            current_year = timezone.now().year  # e.g., 2025
            year_prefix = f"IBL/{current_year:04d}/"
            # Count how many projects exist this year
            existing_projects = Sale.objects.filter(invoice_no__startswith=year_prefix).count()
            invoice_no = existing_projects + 1
            next_code = f"{year_prefix}{invoice_no:05d}"
            self.fields['invoice_no'].initial = next_code
            self.fields['invoice_no'].disabled = True

            current_year = timezone.now().year % 100  # e.g., 2025 → 25
            year_prefix = f"{current_year:02d}IBLR"
            # Count how many projects exist this year
            existing_projects = Sale.objects.filter(report_no__startswith=year_prefix).count()
            report_no = existing_projects + 1
            next_code = f"{year_prefix}{report_no:04d}"
            self.fields['report_no'].initial = next_code
            self.fields['report_no'].disabled = True
        else:
            self.fields['project'].disabled = True


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['description', 'cost']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Task description'}),
            'cost': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }


TaskFormSet = forms.inlineformset_factory(
    Sale, 
    Task, 
    form=TaskForm,
    extra=1,  # Show 3 empty forms by default
    can_delete=True,
    can_delete_extra=True,
    max_num=20,  # Maximum number of tasks allowed
    validate_max=True
)