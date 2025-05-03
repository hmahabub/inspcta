from django.contrib import admin
from .models import CurrencyRate, PDFTemplate
# Register your models here.


admin.site.register(CurrencyRate)
admin.site.register(PDFTemplate)