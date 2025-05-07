from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from .models import Project
from .forms import ProjectCreateForm, ProjectUpdateForm
from django.utils import timezone
from dal import autocomplete

class RelatedModelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Project.objects.all()
        if self.q:
            qs = qs.filter(
                Q(project_number__icontains=self.q ) |
                Q(client__name__icontains=self.q)
                )
        return qs

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'object_list'
    paginate_by = 15
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')

        if search_query:
            queryset = queryset.filter(
                Q(project_number__icontains=search_query) |
                Q(client__name__icontains=search_query)
                )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.select_related('client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Project.PROJECT_STATUS
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now().date()
        return context

class ProjectCreateView(PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectCreateForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')
    permission_required = 'projects.add_project'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProjectUpdateView(PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')
    permission_required = 'projects.change_project'

# class ProjectDeleteView(PermissionRequiredMixin, DeleteView):
#     model = Project
#     template_name = 'projects/project_confirm_delete.html'
#     success_url = reverse_lazy('projects:list')
#     permission_required = 'projects.delete_project'