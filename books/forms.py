from django import forms
from .models import BankBook, CashBook, BankAccount
from django.core.validators import MinValueValidator
from django.utils import timezone

class BankBookForm(forms.ModelForm):
    amount = forms.DecimalField(
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = BankBook
        fields = [
            'bank_account', 'date', 'transaction_type', 'cheque_no','cheque_date' ,
            'amount', 'particulars'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'cheque_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['bank_account'].queryset = BankAccount.objects.filter(is_active=True)

        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
            self.fields['cheque_date'].initial = timezone.now().date()

class CashBookForm(forms.ModelForm):
    amount = forms.DecimalField(
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = CashBook
        fields = [
            'date', 'transaction_type', 'amount', 
            'particulars'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = [
            'name', 'account_number', 'bank_name', 'branch',
            'account_type', 'opening_balance', 'is_active', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'