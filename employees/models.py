# employees/models.py
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Employee(models.Model):
    """
    Extended Employee model with HR, payroll, and emergency contact information
    """
    
    # Personal Information
    name = models.CharField(
        _('Employee Name'),
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
    
    # Employment Details
    is_regular = models.BooleanField(
        _('Regular Employee'),
        default=False,
        help_text=_('Check if the employee is regular/permanent')
    )
    
    DEPARTMENT_CHOICES = [
        ('HR', 'Human Resources'),
        ('FINANCE', 'Finance'),
        ('SALES', 'Sales'),
        ('IT', 'Information Technology'),
        ('OPS', 'Operations'),
        ('MGMT', 'Management'),
    ]
    department = models.CharField(
        _('Department'),
        max_length=10,
        choices=DEPARTMENT_CHOICES
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



    def validate_image_size(value):
        filesize = value.size
        max_size = 1 * 1024 * 1024   # 1 mb in bytes
        if filesize > max_size:
            raise ValidationError(
                _('The maximum file size that can be uploaded is 1 mb'),
                params={'value': value},
            )

    # Additional Fields
    photo = models.ImageField(
        _('Employee Photo'),
        upload_to='employee_photos/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text=_('Maximum file size allowed is 1 mb')
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
    
    # Emergency Contacts
    emergency_contact_person = models.CharField(
        _('Emergency Contact Name'),
        max_length=100,
        help_text=_('Primary emergency contact person')
    )
    
    RELATION_CHOICES = [
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('SPOUSE', 'Spouse'),
        ('SIBLING', 'Sibling'),
        ('FRIEND', 'Friend'),
        ('OTHER', 'Other'),
    ]
    relation_with_the_person = models.CharField(
        _('Relationship'),
        max_length=10,
        choices=RELATION_CHOICES
    )
    
    emergency_contact_1 = models.CharField(
        _('Emergency Contact Number'),
        max_length=17,
        validators=[phone_regex],
        help_text=_('Primary emergency phone number')
    )
    
    
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['-is_regular', 'name']
        permissions = [
            ('can_view_sensitive_data', 'Can view sensitive employee data'),
        ]
    
    def __str__(self):
        return f"{self.name} (NID:{self.nid})"
    
    @property
    def employment_status(self):
        return "Regular" if self.is_regular else "Casual"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('employees:detail', kwargs={'pk': self.pk})