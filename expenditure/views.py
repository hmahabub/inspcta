from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Q, F, ExpressionWrapper, IntegerField
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from collections import defaultdict
from mastermariner.models import MasterMariner


# Regular
class RegularExpenditureListView(LoginRequiredMixin, ListView):
    model = RegularExpenditure
    template_name = 'regular_expenditure/expenditure_list.html'
    context_object_name = 'object_list'
    paginate_by = 20

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    def get_queryset(self):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        employee = self.request.GET.get('employee')


        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        elif start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=30)
        elif end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

        queryset = RegularExpenditure.objects.filter(
                date__gte=start_date,   # Greater than or equal to start_date
                date__lte=end_date      # Less than or equal to end_date
            )

        if employee:
            queryset = queryset.filter(employee__name__icontains=employee)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        context['total_amount'] = sum(obj.total for obj in queryset)
        context['total_advance'] = sum(obj.paid_in_advance for obj in queryset)
        context['total_net_payable'] = context['total_amount'] - context['total_advance']
        return context


# Regular
class RegularExpenditurePerMonthView(LoginRequiredMixin, ListView):
    model = RegularExpenditure
    template_name = 'regular_expenditure/expenditure_per_month_list.html'
    context_object_name = 'object_list'

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    def get_queryset(self):
        selected_month = int(self.request.GET.get('month', datetime.now().month))
        selected_year = int(self.request.GET.get('year', datetime.now().year))


        # Calculate the total cost per record
        cost_expr = ExpressionWrapper(
            (F('ot_hours') * F('ot_rate')) +
            F('conveyance') +
            F('boat_fee') +
            F('fooding_fee') +
            F('hotel_fee') +
            F('night_allownce') +
            F('others'),
            output_field=IntegerField()
        )

        queryset = RegularExpenditure.objects.filter(
                date__month=selected_month,
                date__year=selected_year
            ).annotate(total_cost=cost_expr) \
            .select_related('employee', 'project')

        grouped = defaultdict(lambda: {
            'employee_name': '',
            'employee_nid': '',
            'employee_bkash': '',
            'projects': set(),
            'total_cost': 0,
            'paid_in_advance':0,
            'net_payable':0
        })

        total = 0
        total_paid_in_advance = 0
        total_net_payable = 0

        for record in queryset:
            emp_id = record.employee.id
            grouped[emp_id]['employee_name'] = record.employee.name
            grouped[emp_id]['employee_nid'] = record.employee.nid
            grouped[emp_id]['employee_bkash'] = record.employee.bkash
            grouped[emp_id]['projects'].add(f"{record.project.project_number}")
            grouped[emp_id]['total_cost'] += record.total_cost
            total += record.total_cost
            grouped[emp_id]['paid_in_advance'] += record.paid_in_advance
            total_paid_in_advance += record.paid_in_advance
            grouped[emp_id]['net_payable'] = grouped[emp_id]['total_cost'] - grouped[emp_id]['paid_in_advance']
        
        total_net_payable = total - total_paid_in_advance
        return grouped.values(), total, total_paid_in_advance, total_net_payable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'], context['total_amount'], context['total_paid_in_advance'], context['total_net_payable'] = self.get_queryset()
        context['selected_month'] = int(self.request.GET.get('month', datetime.now().month))
        context['selected_year'] = int(self.request.GET.get('year', datetime.now().year))
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        return context

class RegularExpenditureDetailView(LoginRequiredMixin, ListView):
    model = RegularExpenditure
    template_name = 'regular_expenditure/expenditure_detail.html'
    context_object_name = 'expenditures'
    paginate_by = 10

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    def get_queryset(self):
        employee_id = RegularExpenditure.objects.get(pk=self.kwargs.get('pk')).employee.id
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        queryset = RegularExpenditure.objects.filter(employee_id=employee_id)
        
        if month and year:
            queryset = queryset.filter(
                date__year=year,
                date__month=month
            )
        
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        employee_id = RegularExpenditure.objects.get(pk=self.kwargs.get('pk')).employee.id
        context['employee'] = get_object_or_404(Employee, pk=employee_id)
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        context['total_amount'] = sum(obj.total for obj in queryset)
        context['total_advance'] = sum(obj.paid_in_advance for obj in queryset)
        context['total_net_payable'] = sum(obj.net_payable for obj in queryset)
        return context

