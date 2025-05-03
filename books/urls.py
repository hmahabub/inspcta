from django.urls import path
from .views import (
    BankBookListView, BankBookCreateView,
    CashBookListView, CashBookCreateView,
    BankAccountListView, BankAccountCreateView
)

app_name = 'books'

urlpatterns = [
    # Bank Book URLs
    path('bankbook/', BankBookListView.as_view(), name='bankbook_list'),
    path('bankbook/new/', BankBookCreateView.as_view(), name='bankbook_create'),
    
    # Cash Book URLs
    path('cashbook/', CashBookListView.as_view(), name='cashbook_list'),
    path('cashbook/new/', CashBookCreateView.as_view(), name='cashbook_create'),
    
    # Bank Account URLs
    path('bankaccounts/', BankAccountListView.as_view(), name='bankaccount_list'),
    path('bankaccounts/new/', BankAccountCreateView.as_view(), name='bankaccount_create'),
]