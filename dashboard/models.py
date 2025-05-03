from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _

# Create your models here.


class CurrencyRate(models.Model):
	CURRENCY_CHOICES = [
	('USD', 'US Dollar'),
	('EUR', 'Euro'),
	('TK.', 'Bangladeshi Taka'),
	]

	current_year = datetime.now().year
	year_choices = [(a,a) for a in range(current_year, current_year - 6, -1)]

	currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
	year = models.IntegerField(_('year'), choices=year_choices, default=current_year)
	bdt_equivalent = models.DecimalField(max_digits=6, decimal_places=2)

	def __str__(self):
		return f"{self.currency} - {self.year}"


class PDFTemplate(models.Model):
	method_choice = [('I','Invoice'),('PR','Payroll_Regular'),('PC','Payroll_Casual'),('CB','Cash_Book'),('BB','Bank_Book')]
	isfor = models.CharField(max_length=40,choices=method_choice)
	src_code = models.TextField()
	is_default = models.BooleanField(default=True)

	def __str__(self):
		return self.isfor