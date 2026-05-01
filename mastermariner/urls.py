# MasterMariners/urls.py
from django.urls import path
from .models import MasterMariner
from dal import autocomplete
from .views import (
    MasterMarinerListView, MasterMarinerDetailView,
    MasterMarinerCreateView, MasterMarinerUpdateView, MasterMarinerDeleteView
)

app_name = 'mastermariner'

urlpatterns = [
    path('', MasterMarinerListView.as_view(), name='list'),
    path('create/', MasterMarinerCreateView.as_view(), name='create'),
    path('<int:pk>/', MasterMarinerDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', MasterMarinerUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', MasterMarinerDeleteView.as_view(), name='delete'),
    path('autocomplete/', 
         autocomplete.Select2QuerySetView.as_view(model=MasterMariner),
         name='relatedmodel-autocomplete'),
]