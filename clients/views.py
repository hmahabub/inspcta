from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from .models import Client
from .forms import ClientForm, ClientUpdateForm

from django.http import HttpResponseForbidden

class SuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to view this page.")
        return super().dispatch(request, *args, **kwargs)

class ClientListView(SuperuserRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'object_list'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        type_filter = self.request.GET.get('types')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(tax_id__icontains=search_query)
                )
            
        if type_filter:
            queryset = queryset.filter(types=type_filter)
            
        return queryset.order_by('name')

class ClientDetailView(SuperuserRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'object'

class ClientCreateView(PermissionRequiredMixin,SuperuserRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')
    permission_required = 'clients.add_client'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ClientUpdateView(PermissionRequiredMixin,SuperuserRequiredMixin, UpdateView):
    model = Client
    form_class = ClientUpdateForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')
    permission_required = 'clients.change_client'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

class ClientDeleteView(PermissionRequiredMixin,SuperuserRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')
    permission_required = 'clients.delete_client'