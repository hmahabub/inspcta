from openpyxl import Workbook
from openpyxl.styles import Font
from django.http import HttpResponse


def export_project_report_excel(report_data, title="Project Report"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Report"

    headers = [
        "Project",
        "Regular Cost",
        "Provisional Cost",
        "Operational Cost",
        "Total Cost",
        "Sales",
        "Received",
        "Balance",
        "Sales (BDT)",
        "Received (BDT)"
    ]

    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    for row in report_data:
        ws.append([
            row["project"],
            row["regular"],
            row["provisional"],
            row["operational"],
            row["total_cost"],
            row["sales"],
            row["received"],
            row["balance"],
            row["sales_bdt"],
            row["received_bdt"],
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="project_report.xlsx"'

    wb.save(response)
    return response
