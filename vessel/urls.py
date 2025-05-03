from django.urls import path
from .views import (
    VesselListView, VesselDetailView,
    VesselCreateView, VesselUpdateView, VesselDeleteView, MVesselCreateView, MVesselUpdateView
)

app_name = 'vessels'

urlpatterns = [
    path('', VesselListView.as_view(), name='list'),
    path('create/', VesselCreateView.as_view(), name='create'),
    path('<int:pk>/', VesselDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', VesselUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', VesselDeleteView.as_view(), name='delete'),

    path('<int:pk>/mv-create/', MVesselCreateView.as_view(), name='mv-create'),
    path('<int:pk>/mv-update/', MVesselUpdateView.as_view(), name='mv-update'),
]