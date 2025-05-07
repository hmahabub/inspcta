from django.urls import path
from .views import (
    ProjectListView, ProjectDetailView,
    ProjectCreateView, ProjectUpdateView
)
from .views import RelatedModelAutocomplete

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('create/', ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', ProjectUpdateView.as_view(), name='update'),
    # path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='delete'),
    path('relatedmodel-autocomplete/', RelatedModelAutocomplete.as_view(), name='relatedmodel-autocomplete'),
]

