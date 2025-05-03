# expenditure/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from clients.models import Client
from projects.models import Project
from employees.models import Employee
from django.utils import timezone



class Expenditure(models.Model):
    EXPENDITURE_TYPES = (
        ('REGULAR', 'Regular'),
        ('PROVISIONAL', 'Provisional'),
        ('OPERATIONAL', 'Operational'),
    )
    
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('BKASH', 'bKash'),
        ('CHECK', 'Check'),
    )
    
    expenditure_type = models.CharField(
        max_length=20, 
        choices=EXPENDITURE_TYPES,
        verbose_name="Type of Expenditure"
    )
    
    
    date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    receipt_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-updated_at']

# 1. Regular Employee Project Cost
class RegularExpenditure(Expenditure):
	project = models.ForeignKey(
	Project,
	on_delete=models.PROTECT,
	related_name='project_regular'
	)
	employee = models.ForeignKey(
	Employee,
	on_delete=models.PROTECT,
	related_name='project_costs_regular'
	)
	ot_hours = models.IntegerField(default=0)
	ot_rate = models.IntegerField(default=50)
	conveyance = models.IntegerField(default=0)
	boat_fee = models.IntegerField(default=0)
	fooding_fee= models.IntegerField(default=0)
	hotel_fee = models.IntegerField(default=0)
	night_allownce = models.IntegerField(default=0)
	others = models.IntegerField(default=0)
	paid_in_advance = models.IntegerField(default=0)
	@property
	def ot(self):
		return self.ot_hours * self.ot_rate
	@property
	def total(self):
		total = self.ot + self.conveyance +self.boat_fee + self.fooding_fee + self.hotel_fee +self.night_allownce+self.others
		return total
	@property
	def net_payable(self):
		return self.total - self.paid_in_advance


# 2. Provisionary Employee Project Cost
class ProvisionaryExpenditure(Expenditure):
	project = models.ForeignKey(
	    Project,
	    on_delete=models.PROTECT,
	    related_name='project_provision'
	)
	employee = models.ForeignKey(
	    Employee,
	    on_delete=models.PROTECT,
	    related_name='project_costs_provisionary'
	)
	fixed_amount= models.IntegerField(default=0)
	ot_hours = models.IntegerField(default=0)
	ot_rate = models.IntegerField(default=50)
	conveyance = models.IntegerField(default=0)
	boat_fee = models.IntegerField(default=0)
	fooding_fee= models.IntegerField(default=0)
	hotel_fee = models.IntegerField(default=0)
	night_allownce = models.IntegerField(default=0)
	others = models.IntegerField(default=0)
	paid_in_advance = models.IntegerField(default=0)
	@property
	def ot(self):
		return self.ot_hours * self.ot_rate
	@property
	def total(self):
		total = self.ot + self.conveyance +self.boat_fee + self.fooding_fee + self.hotel_fee +self.night_allownce+self.others
		return total

	@property
	def net_payable(self):
		return self.total - self.paid_in_advance


# 3. Operational Cost
class OperationalExpenditure(Expenditure):
	project = models.ForeignKey(
	    Project,
	    on_delete=models.PROTECT,
	    related_name='project_operation'
	)
	escort = models.IntegerField(default=0)
	mariner = models.IntegerField(default=0)
	equipment = models.IntegerField(default=0)
	speedboat = models.IntegerField(default=0)
	others = models.IntegerField(default=0)
	@property
	def total(self):
		return self.escort + self.mariner + self.equipment + self.speedboat + self.others