from django.urls import path
from .views import *
app_name = 'expenditures'

urlpatterns = [
    # Regular
    path('regular/', RegularExpenditureListView.as_view(), name='regular-list'),
    path('regular/<int:pk>/detail/', RegularExpenditureDetailView.as_view(), name='regular-detail'),
    path('regular/create/', RegularExpenditureCreateView.as_view(), name='regular-create'),
    path('regular/<int:pk>/update/', RegularExpenditureUpdateView.as_view(), name='regular-update'),
    path('regular/<int:pk>/delete/', RegularExpenditureDeleteView.as_view(), name='regular-delete'),
    path('regular-per-month/', RegularExpenditurePerMonthView.as_view(), name='regular-per-month'),


    # Provision
    path('provision/', ProvisionaryExpenditureListView.as_view(), name='provision-list'),
    path('provision/<int:pk>/detail/', ProvisionaryExpenditureDetailView.as_view(), name='provision-detail'),
    path('provision/create/', ProvisionaryExpenditureCreateView.as_view(), name='provision-create'),
    path('provision/<int:pk>/update/', ProvisionaryExpenditureUpdateView.as_view(), name='provision-update'),
    path('provision/<int:pk>/delete/', ProvisionaryExpenditureDeleteView.as_view(), name='provision-delete'),
    path('provision-per-month/', ProvisionaryExpenditurePerMonthView.as_view(), name='provision-per-month'),

    # Operational
    path('operational/', OperationalExpenditureListView.as_view(), name='operation-list'),
    path('operational/<int:pk>/detail/', OperationalExpenditureDetailView.as_view(), name='operation-detail'),
    path('operational/create/', OperationalExpenditureCreateView.as_view(), name='operation-create'),
    path('operational/<int:pk>/update/', OperationalExpenditureUpdateView.as_view(), name='operation-update'),
    path('operational/<int:pk>/delete/', OperationalExpenditureDeleteView.as_view(), name='operation-delete'),
]
