# MasterMariners/models.py
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class MasterMariner(models.Model):
    """
    Extended MasterMariner model with HR, payroll, and emergency contact information
    """
    
    # Personal Information
    name = models.CharField(
        _('MasterMariner Name'),
        max_length=100,
        help_text=_('Individual name')
    )

    nid = models.CharField(
        _('National ID'),
        max_length=20,
        unique=True,
        help_text=_('Government-issued national identification number')
    )
    
    MARITAL_STATUS = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    marital_status = models.CharField(
        _('Marital Status'),
        max_length=10,
        choices=MARITAL_STATUS,
        blank=True,
        null=True
    )
    
    designation = models.CharField(
        _('Designation'),
        max_length=100,
        help_text=_('Official job title/position')
    )
    
    join_date = models.DateField(
        _('Joining Date'),
        auto_now_add=True
    )
    
    # Contact Information
    email = models.EmailField(
        _('Email Address'),
        validators=[EmailValidator()],
        help_text=_('Primary contact email')
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be in format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(
        _('Phone Number'),
        validators=[phone_regex],
        max_length=17,
    )


    address = models.TextField(
        _('Current Address'),
        max_length=200
    )
    
    # Financial Information
    bkash = models.CharField(
        _('bKash Number'),
        max_length=15,
        blank=True,
        null=True,
        help_text=_('Mobile banking number for payments')
    )
    
    bank_name = models.CharField(
        _('Bank Name'),
        max_length=100,
        blank=True,
        null=True
    )
    
    account_number = models.CharField(
        _('Account Number'),
        max_length=30,
        blank=True,
        null=True,
        help_text=_('Bank account number for salary')
    )
    
    
    class Meta:
        verbose_name = _('MasterMariner')
        verbose_name_plural = _('MasterMariners')
        ordering = ['name']
        permissions = [
            ('can_view_sensitive_data', 'Can view sensitive Mastermariner data'),
        ]
    
    def __str__(self):
        return f"{self.name} (NID:{self.nid})"
    
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('mastermariners:detail', kwargs={'pk': self.pk})