from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from clients.models import Client
from employees.models import Employee
from projects.models import Project
from expenditure.models import RegularExpenditure, ProvisionaryExpenditure, OperationalExpenditure
from sales.models import Sale
from django.utils import timezone
from django.urls import reverse_lazy
from .models import PDFTemplate
from .forms import PDFTemplateCreateForm
from activity_log.models import ActivityLog

class HomeView(TemplateView):
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = timezone.now().year
        
        if self.request.user.is_authenticated:    
            reg_exp = RegularExpenditure.objects.filter(date__icontains=year)
            pro_exp = ProvisionaryExpenditure.objects.filter(date__icontains=year)
            opt_exp = OperationalExpenditure.objects.filter(date__icontains=year)

            context["activity_logs"] = ActivityLog.objects.all()[:5]

            context['total_cost'] = (
                sum((obj.total for obj in reg_exp or [])) +
                sum((obj.total for obj in pro_exp or [])) +
                sum((obj.total for obj in opt_exp or []))
            )


            sales_dt = Sale.objects.filter(invoice_date__icontains=year)
            context['total_recieved'] = sum(obj.recieved_amount * obj.bdt_equivalent for obj in sales_dt)
            context['total_sales'] = sum(obj.total_amount * obj.bdt_equivalent for obj in sales_dt)
            context["profit"] = context['total_sales']-context['total_cost'] 
            context["net_profit"] = context['total_recieved'] - context['total_cost'] 

            context['year'] = year
            context['client_count'] = Client.objects.count()
            context['employee_count'] = Employee.objects.count()
            context['project_count'] = Project.objects.filter(starting__contains=year).count()
            
        return context

    def upload_data(self):
        # Load JSON
        client_data = json.loads(client_data_json)
        employee_data = json.loads(employee_data_json)

        

        # Upload Clients
        for item in client_data:
            # fields = item['fields']
            # Client.objects.create(
            #     pk=item['pk'],
            #     defaults=fields
            # )
            print(f"Uploaded Client: {fields['client_name']}")


class TemplateListView(LoginRequiredMixin, ListView):
    model = PDFTemplate
    template_name = 'dashboard/template_list.html'
    context_object_name = 'object_list'


class PDFTemplateCreateView(PermissionRequiredMixin, CreateView):
    model = PDFTemplate
    form_class = PDFTemplateCreateForm
    template_name = 'template/template_form.html'
    success_url = reverse_lazy('dashboard:create-pdf-template')
    permission_required = 'dashboard.add_pdftemplate'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)