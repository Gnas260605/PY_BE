from __future__ import annotations

import csv
from io import StringIO

from app.db.connection import connection_scope
from app.reports import repository
from app.reports.schemas import TechnicianWorkloadResponse
from app.tickets.schemas import TicketListQuery, TicketSummaryResponse, DashboardStatsResponse
import io
import openpyxl
from openpyxl.styles import Font, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime


CATEGORY_LABELS = {
    "INCIDENT": "Sự cố",
    "SERVICE_REQUEST": "Yêu cầu dịch vụ",
    "MAINTENANCE": "Bảo trì",
    "ACCESS_REQUEST": "Cấp quyền",
}

PRIORITY_LABELS = {
    "URGENT": "Khẩn cấp",
    "HIGH": "Cao",
    "MEDIUM": "Trung bình",
    "LOW": "Thấp",
}

STATUS_LABELS = {
    "OPEN": "Chờ tiếp nhận",
    "ASSIGNED": "Đã phân công",
    "IN_PROGRESS": "Đang xử lý",
    "RESOLVED": "Đã giải quyết",
    "CLOSED": "Đã đóng",
}

CSV_HEADERS = [
    "Mã sự cố",
    "Tiêu đề",
    "Phân loại",
    "Mức độ ưu tiên",
    "Trạng thái",
    "Người yêu cầu",
    "KTV phụ trách",
    "Thiết bị liên quan",
    "Thời gian tạo",
    "Cập nhật lần cuối",
]


def get_technician_workload() -> list[TechnicianWorkloadResponse]:
    with connection_scope() as connection:
        rows = repository.get_technician_workload(connection)
    return [TechnicianWorkloadResponse(**row) for row in rows]


def export_tickets_csv(query: TicketListQuery) -> str:
    with connection_scope() as connection:
        rows = repository.list_tickets_for_export(
            connection,
            status=query.status,
            priority=query.priority,
            category=query.category,
            technician_id=query.technician_id,
            user_id=query.user_id,
            keyword=query.keyword,
        )

    output = StringIO()
    output.write("\ufeff")  # UTF-8 BOM for seamless Excel compatibility
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for row in rows:
        ticket_id = f"#TK-{row['id']:04d}" if row.get("id") else "-"
        category = CATEGORY_LABELS.get(row.get("category"), row.get("category") or "-")
        priority = PRIORITY_LABELS.get(row.get("priority"), row.get("priority") or "-")
        status_val = STATUS_LABELS.get(row.get("status"), row.get("status") or "-")
        creator = row.get("creator_name") or (f"User #{row.get('user_id')}" if row.get("user_id") else "-")
        technician = row.get("technician_name") or "Chưa phân công"

        if row.get("device_code") and row.get("device_name"):
            device = f"{row['device_code']} ({row['device_name']})"
        elif row.get("device_name"):
            device = str(row["device_name"])
        else:
            device = "-"

        created = str(row.get("created_at") or "-")
        updated = str(row.get("updated_at") or "-")

        writer.writerow([
            ticket_id,
            row.get("title") or "-",
            category,
            priority,
            status_val,
            creator,
            technician,
            device,
            created,
            updated,
        ])

    return output.getvalue()


def export_tickets_excel(query: TicketListQuery) -> io.BytesIO:
    with connection_scope() as connection:
        rows = repository.list_tickets_for_export(
            connection,
            status=query.status,
            priority=query.priority,
            category=query.category,
            technician_id=query.technician_id,
            user_id=query.user_id,
            keyword=query.keyword,
        )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tickets Export"

    for col_num, header_title in enumerate(CSV_HEADERS, 1):
        cell = ws.cell(row=1, column=col_num, value=header_title)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for row_num, row in enumerate(rows, 2):
        ticket_id = f"#TK-{row['id']:04d}" if row.get("id") else "-"
        category = CATEGORY_LABELS.get(row.get("category"), row.get("category") or "-")
        priority = PRIORITY_LABELS.get(row.get("priority"), row.get("priority") or "-")
        status_val = STATUS_LABELS.get(row.get("status"), row.get("status") or "-")
        creator = row.get("creator_name") or (f"User #{row.get('user_id')}" if row.get("user_id") else "-")
        technician = row.get("technician_name") or "Chưa phân công"

        device = "-"
        if row.get("device_code") and row.get("device_name"):
            device = f"{row['device_code']} ({row['device_name']})"
        elif row.get("device_name"):
            device = str(row["device_name"])

        ws.cell(row=row_num, column=1, value=ticket_id)
        ws.cell(row=row_num, column=2, value=row.get("title") or "-")
        ws.cell(row=row_num, column=3, value=category)
        ws.cell(row=row_num, column=4, value=priority)
        ws.cell(row=row_num, column=5, value=status_val)
        ws.cell(row=row_num, column=6, value=creator)
        ws.cell(row=row_num, column=7, value=technician)
        ws.cell(row=row_num, column=8, value=device)
        ws.cell(row=row_num, column=9, value=str(row.get("created_at") or "-"))
        ws.cell(row=row_num, column=10, value=str(row.get("updated_at") or "-"))

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_dashboard_pdf(stats: DashboardStatsResponse) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1
    
    elements.append(Paragraph(f"Dashboard Statistics Report", title_style))
    elements.append(Paragraph(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    overview_data = [
        ["Metric", "Total Count"],
        ["Total Tickets", str(stats.total_tickets)],
        ["Total Devices", str(stats.total_devices)],
        ["Total Users", str(stats.total_users)],
    ]
    overview_table = Table(overview_data, colWidths=[200, 100])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("System Overview", styles['Heading2']))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))
    
    status_data = [["Status", "Count"]]
    for item in stats.status_counts:
        status_data.append([item["status"], str(item["count"])])
        
    status_table = Table(status_data, colWidths=[200, 100])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Tickets by Status", styles['Heading2']))
    elements.append(status_table)
    elements.append(Spacer(1, 20))
    
    priority_data = [["Priority", "Count"]]
    for item in stats.priority_counts:
        priority_data.append([item["priority"], str(item["count"])])
        
    priority_table = Table(priority_data, colWidths=[200, 100])
    priority_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.indianred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Tickets by Priority", styles['Heading2']))
    elements.append(priority_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