class RegularExpenditureCreateView(PermissionRequiredMixin, CreateView):
    model = RegularExpenditure
    form_class = RegularExpenditureCreateForm
    template_name = 'regular_expenditure/expenditure_form.html'
    success_url = reverse_lazy('expenditures:regular-list')
    permission_required = 'expenditure.add_regularexpenditure'  # all lowercase
    raise_exception = True

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)

class RegularExpenditureUpdateView(PermissionRequiredMixin, UpdateView):
    model = RegularExpenditure
    form_class = RegularExpenditureUpdateForm
    template_name = 'regular_expenditure/expenditure_form.html'
    success_url = reverse_lazy('expenditures:regular-list')
    permission_required = 'expenditure.change_regularexpenditure'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

class RegularExpenditureDeleteView(PermissionRequiredMixin, DeleteView):
    model = RegularExpenditure
    template_name = 'regular_expenditure/expenditure_confirm_delete.html'
    success_url = reverse_lazy('expenditures:regular-list')
    permission_required = 'expenditures.delete_employee'

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False  # Soft delete instead of actual deletion
        employee.save()
        return HttpResponseRedirect(self.get_success_url())

# Similarly for Provision and Operational...
class ProvisionaryExpenditureListView(LoginRequiredMixin, ListView):
    model = ProvisionaryExpenditure
    template_name = 'provision_expenditure/expenditure_list.html'
    context_object_name = 'object_list'
    paginate_by = 20

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    def get_queryset(self):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        employee = self.request.GET.get('employee')


        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        elif start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=30)
        elif end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

        queryset = ProvisionaryExpenditure.objects.filter(
                date__gte=start_date,   # Greater than or equal to start_date
                date__lte=end_date      # Less than or equal to end_date
            )

        if employee:
            queryset = queryset.filter(employee__name__icontains=employee)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        context['total_amount'] = sum(obj.total for obj in queryset)
        context['total_advance'] = sum(obj.paid_in_advance for obj in queryset)
        context['total_net_payable'] = sum(obj.net_payable for obj in queryset)
        return context

# Regular
class ProvisionaryExpenditurePerMonthView(LoginRequiredMixin, ListView):
    model = ProvisionaryExpenditure
    template_name = 'provision_expenditure/expenditure_per_month_list.html'
    context_object_name = 'object_list'

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    def get_queryset(self):
        selected_month = int(self.request.GET.get('month', datetime.now().month))
        selected_year = int(self.request.GET.get('year', datetime.now().year))

        # Calculate the total cost per record
        cost_expr = ExpressionWrapper(
            (F('ot_hours') * F('ot_rate')) +
            F('fixed_amount') +
            F('conveyance') +
            F('boat_fee') +
            F('fooding_fee') +
            F('hotel_fee') +
            F('night_allownce') +
            F('others'),
            output_field=IntegerField()
        )

        queryset = ProvisionaryExpenditure.objects.filter(
                date__month=selected_month,
                date__year=selected_year
            ).annotate(total_cost=cost_expr) \
            .select_related('employee', 'project')

        grouped = defaultdict(lambda: {
            'employee_name': '',
            'employee_nid': '',
            'employee_bkash': '',
            'projects': set(),
            'total_cost': 0,
            'paid_in_advance':0,
            'net_payable':0
        })

        total = 0
        total_paid_in_advance = 0
        total_net_payable = 0

        for record in queryset:
            emp_id = record.employee.id
            grouped[emp_id]['employee_name'] = record.employee.name
            grouped[emp_id]['employee_nid'] = record.employee.nid
            grouped[emp_id]['employee_bkash'] = record.employee.bkash
            grouped[emp_id]['projects'].add(f"{record.project.project_number}")
            grouped[emp_id]['total_cost'] += record.total_cost
            total += record.total_cost
            grouped[emp_id]['paid_in_advance'] += record.paid_in_advance
            total_paid_in_advance += record.paid_in_advance
            grouped[emp_id]['net_payable'] += record.total_cost - record.paid_in_advance
            total_net_payable += record.total_cost - record.paid_in_advance

        

        return grouped.values(), total, total_paid_in_advance, total_net_payable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'], context['total_amount'], context['total_paid_in_advance'], context['total_net_payable'] = self.get_queryset()
        context['selected_month'] = int(self.request.GET.get('month', datetime.now().month))
        context['selected_year'] = int(self.request.GET.get('year', datetime.now().year))
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        return context

