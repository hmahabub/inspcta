from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Q, F, ExpressionWrapper, IntegerField
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from collections import defaultdict

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

        print(type(selected_month))

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
            grouped[emp_id]['net_payable'] = grouped[emp_id]['total_cost'] - grouped[emp_id]['paid_in_advance']
            total_net_payable += grouped[emp_id]['total_cost'] - grouped[emp_id]['paid_in_advance']

        

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

class OperationalExpenditureDetailView(LoginRequiredMixin, ListView):
    model = OperationalExpenditure
    template_name = 'operation_expenditure/expenditure_detail.html'
    context_object_name = 'expenditures'
    paginate_by = 10


    def get_total_expenditure(self, project_id):
        month = self.request.GET.get('pk')
        year = self.request.GET.get('year')
        
        regular = RegularExpenditure.objects.filter(project=project_id)
        provision = ProvisionaryExpenditure.objects.filter(project=project_id)
        operation = OperationalExpenditure.objects.filter(project=project_id)
        
        regular_total = sum(obj.total for obj in regular)
        provision_total = sum(obj.total for obj in provision)
        operation_total = sum(obj.total for obj in operation)
        total_amount  = regular_total + provision_total + operation_total
        return regular_total, provision_total, operation_total, total_amount

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        project_id = OperationalExpenditure.objects.get(pk=self.kwargs.get('pk')).project.id
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
