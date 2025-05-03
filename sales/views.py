# sales/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Sale, Task
from .forms import SaleForm, TaskFormSet
from django.db.models import Q

from django.http import HttpResponseForbidden

class SuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)


class SaleListView(LoginRequiredMixin,SuperuserRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    ordering = ['-invoice_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(
                Q(invoice_no__icontains=search_query) )    
        return queryset


class SaleCreateView(PermissionRequiredMixin,SuperuserRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:list')
    permission_required  ='sales.add_sale'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['task_formset'] = TaskFormSet(self.request.POST)
        else:
            context['task_formset'] = TaskFormSet(queryset=Task.objects.none())  # Start with empty formset
        context['sale_form'] = context['form']  # Make form available in template as sale_form
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        task_formset = context['task_formset']
        if task_formset.is_valid():
            self.object = form.save()
            task_formset.instance = self.object
            task_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SaleUpdateView(PermissionRequiredMixin,SuperuserRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    permission_required  ='sales.change_sale'

    def get_success_url(self):
        return reverse_lazy('sales:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['task_formset'] = TaskFormSet(self.request.POST, instance=self.object)
        else:
            # This line is crucial - it loads existing tasks
            context['task_formset'] = TaskFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        task_formset = context['task_formset']
        
        if task_formset.is_valid():
            self.object = form.save()
            task_formset.instance = self.object
            task_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SaleDetailView(LoginRequiredMixin,SuperuserRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'

class SaleInvoiceView(LoginRequiredMixin,SuperuserRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/sale_invoice.html'
    context_object_name = 'info'

class SaleDeleteView(PermissionRequiredMixin,SuperuserRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:list')