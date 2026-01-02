from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce

from expenditure.models import (
    RegularExpenditure,
    ProvisionaryExpenditure,
    OperationalExpenditure,
)

from sales.models import Sale
from projects.models import Project


def project_report(year=None, month=None):
    """
    If month is None → Yearly report
    If month provided → Monthly report
    """

    projects = Project.objects.all()
    report_data = []

    for project in projects:

        date_filter = {}
        if year:
            date_filter["date__year"] = year
        if month:
            date_filter["date__month"] = month

        # ---------------- COSTS ----------------
        regular_qs = RegularExpenditure.objects.filter(project=project, **date_filter)
        provisional_qs = ProvisionaryExpenditure.objects.filter(project=project, **date_filter)
        operational_qs = OperationalExpenditure.objects.filter(project=project, **date_filter)

        regular_total = sum(r.total for r in regular_qs)
        provisional_total = sum(p.total for p in provisional_qs)
        operational_total = sum(o.total for o in operational_qs)

        total_cost = regular_total + provisional_total + operational_total

        # ---------------- SALES ----------------
        sales_filter = {}
        if year:
            sales_filter["invoice_date__year"] = year
        if month:
            sales_filter["invoice_date__month"] = month

        sales = Sale.objects.filter(project=project, **sales_filter)

        total_sales = sum(s.total_amount for s in sales)
        received = sum(s.recieved_amount for s in sales)

        # Convert to BDT
        total_sales_bdt = sum(
            s.total_amount * s.bdt_equivalent for s in sales
        )

        received_bdt = sum(
            s.recieved_amount * s.bdt_equivalent for s in sales
        )

        report_data.append({
            "project": project.project_number,
            "regular": regular_total,
            "provisional": provisional_total,
            "operational": operational_total,
            "total_cost": total_cost,
            "sales": total_sales,
            "received": received,
            "balance": total_sales - received,
            "sales_bdt": total_sales_bdt,
            "received_bdt": received_bdt,
        })

    return report_data
