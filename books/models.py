from django.db import models
from employees.models import Employee
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Case, When, F, DecimalField, Sum
class BankBook(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT'),
    )

    bank_account = models.ForeignKey(
        'BankAccount',
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    particulars = models.CharField(max_length=300)
    cheque_no = models.CharField(max_length=100)
    cheque_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = _('Bank Book Entry')
        verbose_name_plural = _('Bank Book Entries')

    def __str__(self):
        return f"{self.amount} ({self.date})"

    def date_update(self, query, current_balance):
        instance = query.first()
        if instance.transaction_type in ['CREDIT']: 
            instance.current_balance = current_balance + instance.amount
        elif instance.transaction_type in ['DEBIT']:
            instance.current_balance = current_balance - instance.amount
        current_balance = instance.current_balance
        instance.save()
        if query.exclude(id=instance.id):
            return self.date_update(query.exclude(id=instance.id), current_balance)
        else:
            return True

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only set on first save (object creation)
            queryset = BankBook.objects.filter(date__gt=self.date).order_by('date','id')
            queryset_lesser = BankBook.objects.filter(date__lte=self.date).order_by('date','id')

            total_CREDITs = queryset_lesser.filter(
                transaction_type__in=['CREDIT']
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_DEBITs = queryset_lesser.filter(
                transaction_type__in=['DEBIT']
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            current_balance = total_CREDITs - total_DEBITs

            if self.transaction_type in ['CREDIT']:
                self.current_balance = current_balance + self.amount
            elif self.transaction_type in ['DEBIT']:
                self.current_balance = current_balance - self.amount

            current_balance = self.current_balance
            if queryset:
                self.date_update(queryset, current_balance)

        super().save(*args, **kwargs)

class CashBook(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT'),
    )

    date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    particulars = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = _('Cash Book Entry')
        verbose_name_plural = _('Cash Book Entries')

    def __str__(self):
        return f"{self.amount} ({self.date})"

    def date_update(self, query, current_balance):
        instance = query.first()
        if instance.transaction_type in ['CREDIT']: 
            instance.current_balance = current_balance + instance.amount
        elif instance.transaction_type in ['DEBIT']:
            instance.current_balance = current_balance - instance.amount
        current_balance = instance.current_balance
        instance.save()
        if query.exclude(id=instance.id):
            return self.date_update(query.exclude(id=instance.id), current_balance)
        else:
            return True

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only set on first save (object creation)
            queryset = CashBook.objects.filter(date__gt=self.date).order_by('date','id')
            queryset_lesser = CashBook.objects.filter(date__lte=self.date).order_by('date','id')

            total_CREDITs = queryset_lesser.filter(
                transaction_type__in=['CREDIT']
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_DEBITs = queryset_lesser.filter(
                transaction_type__in=['DEBIT']
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            current_balance = total_CREDITs - total_DEBITs
            if self.transaction_type in ['CREDIT']:
                self.current_balance = current_balance + self.amount
            elif self.transaction_type in ['DEBIT']:
                self.current_balance = current_balance - self.amount
            current_balance = self.current_balance
            if queryset:
                self.date_update(queryset, current_balance)

        super().save(*args, **kwargs)


class BankAccount(models.Model):
    ACCOUNT_TYPES = (
        ('CURRENT', 'Current Account'),
        ('SAVINGS', 'Savings Account'),
        ('FIXED', 'Fixed CREDIT'),
    )

    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['bank_name', 'name']
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')

    def __str__(self):
        return f"{self.bank_name} - {self.name} ({self.account_number})"

    def update_balance(self):
        total_CREDITs = self.transactions.filter(
            transaction_type__in=['CREDIT']
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_DEBITs = self.transactions.filter(
            transaction_type__in=['DEBIT']
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        self.current_balance = self.opening_balance + total_CREDITs - total_DEBITs
        self.save()