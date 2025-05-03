from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Q
from .models import BankBook, CashBook, BankAccount
from .forms import BankBookForm, CashBookForm, BankAccountForm
from django.db.models import Case, When, F, DecimalField, Sum

from django.db.models import Sum, F, Case, When, DecimalField
from django.db.models.functions import Coalesce


from django.utils import timezone
from datetime import timedelta

class BankBookListView(LoginRequiredMixin, ListView):
    model = BankBook
    template_name = 'books/bankbook_list.html'
    context_object_name = 'transactions'
    paginate_by = 30

    def get_queryset(self):
        account_id = self.request.GET.get('account',1)
        self.bank_account = BankAccount.objects.get(id=account_id)
        
        queryset = self.bank_account.transactions.all()

        today = timezone.now().date()
        one_month_before = today - timedelta(days=30)
        
        # Apply filters
        start_date = self.request.GET.get('start_date', one_month_before)
        end_date = self.request.GET.get('end_date', today)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Calculate running balance
        queryset = queryset.annotate(
            debit_amount=Case(
                When(transaction_type__in=['DEBIT'], then=F('amount')),
                default=0,
                output_field=DecimalField()
            ),
            credit_amount=Case(
                When(transaction_type__in=['CREDIT'], then=F('amount')),
                default=0,
                output_field=DecimalField()
            )
        ).order_by('date', 'id')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account_id = self.request.GET.get('account',1)
        context['bank_account'] = BankAccount.objects.get(id=account_id)

        today = timezone.now().date()
        one_month_before = today - timedelta(days=30)
        
        start_date = self.request.GET.get('start_date', one_month_before)
        end_date = self.request.GET.get('end_date', today)

        context['start_date'] = start_date
        context['end_date'] = end_date
        
        # Calculate totals
        queryset = self.get_queryset()
        context['total_debit'] = queryset.aggregate(
            total=Sum('debit_amount')
        )['total'] or 0
        
        context['total_credit'] = queryset.aggregate(
            total=Sum('credit_amount')
        )['total'] or 0
        if queryset:
            context['last_balance'] = queryset.last().current_balance
        
        return context

class BankBookCreateView(PermissionRequiredMixin, CreateView):
    model = BankBook
    form_class = BankBookForm
    template_name = 'books/bankbook_form.html'
    success_url = reverse_lazy('books:bankbook_list')
    permission_required = 'books.add_bankbook'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.bank_account.update_balance()
        return response

# Cash Book Views
class CashBookListView(LoginRequiredMixin, ListView):
    model = CashBook
    template_name = 'books/cashbook_list.html'
    context_object_name = 'transactions'
    paginate_by = 30

    def get_queryset(self):
        today = timezone.now().date()
        one_month_before = today - timedelta(days=30)
        
        # Apply filters
        start_date = self.request.GET.get('start_date', one_month_before)
        end_date = self.request.GET.get('end_date', today)
        
        queryset = CashBook.objects.filter(date__gte=start_date, date__lte=end_date)
            
        # Calculate running balance
        queryset = queryset.annotate(
            debit_amount=Case(
                When(transaction_type__in=['DEBIT'], then=F('amount')),
                default=0,
                output_field=DecimalField()
            ),
            credit_amount=Case(
                When(transaction_type__in=['CREDIT'], then=F('amount')),
                default=0,
                output_field=DecimalField()
            )
        ).order_by('date', 'id')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()
        one_month_before = today - timedelta(days=30)
        
        start_date = self.request.GET.get('start_date', one_month_before)
        end_date = self.request.GET.get('end_date', today)

        context['start_date'] = start_date
        context['end_date'] = end_date
        
        # Calculate totals
        queryset = self.get_queryset()
        context['total_debit'] = queryset.aggregate(
            total=Sum('debit_amount')
        )['total'] or 0
        
        context['total_credit'] = queryset.aggregate(
            total=Sum('credit_amount')
        )['total'] or 0
        if queryset:
            context['last_balance'] = queryset.last().current_balance
        
        return context

class CashBookCreateView(PermissionRequiredMixin, CreateView):
    model = CashBook
    form_class = CashBookForm
    template_name = 'books/cashbook_form.html'
    success_url = reverse_lazy('books:cashbook_list')
    permission_required = 'books.add_cashbook'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

# Bank Account Views
class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = 'books/bankaccount_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return BankAccount.objects.all().annotate(
            current_balance_calculated=Sum(
                Case(
                    When(transactions__transaction_type__in=['CREDIT'], then=F('transactions__amount')),
                    default=0,
                    output_field=DecimalField()
                )
            ) - Sum(
                Case(
                    When(transactions__transaction_type__in=['DEBIT'], then=F('transactions__amount')),
                    default=0,
                    output_field=DecimalField()
                )
            ) + F('opening_balance')
        )

class BankAccountCreateView(PermissionRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'books/bankaccount_form.html'
    success_url = reverse_lazy('books:bankaccount_list')
    permission_required = 'books.add_bankaccount'