# reports/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Report

class ReportListView(ListView):
    model = Report
    template_name = 'reports/report_list.html'

class ReportCreateView(CreateView):
    model = Report
    fields = '__all__'
    success_url = reverse_lazy('report-list')
    template_name = 'reports/report_form.html'

class ReportUpdateView(UpdateView):
    model = Report
    fields = '__all__'
    success_url = reverse_lazy('report-list')
    template_name = 'reports/report_form.html'

class ReportDeleteView(DeleteView):
    model = Report
    success_url = reverse_lazy('report-list')
    template_name = 'reports/report_confirm_delete.html'