class ProvisionaryExpenditureDetailView(LoginRequiredMixin, ListView):
    model = ProvisionaryExpenditure
    template_name = 'provision_expenditure/expenditure_detail.html'
    context_object_name = 'expenditures'
    paginate_by = 10

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    def get_queryset(self):
        employee_id = ProvisionaryExpenditure.objects.get(pk=self.kwargs.get('pk')).employee.id
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        queryset = ProvisionaryExpenditure.objects.filter(employee_id=employee_id)
        
        if month and year:
            queryset = queryset.filter(
                date__year=year,
                date__month=month
            )
        
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        employee_id = ProvisionaryExpenditure.objects.get(pk=self.kwargs.get('pk')).employee.id
        context['employee'] = get_object_or_404(Employee, pk=employee_id)
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        context['total_amount'] = sum(obj.total for obj in queryset)
        context['total_advance'] = sum(obj.paid_in_advance for obj in queryset)
        context['total_net_payable'] = sum(obj.net_payable for obj in queryset)
        return context

class ProvisionaryExpenditureCreateView(PermissionRequiredMixin, CreateView):
    model = ProvisionaryExpenditure
    form_class = ProvisionaryExpenditureCreateForm
    template_name = 'provision_expenditure/expenditure_form.html'
    success_url = reverse_lazy('expenditures:provision-list')
    permission_required = 'expenditure.add_provisionaryexpenditure'  # all lowercase
    raise_exception = True

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)


class ProvisionaryExpenditureUpdateView(PermissionRequiredMixin, UpdateView):
    model = ProvisionaryExpenditure
    form_class = ProvisionaryExpenditureUpdateForm
    template_name = 'provision_expenditure/expenditure_form.html'
    success_url = reverse_lazy('expenditures:provision-list')
    permission_required = 'expenditure.change_provisionaryexpenditure'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

class ProvisionaryExpenditureDeleteView(PermissionRequiredMixin, DeleteView):
    model = ProvisionaryExpenditure
    template_name = 'provision_expenditure/expenditure_confirm_delete.html'
    success_url = reverse_lazy('expenditures:provision-list')
    permission_required = 'expenditures.delete_employee'

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False  # Soft delete instead of actual deletion
        employee.save()
        return HttpResponseRedirect(self.get_success_url())

class OperationalExpenditureListView(LoginRequiredMixin, ListView):
    model = OperationalExpenditure
    template_name = 'operation_expenditure/expenditure_list.html'
    context_object_name = 'object_list'
    paginate_by = 20

    months = [ (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December') ]

    def get_queryset(self):
        search_query = self.request.GET.get('q')

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        elif start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=30)
        elif end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

        queryset = OperationalExpenditure.objects.filter(
                date__gte=start_date,   # Greater than or equal to start_date
                date__lte=end_date      # Less than or equal to end_date
            )

        if search_query:
            queryset = OperationalExpenditure.objects.filter(
                Q(project__project_number__icontains=search_query) |
                Q(project__client__name__icontains=search_query)
                )

        self.starting = start_date.date()
        self.ending = end_date.date()
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['starting'] = self.starting 
        context['ending'] = self.ending
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['months'] = self.months
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 6, -1)
        context['total_amount'] = sum(obj.total for obj in queryset)
        return context

