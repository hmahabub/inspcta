# vessels/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import LV, MV
from .forms import LVForm, MVForm

class VesselListView(LoginRequiredMixin, ListView):
    model = LV
    template_name = 'vessels/vessel_list.html'
    context_object_name = 'vessels'
    paginate_by = 20

    def get_queryset(self):
        return LV.objects.order_by('vessel_name')

class VesselCreateView(PermissionRequiredMixin, CreateView):
	model = LV
	form_class = LVForm
	template_name = 'vessels/vessel_form.html'
	success_url = reverse_lazy('vessels:list')
	context_object_name = 'vessel'
	permission_required = 'vessel.add_lv'

	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super().form_valid(form)

class VesselUpdateView(PermissionRequiredMixin, UpdateView):
    model = LV
    form_class = LVForm
    template_name = 'vessels/vessel_form.html'
    permission_required = 'vessel.change_lv'

    def get_success_url(self):
        return reverse_lazy('vessels:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

class VesselDetailView(LoginRequiredMixin, DetailView):
    model = LV
    template_name = 'vessels/vessel_detail.html'
    context_object_name = 'vessel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class VesselDeleteView(PermissionRequiredMixin, DeleteView):
    model = LV
    template_name = 'vessels/vessel_confirm_delete.html'
    success_url = reverse_lazy('vessels:list')


class MVesselCreateView(PermissionRequiredMixin, CreateView):
    model = MV
    form_class = MVForm
    template_name = 'vessels/mvessel_form.html'
    success_url = reverse_lazy('vessels:list')
    permission_required = 'vessels.add_mv'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.kwargs.get('pk')
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class MVesselUpdateView(PermissionRequiredMixin, UpdateView):
    model = LV
    form_class = LVForm
    template_name = 'vessels/vessel_form.html'

    def get_success_url(self):
        return reverse_lazy('vessels:list')

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