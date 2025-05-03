# report/urls.py
from django.urls import path
from .views import ReportListView, ReportCreateView, ReportUpdateView, ReportDeleteView

app_name = 'reports' 

urlpatterns = [
    path('', ReportListView.as_view(), name='report-list'),
    path('new/', ReportCreateView.as_view(), name='report-create'),
    path('<int:pk>/edit/', ReportUpdateView.as_view(), name='report-update'),
    path('<int:pk>/delete/', ReportDeleteView.as_view(), name='report-delete'),
]