class OperationalExpenditureDetailView(LoginRequiredMixin, DetailView):  # Changed to DetailView
    model = OperationalExpenditure
    template_name = 'operation_expenditure/expenditure_detail.html'
    context_object_name = 'expenditure'

    def get_total_expenditure(self, project_id):
        regular = RegularExpenditure.objects.filter(project=project_id)
        provision = ProvisionaryExpenditure.objects.filter(project=project_id)
        operation = OperationalExpenditure.objects.filter(project=project_id)
        
        regular_total = sum(obj.total for obj in regular)
        provision_total = sum(obj.total for obj in provision)
        operation_total = sum(obj.total for obj in operation)
        total_amount = regular_total + provision_total + operation_total
        return regular_total, provision_total, operation_total, total_amount

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expenditure = self.get_object()
        project_id = expenditure.project.id
        context['project'] = Project.objects.get(pk=project_id)
        context['regular_total'], context['provision_total'], context['operation_total'], context['total_amount'] = self.get_total_expenditure(project_id)
        return context

class OperationalExpenditureCreateView(PermissionRequiredMixin, CreateView):
    model = OperationalExpenditure
    form_class = OperationalExpenditureCreateForm
    template_name = 'operation_expenditure/expenditure_form.html'
    success_url = reverse_lazy('expenditures:operation-list')
    permission_required = 'expenditure.add_operationalexpenditure'  # all lowercase
    raise_exception = True

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)


class OperationalExpenditureUpdateView(PermissionRequiredMixin, UpdateView):
    model = OperationalExpenditure
    form_class = OperationalExpenditureUpdateForm
    template_name = 'operation_expenditure/expenditure_form.html'
    success_url = reverse_lazy('expenditures:operation-list')
    permission_required = 'expenditure.change_operationalxpenditure'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class OperationalExpenditureDeleteView(DeleteView):
    model = OperationalExpenditure
    template_name = 'operation_expenditure/expenditure_confirm_delete.html'
    success_url = reverse_lazy('expenditures:operation-list')
    permission_required = 'expenditures.delete_employee'

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False  # Soft delete instead of actual deletion
        employee.save()
        return HttpResponseRedirect(self.get_success_url())


