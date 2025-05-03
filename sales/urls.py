# sales/urls.py
from django.urls import path
from .views import SaleListView, SaleCreateView, SaleUpdateView, SaleDeleteView, SaleDetailView, SaleInvoiceView

app_name = 'sales' 

urlpatterns = [
    path('', SaleListView.as_view(), name='list'),
    path('create/', SaleCreateView.as_view(), name='create'),
    path('<int:pk>/', SaleDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', SaleUpdateView.as_view(), name='update'),
    path('<int:pk>/invoice/', SaleInvoiceView.as_view(), name='invoice'),
    path('<int:pk>/delete/', SaleDeleteView.as_view(), name='delete'),
]