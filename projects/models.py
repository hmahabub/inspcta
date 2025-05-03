# projects/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from clients.models import Client
from employees.models import Employee
from django.utils import timezone

class Project(models.Model):
    PROJECT_STATUS = (
        ('PLANNING', 'Planning'),
        ('ONGOING', 'Ongoing'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    # Core Fields
    project_number = models.CharField(
        _('Project Number'),
        max_length=20,
        unique=True, 
        help_text=_('Unique project identifier (e.g., PROJ-2023-001)')
    )
    
    vessel_name = models.CharField(
        _('Vessel Name'),
        max_length=100,
        help_text=_('Name of vessel/ship/unit')
    )
    
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='projects',
        verbose_name=_('Client')
    )
    
    # Dates
    starting = models.DateField(
        _('Start Date'),
        help_text=_('Planned commencement date')
    )
    
    ending = models.DateField(
        _('End Date'),
        help_text=_('Planned completion date')
    )
    
    actual_end = models.DateField(
        _('Actual End Date'),
        null=True,
        blank=True,
        help_text=_('Actual completion date')
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=PROJECT_STATUS,
        default='PLANNING'
    )
    
    
    # Metadata
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-starting', 'project_number']
        indexes = [
            models.Index(fields=['project_number']),
            models.Index(fields=['vessel_name']),
            models.Index(fields=['status']),
            models.Index(fields=['starting', 'ending']),
        ]

    def __str__(self):
        return f"[{self.project_number}] - {self.client}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('projects:detail', kwargs={'pk': self.pk})

    @property
    def duration(self):
        """Calculate project duration in days"""
        if self.starting and self.ending:
            return (self.ending - self.starting).days
        return None

    @property
    def is_active(self):
        """Check if project is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'ONGOING' 
            and self.starting <= today 
            and (self.ending >= today or self.actual_end is None)
        )

    @property
    def progress(self):
        """Calculate project progress percentage (simplified example)"""
        if self.status == 'COMPLETED':
            return 100
        elif self.status == 'PLANNING':
            return 0
        elif self.starting and self.ending:
            from django.utils import timezone
            today = timezone.now().date()
            total_days = self.duration
            elapsed_days = (today - self.starting).days
            return min(90, max(10, int((elapsed_days / total_days) * 100)))
        return 0

    @property
    def has_sales_entry(self):
        """Check if project has an associated sales entry"""
        return hasattr(self, 'sales_entry')

    def save(self, *args, **kwargs):
        if not self.project_number:
            current_year = timezone.now().year % 100  # e.g., 2025 → 25
            year_prefix = f"{current_year:02d}IBL"

            # Count how many projects exist this year
            existing_projects = Project.objects.filter(project_number__startswith=year_prefix).count()
            project_number = existing_projects + 1

            self.project_number = f"{year_prefix}{project_number:04d}"
        super().save(*args, **kwargs)