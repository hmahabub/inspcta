# reports/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Report

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Exists, OuterRef
from projects.models import Project
from expenditure.models import RegularExpenditure, ProvisionaryExpenditure, OperationalExpenditure
from sales.models import Sale


class ProjectFinancialReportView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'reports/project_financial_report.html'
    context_object_name = 'object_list'
    paginate_by = 15
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # -------------------------
        # YEAR FILTER
        # -------------------------
        year = self.request.GET.get('year')
        if not year:
            # Default: last year
            year = timezone.now().year - 1
        else:
            year = int(year)

        # Only projects created in the selected year
        queryset = queryset.filter(created_at__year=year)

        # Only include projects with any transaction (expenditure or sale)
        queryset = queryset.filter(
            Q(project_regular__isnull=False) |
            Q(project_provision__isnull=False) |
            Q(project_operation__isnull=False) |
            Q(sales_entry__isnull=False)
        ).distinct()

        return queryset.select_related('client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get year from GET or default
        year = self.request.GET.get('year')
        if not year:
            year = timezone.now().year - 1
        else:
            year = int(year)
        context['year'] = year

        report = []

        for project in context['object_list']:

            # ---------------------------
            # Regular Expenditure
            # ---------------------------
            regular_cost = project.project_regular.aggregate(
                total=Coalesce(
                    Sum(
                        F('ot_hours') * F('ot_rate') +
                        F('conveyance') +
                        F('boat_fee') +
                        F('fooding_fee') +
                        F('hotel_fee') +
                        F('night_allownce') +
                        F('others')
                    ),
                    0
                )
            )['total']

            # ---------------------------
            # Provisionary Expenditure
            # ---------------------------
            provision_cost = project.project_provision.aggregate(
                total=Coalesce(
                    Sum(
                        F('fixed_amount') +
                        F('ot_hours') * F('ot_rate') +
                        F('conveyance') +
                        F('boat_fee') +
                        F('fooding_fee') +
                        F('hotel_fee') +
                        F('night_allownce') +
                        F('others')
                    ),
                    0
                )
            )['total']

            # ---------------------------
            # Operational Expenditure
            # ---------------------------
            operational_cost = project.project_operation.aggregate(
                total=Coalesce(
                    Sum(
                        F('escort') +
                        F('mariner') +
                        F('equipment') +
                        F('speedboat') +
                        F('others')
                    ),
                    0
                )
            )['total']

            # ---------------------------
            # Sales
            # ---------------------------
            sales_amount = project.sales_entry.aggregate(
                total=Coalesce(Sum('recieved_amount'), Decimal('0.00'))
            )['total']

            total_cost = regular_cost + provision_cost + operational_cost
            profit = sales_amount - total_cost

            report.append({
                'project': project,
                'regular_cost': regular_cost,
                'provision_cost': provision_cost,
                'operational_cost': operational_cost,
                'total_cost': total_cost,
                'sales_amount': sales_amount,
                'profit': profit,
            })

        # Totals
        context['totals'] = {
            'regular': sum(r['regular_cost'] for r in report),
            'provision': sum(r['provision_cost'] for r in report),
            'operational': sum(r['operational_cost'] for r in report),
            'cost': sum(r['total_cost'] for r in report),
            'sales': sum(r['sales_amount'] for r in report),
            'profit': sum(r['profit'] for r in report),
        }

        context['report'] = report

        return context



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