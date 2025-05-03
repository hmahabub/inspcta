from django.db import models
from django.utils.translation import gettext_lazy as _

class LV(models.Model):
	vessel_name = models.CharField(
        _('Vessel Name'),
        max_length=100,
        help_text=_('Name of vessel/ship/unit')
    )
	code = models.CharField(max_length=15, blank=True, null=True)
	loa = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	brdth = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	fb = models.DecimalField(
		_('LT/FB (Declared)'),
		max_digits=6,decimal_places=3,blank=True, null=True)
	light_fpk = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	light_apk = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)

	# Metadata
	created_at = models.DateTimeField(
	_('Created At'),
	auto_now_add=True
	)

	updated_at = models.DateTimeField(
	_('Updated At'),
	auto_now=True
	)

	def __str__(self):
		return self.vessel_name

class MV(models.Model):
	l_vessel = models.ForeignKey(
        LV,
        on_delete=models.PROTECT,
        related_name='l_vessel',
        verbose_name=_('Lighter Vessel')
    )
	date = models.DateField()
	m_vessel = models.CharField(_('Motor Vessel Name'),max_length=40)
	co_eff = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	consignee = models.CharField(max_length=30, blank=True, null=True)
	cargo = models.CharField(max_length=30, blank=True, null=True)
	survey = models.CharField(max_length=30, blank=True, null=True)
	shrinkage = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	load_fb = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	density = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	cons = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	quantity = models.DecimalField(max_digits=8,decimal_places=3,blank=True, null=True)
	final_quantity =models.DecimalField(max_digits=8,decimal_places=3,blank=True, null=True)
	tpc = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	load_fpk = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	load_apk = models.DecimalField(max_digits=6,decimal_places=3,blank=True, null=True)
	forw_drft = models.CharField(max_length=30, blank=True, null=True)
	aft_drft = models.CharField(max_length=30, blank=True, null=True)
	mid_drft = models.CharField(max_length=30, blank=True, null=True)

	# Metadata
	created_at = models.DateTimeField(
	_('Created At'),
	auto_now_add=True
	)

	updated_at = models.DateTimeField(
	_('Updated At'),
	auto_now=True
	)
