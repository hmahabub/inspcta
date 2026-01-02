from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse


def export_project_report_pdf(report_data, title="Project Financial Report"):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="project_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles['Title']))

    table_data = [[
        "Project", "Regular", "Provisional", "Operational",
        "Total Cost", "Sales", "Received", "Balance", "Sales (BDT)"
    ]]

    for row in report_data:
        table_data.append([
            row["project"],
            row["regular"],
            row["provisional"],
            row["operational"],
            row["total_cost"],
            row["sales"],
            row["received"],
            row["balance"],
            row["sales_bdt"],
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    doc.build(elements)

    return response
