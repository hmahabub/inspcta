# employees/urls.py
from django.urls import path
from .views import (
    EmployeeListView, EmployeeDetailView,
    EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView, REmployeeRelatedModelAutocomplete, 
    CEmployeeRelatedModelAutocomplete
)

app_name = 'employees'

urlpatterns = [
    path('', EmployeeListView.as_view(), name='list'),
    path('create/', EmployeeCreateView.as_view(), name='create'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', EmployeeUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', EmployeeDeleteView.as_view(), name='delete'),
    path('relatedmodel-autocomplete-r/', REmployeeRelatedModelAutocomplete.as_view(), name='relatedmodel-autocomplete-r'),
    path('relatedmodel-autocomplete-p/', CEmployeeRelatedModelAutocomplete.as_view(), name='relatedmodel-autocomplete-p'),
]