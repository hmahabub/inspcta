from django.urls import path
from .views import PDFTemplateCreateView

app_name = 'dashboard'

urlpatterns = [
    path('create-pdf-template/', PDFTemplateCreateView.as_view(), name='create-pdf-template'),
]