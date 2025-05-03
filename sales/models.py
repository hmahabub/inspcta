# sales/models.py
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Project
from dashboard.models import CurrencyRate
from django.core.validators import MinValueValidator
from django.utils import timezone

class Sale(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('TK.', 'Bangladeshi Taka'),
    ]
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='sales_entry'
    )

    
    invoice_no = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()

    report_no = models.CharField(max_length=20)
    report_date = models.DateField()

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    job_order_no = models.CharField(max_length=20,blank=True,null=True)
    shipper = models.CharField(max_length=200,blank=True,null=True)
    buyer = models.CharField(max_length=200,blank=True,null=True)
    cargo = models.CharField(max_length=80,blank=True,null=True)
    bl_qtn = models.CharField(max_length=80,blank=True,null=True)
    ins_qtn = models.CharField(max_length=80,blank=True,null=True)
    date_of_ins = models.CharField(max_length=80,blank=True,null=True)
    plc_of_ins = models.CharField(max_length=80,blank=True,null=True)

    recieved_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    @property
    def total_amount(self):
        return sum(task.cost for task in self.tasks.all())

    @property
    def vat(self):
        if self.project.client.types == 'INT':
            vat_amount = 0
        else:
            vat_amount = self.total_amount * .15
        return vat_amount

    @property
    def net_recieved(self):
        return self.recieved_amount - self.vat

    @property
    def balance_amount(self):
        return self.total_amount - self.recieved_amount

    @property
    def bdt_equivalent(self):
        year = self.invoice_date.year
        records = CurrencyRate.objects.filter(currency=self.currency)
        exact = records.filter(year=year).first()
        if exact:
            return exact.bdt_equivalent

        # Annotate absolute difference and order by it
        closest = records.annotate(
            diff=Abs(F('year') - year)
        ).order_by('diff').first()

        return closest.bdt_equivalent if closest else None
        


    def save(self, *args, **kwargs):
        if not self.invoice_no:
            current_year = timezone.now().year  # e.g., 2025
            year_prefix = f"IBL/{current_year:04d}/"

            # Count how many projects exist this year
            existing_projects = Sale.objects.filter(invoice_no__startswith=year_prefix).count()
            invoice_no = existing_projects + 1
            self.invoice_no = f"{year_prefix}{invoice_no:05d}"

        if not self.report_no:
            current_year = timezone.now().year % 100  # e.g., 2025 → 25
            year_prefix = f"{current_year:02d}IBLR"

            # Count how many projects exist this year
            existing_projects = Sale.objects.filter(report_no__startswith=year_prefix).count()
            report_no = existing_projects + 1
            self.report_no = f"{year_prefix}{report_no:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.invoice_no} - {self.invoice_date}"

class Task(models.Model):
    sale = models.ForeignKey(Sale, related_name='tasks', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.cost}"

@receiver(post_save, sender=Sale)
def update_project_status(sender, instance, created, **kwargs):
    """Signal to mark project complete when sales entry is created"""
    if created:
        instance.project.status = 'COMPLETED'
        instance.project.actual_end = instance.invoice_date
        instance.project.save()

