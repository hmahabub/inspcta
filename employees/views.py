# employees/views.py
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, 
    CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from .models import Employee
from .forms import EmployeeCreateForm, EmployeeUpdateForm
from django.utils import timezone
from dal import autocomplete

class REmployeeRelatedModelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Employee.objects.all()
        if self.q:
            qs = qs.filter(is_regular=True)
            qs = qs.filter(
                Q(name__icontains=self.q )
                )
        return qs

class CEmployeeRelatedModelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Employee.objects.all()
        if self.q:
            qs = qs.filter(is_regular=False)
            qs = qs.filter(
                Q(name__icontains=self.q )
                )
        return qs

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'object_list'
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        department_filter = self.request.GET.get('department')
        status_filter = self.request.GET.get('is_regular')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(nid__icontains=search_query))
        
        if department_filter:
            queryset = queryset.filter(department=department_filter)
            
        if status_filter:
            if status_filter == 'regular':
                queryset = queryset.filter(is_regular=True)
            elif status_filter == 'probation':
                queryset = queryset.filter(is_regular=False)
                
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Employee.DEPARTMENT_CHOICES
        context['search_query'] = self.request.GET.get('q', '')
        context['department_filter'] = self.request.GET.get('department', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now().date()
        return context


class EmployeeCreateView(PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeCreateForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:list')
    permission_required = 'employees.add_employee'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class EmployeeUpdateView(PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:list')
    permission_required = 'employees.change_employee'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class EmployeeDeleteView(PermissionRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:list')
    permission_required = 'employees.delete_employee'

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False  # Soft delete instead of actual deletion
        employee.save()
        return HttpResponseRedirect(self.get_success_url())