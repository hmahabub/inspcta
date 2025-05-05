from django.views.generic import ListView
from django.contrib.auth import get_user_model
from .models import ActivityLog
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()

class ActivityLogListView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'activity_log/list.html'  # Update with your template path
    context_object_name = 'object_list'
    paginate_by = 20  # Optional: Add pagination

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user if provided in GET params
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user__id=user_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass all users to the template for the dropdown
        context['users'] = User.objects.all().order_by('username')
        return context