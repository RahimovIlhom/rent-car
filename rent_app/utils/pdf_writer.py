import os
from datetime import datetime
import locale
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Indenter
from reportlab.lib.styles import getSampleStyleSheet

locale.setlocale(locale.LC_ALL, '')


def pdf_writer(data):
    def format_date(date_str):
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime('%d-%m-%Y %H:%M')
        except Exception as e:
            return date_str

    def format_currency(value):
        try:
            return locale.format_string("%d", int(float(value)), grouping=True)
        except ValueError:
            return value

    # Update date formats in main details
    data['start_date'] = format_date(data['start_date'])
    data['end_date'] = format_date(data['end_date'])

    if data['rent_type'] == 'daily':
        rent_type = "Kunlik ijara"
        period_type = 'kun'
    elif data['rent_type'] == 'monthly':
        rent_type = "Oylik ijara"
        period_type = 'oy'
    elif data['rent_type'] == 'credit':
        rent_type = "Nasiya"
        period_type = 'oy'
    else:
        rent_type = "Noma'lum"
        period_type = 'noma\'lum'

    for schedule in data['payment_schedules']:
        schedule['due_date'] = format_date(schedule['due_date'])
        schedule['payment_closing_date'] = format_date(schedule['payment_closing_date'])

    # Create the PDF document with adjusted margins
    directory = "media/rentals/contracts"
    if not os.path.exists(directory):
        os.makedirs(directory)

    pdf_file = f"{directory}/contract{data['id']}.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Add title
    title = Paragraph("Ijara shartnoma", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Add main details
    main_details = [
        ("ID", data['id']),
        ("Xodim", f"{data['employee']['fullname']} {data['employee']['phone']}"),
        ("Ism-familiya", data['fullname']),
        ("Telefon raqam", data['phone']),
        ("Pasport", data['passport']),
        ("Ijara turi", rent_type),
        ("Ijara narxi", format_currency(data['rent_amount'])),
        (f"Ijara muddati", f"{data['rent_period']} ({period_type})"),
        ("Zalok", format_currency(data['initial_payment_amount'])),
        ("Boshlanish sanasi", data['start_date']),
        ("Tugash sanasi", data['end_date']),
        ("Umumiy miqdor", f"{format_currency(data['amount'])} {data['currency']}"),
        ("Umumiy jarima", f"{format_currency(data['total_penalty_amount'])} {data['currency']}"),
        ("Umumiy to'langan miqdor", f"{format_currency(data['total_paid_amount'])} {data['currency']}"),
        ("Umumiy qarzdorlik", f"{format_currency(data['total_amount'])} {data['currency']}"),
        ("Holat", "Ijara faol" if data['is_active'] else "Ijara yopilgan"),
    ]

    # Convert details to table format
    table_data = [[Paragraph(key, styles['Normal']), Paragraph(str(value), styles['Normal'])] for key, value in
                  main_details]
    details_table = Table(table_data, hAlign='LEFT', colWidths=[150, 300])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 12))

    # Add payment schedule details
    elements.append(Paragraph("To'lov jadvali", styles['Heading2']))
    payment_schedule_data = [
        ["T/r", "To'lov sanasi", "To'lov miqdori", "Jarima miqdori", "To'langan", "To'langan sanasi", "To'langan"]]

    num = 1
    for payment in data['payment_schedules']:
        payment_schedule_data.append([
            num,
            payment['due_date'],
            format_currency(payment['amount']),
            format_currency(payment['penalty_amount']),
            format_currency(payment['amount_paid']),
            payment['payment_closing_date'],
            "Ha" if payment['is_paid'] else "Yo'q",
        ])
        num += 1

    # Append totals
    payment_schedule_data.append([
        "",
        "Umumiy",
        f"{format_currency(data['amount'])} {data['currency']}",
        f"{format_currency(data['total_penalty_amount'])} {data['currency']}",
        f"{format_currency(data['total_paid_amount'])} {data['currency']}",
        f"Qarzdorlik: {format_currency(data['total_amount'])} {data['currency']}",
        ""
    ])

    payment_schedule_table = Table(payment_schedule_data, hAlign='LEFT', colWidths=[30, 90, 80, 80, 80, 110, 50])
    payment_schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(payment_schedule_table)

    # Build the PDF
    document.build(elements)

    return pdf_file
