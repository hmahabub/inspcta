# clients/models.py
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    """
    Client model for Inspecta ERP with comprehensive contact management
    """
    class ClientTypes(models.TextChoices):
        LOCAL = 'LOC', _('Local')
        INTERNATIONAL = 'INT', _('International')

    # Core Fields
    name = models.CharField(
        _('Client Name'),
        max_length=100,
        help_text=_('Official business or individual name')
    )
    
    contact_person = models.CharField(
        _('Primary Contact'),
        max_length=100,
        blank=True,
        help_text=_('Main point of contact')
    )
    
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
        blank=True
    )
    
    address = models.TextField(
        _('Full Address'),
        max_length=200,
        blank=True
    )
    
    # Status Management
    types = models.CharField(
        _('Client Types'),
        max_length=3,
        choices=ClientTypes.choices,
        default=ClientTypes.INTERNATIONAL
    )
    
    # Additional Fields
    tax_id = models.CharField(
        _('Tax Identification Number'),
        max_length=30,
        blank=True,
        null=True
    )
    
    website = models.URLField(
        _('Website'),
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Internal Notes'),
        blank=True,
        null=True
    )
    
    # Metadata
    created_at = models.DateTimeField(
        _('Created Date'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('Last Updated'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['types']),
        ]

    def __str__(self):
        return f"{self.name} ({self.types})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('clients:detail', kwargs={'pk': self.pk})

    @property
    def primary_contact(self):
        """Formatted primary contact information"""
        if self.contact_person and self.phone:
            return f"{self.contact_person} | {self.phone}"
        return self.contact_person or self.email