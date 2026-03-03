# mastermariners/views.py
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, 
    CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from .models import MasterMariner
from .forms import MasterMarinerCreateForm, MasterMarinerUpdateForm
from django.utils import timezone
from dal import autocomplete

class MasterMarinerListView(LoginRequiredMixin, ListView):
    model = MasterMariner
    template_name = 'mastermariner/mastermariner_list.html'
    context_object_name = 'object_list'
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(nid__icontains=search_query))
                
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class MasterMarinerDetailView(LoginRequiredMixin, DetailView):
    model = MasterMariner
    template_name = 'mastermariner/mastermariner_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now().date()
        return context


class MasterMarinerCreateView(PermissionRequiredMixin, CreateView):
    model = MasterMariner
    form_class = MasterMarinerCreateForm
    template_name = 'mastermariner/mastermariner_form.html'
    success_url = reverse_lazy('mastermariners:list')
    permission_required = 'mastermariner.add_mastermariner'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class MasterMarinerUpdateView(PermissionRequiredMixin, UpdateView):
    model = MasterMariner
    form_class = MasterMarinerUpdateForm
    template_name = 'mastermariner/mastermariner_form.html'
    success_url = reverse_lazy('mastermariners:list')
    permission_required = 'mastermariner.change_mastermariner'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class MasterMarinerDeleteView(PermissionRequiredMixin, DeleteView):
    model = MasterMariner
    template_name = 'mastermariner/mastermariner_confirm_delete.html'
    success_url = reverse_lazy('mastermariners:list')
    permission_required = 'mastermariner.delete_mastermariner'

    def delete(self, request, *args, **kwargs):
        mastermariner = self.get_object()
        mastermariner.is_active = False  # Soft delete instead of actual deletion
        mastermariner.save()
        return HttpResponseRedirect(self.get_success_url())