# NEW: Project Expense Report View - FIXED (no is_active field)
class ProjectExpenseReportView(LoginRequiredMixin, ListView):
    """
    View to display all projects with their total expenses
    """
    model = Project
    template_name = 'expenditure_reports/project_expense_report.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        # Get all projects (no is_active filter since it doesn't exist)
        queryset = Project.objects.all()
        
        # Filter by project number or client name
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(project_number__icontains=search_query) |
                Q(client__name__icontains=search_query)
            )
        
        # Filter by date range based on project dates
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        self.start_date = start_date
        self.end_date = end_date
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            # Filter projects that are active during this period
            queryset = queryset.filter(
                Q(starting__lte=end_date) & 
                (Q(ending__gte=start_date) | Q(ending__isnull=True))
            )
            self.filter_by_date = True
            self.filter_start_date = start_date
            self.filter_end_date = end_date
        else:
            self.filter_by_date = False
            self.filter_start_date = None
            self.filter_end_date = None
        
        return queryset.order_by('-starting')
    
    def get_project_expenses(self, project):
        """Calculate all expenses for a project with optional date filtering"""
        
        # Base querysets
        regular_qs = RegularExpenditure.objects.filter(project=project)
        provision_qs = ProvisionaryExpenditure.objects.filter(project=project)
        operation_qs = OperationalExpenditure.objects.filter(project=project)
        
        # Apply date filters if provided
        if self.filter_by_date and self.filter_start_date and self.filter_end_date:
            regular_qs = regular_qs.filter(date__gte=self.filter_start_date, date__lte=self.filter_end_date)
            provision_qs = provision_qs.filter(date__gte=self.filter_start_date, date__lte=self.filter_end_date)
            operation_qs = operation_qs.filter(date__gte=self.filter_start_date, date__lte=self.filter_end_date)
        
        # Calculate totals
        regular_total = sum(obj.total for obj in regular_qs)
        provision_total = sum(obj.total for obj in provision_qs)
        operation_total = sum(obj.total for obj in operation_qs)
        
        # Calculate advances
        regular_advance = sum(obj.paid_in_advance for obj in regular_qs)
        provision_advance = sum(obj.paid_in_advance for obj in provision_qs)
        
        total_expense = regular_total + provision_total + operation_total
        total_advance = regular_advance + provision_advance
        net_payable = total_expense - total_advance
        
        # Get count of each type
        regular_count = regular_qs.count()
        provision_count = provision_qs.count()
        operation_count = operation_qs.count()
        
        return {
            'regular_total': regular_total,
            'provision_total': provision_total,
            'operation_total': operation_total,
            'total_expense': total_expense,
            'total_advance': total_advance,
            'net_payable': net_payable,
            'regular_count': regular_count,
            'provision_count': provision_count,
            'operation_count': operation_count,
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate expenses for each project
        projects_with_expenses = []
        grand_total_expense = 0
        grand_total_advance = 0
        grand_net_payable = 0
        
        for project in context['projects']:
            expense_data = self.get_project_expenses(project)
            projects_with_expenses.append({
                'project': project,
                'expenses': expense_data
            })
            grand_total_expense += expense_data['total_expense']
            grand_total_advance += expense_data['total_advance']
            grand_net_payable += expense_data['net_payable']
        
        context['projects_with_expenses'] = projects_with_expenses
        context['grand_total_expense'] = grand_total_expense
        context['grand_total_advance'] = grand_total_advance
        context['grand_net_payable'] = grand_net_payable
        
        # Add filter context
        context['search_query'] = self.request.GET.get('q', '')
        context['start_date'] = self.start_date
        context['end_date'] = self.end_date
        
        # Summary statistics
        context['total_projects'] = context['projects'].count()
        context['total_projects_with_expenses'] = len([p for p in projects_with_expenses if p['expenses']['total_expense'] > 0])
        
        return context


class ProjectExpenseDetailView(LoginRequiredMixin, TemplateView):
    """
    Detailed view of all expenses for a specific project
    """
    template_name = 'expenditure_reports/project_expense_detail.html'
    
    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs.get('pk'))
    
    def get_expenditures(self, project):
        """Get all expenditures with optional filtering"""
        
        # Base querysets with select_related for efficiency
        regular = RegularExpenditure.objects.filter(project=project).select_related('employee')
        provision = ProvisionaryExpenditure.objects.filter(project=project).select_related('employee')
        operation = OperationalExpenditure.objects.filter(project=project).select_related('master_mariner')
        
        # Apply date filters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            regular = regular.filter(date__gte=start_date)
            provision = provision.filter(date__gte=start_date)
            operation = operation.filter(date__gte=start_date)
            self.start_date = start_date
        else:
            self.start_date = None
            
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            regular = regular.filter(date__lte=end_date)
            provision = provision.filter(date__lte=end_date)
            operation = operation.filter(date__lte=end_date)
            self.end_date = end_date
        else:
            self.end_date = None
        
        # Apply expenditure type filter
        expense_type = self.request.GET.get('expense_type')
        if expense_type == 'regular':
            provision = ProvisionaryExpenditure.objects.none()
            operation = OperationalExpenditure.objects.none()
        elif expense_type == 'provision':
            regular = RegularExpenditure.objects.none()
            operation = OperationalExpenditure.objects.none()
        elif expense_type == 'operation':
            regular = RegularExpenditure.objects.none()
            provision = ProvisionaryExpenditure.objects.none()
        
        return {
            'regular': regular.order_by('-date'),
            'provision': provision.order_by('-date'),
            'operation': operation.order_by('-date'),
        }
    
    def get_totals(self, expenditures):
        """Calculate totals from expenditures"""
        regular_total = sum(e.total for e in expenditures['regular'])
        provision_total = sum(e.total for e in expenditures['provision'])
        operation_total = sum(e.total for e in expenditures['operation'])
        
        regular_advance = sum(e.paid_in_advance for e in expenditures['regular'])
        provision_advance = sum(e.paid_in_advance for e in expenditures['provision'])
        
        total_expense = regular_total + provision_total + operation_total
        total_advance = regular_advance + provision_advance
        net_payable = total_expense - total_advance
        
        return {
            'regular_total': regular_total,
            'provision_total': provision_total,
            'operation_total': operation_total,
            'total_expense': total_expense,
            'total_advance': total_advance,
            'net_payable': net_payable,
            'regular_count': expenditures['regular'].count(),
            'provision_count': expenditures['provision'].count(),
            'operation_count': expenditures['operation'].count(),
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        expenditures = self.get_expenditures(project)
        totals = self.get_totals(expenditures)
        
        context['project'] = project
        context['regular_expenditures'] = expenditures['regular']
        context['provision_expenditures'] = expenditures['provision']
        context['operation_expenditures'] = expenditures['operation']
        context['totals'] = totals
        
        # Filter context
        context['start_date'] = self.start_date.strftime('%Y-%m-%d') if self.start_date else ''
        context['end_date'] = self.end_date.strftime('%Y-%m-%d') if self.end_date else ''
        context['expense_type'] = self.request.GET.get('expense_type', '')
        
        # Chart data (optional, for visualization)
        context['chart_labels'] = ['Regular', 'Provisionary', 'Operational']
        context['chart_data'] = [totals['regular_total'], totals['provision_total'], totals['operation_total']]
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle export to CSV"""
        import csv
        
        if 'export_csv' in request.POST:
            project = self.get_project()
            expenditures = self.get_expenditures(project)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{project.project_number}_expenses.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Date', 'Type', 'Employee/Mariner', 'Description', 'Amount', 'Advance Paid', 'Net Payable'])
            
            # Write regular expenditures
            for exp in expenditures['regular']:
                writer.writerow([
                    exp.date.strftime('%Y-%m-%d'),
                    'Regular',
                    exp.employee.name,
                    f"OT: {exp.ot_hours}h @ {exp.ot_rate}/hr, Conveyance: {exp.conveyance}, Boat: {exp.boat_fee}, Food: {exp.fooding_fee}, Hotel: {exp.hotel_fee}, Night Allow: {exp.night_allownce}, Others: {exp.others}",
                    exp.total,
                    exp.paid_in_advance,
                    exp.net_payable
                ])
            
            # Write provision expenditures
            for exp in expenditures['provision']:
                writer.writerow([
                    exp.date.strftime('%Y-%m-%d'),
                    'Provisionary',
                    exp.employee.name,
                    f"Fixed: {exp.fixed_amount}, OT: {exp.ot_hours}h @ {exp.ot_rate}/hr, Conveyance: {exp.conveyance}, Boat: {exp.boat_fee}, Food: {exp.fooding_fee}, Hotel: {exp.hotel_fee}, Night Allow: {exp.night_allownce}, Others: {exp.others}",
                    exp.total,
                    exp.paid_in_advance,
                    exp.net_payable
                ])
            
            # Write operational expenditures
            for exp in expenditures['operation']:
                writer.writerow([
                    exp.date.strftime('%Y-%m-%d'),
                    'Operational',
                    exp.master_mariner.name if exp.master_mariner else 'N/A',
                    f"Escort: {exp.escort}, Mariner: {exp.mariner}, Equipment: {exp.equipment}, Speedboat: {exp.speedboat}, Others: {exp.others}",
                    exp.total,
                    'N/A',
                    exp.total
                ])
            
            return response
        
        return super().get(request, *args, **kwargs)