import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


def _setup_japanese_font():
    font_name = 'JapaneseFont'
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    win_fonts = [
        'C:/Windows/Fonts/msgothic.ttc',
        'C:/Windows/Fonts/meiryo.ttc',
        'C:/Windows/Fonts/msmincho.ttc',
    ]
    for font_path in win_fonts:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except Exception:
                continue

    try:
        cid_font = 'HeiseiKakuGo-W5'
        pdfmetrics.registerFont(UnicodeCIDFont(cid_font))
        return cid_font
    except Exception:
        pass

    return 'Helvetica'


def generate_reservation_pdf(reservation):
    font_name = _setup_japanese_font()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontName=font_name,
        fontSize=18, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14, spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'],
        fontName=font_name,
        fontSize=11, spaceAfter=6
    )

    elements = []
    elements.append(Paragraph('予約票 / Reservation Voucher', title_style))
    elements.append(Spacer(1, 10*mm))

    data = [
        ['予約ID / Reservation ID', str(reservation.id)],
        ['施設名 / Facility', reservation.facility.name if reservation.facility else ''],
        ['利用日 / Date', reservation.reserved_date.strftime('%Y-%m-%d') if reservation.reserved_date else ''],
        ['開始時間 / Start', reservation.start_time.strftime('%H:%M') if reservation.start_time else ''],
        ['終了時間 / End', reservation.end_time.strftime('%H:%M') if reservation.end_time else ''],
        ['人数 / People', str(reservation.number_of_people)],
        ['利用目的 / Purpose', reservation.purpose or ''],
        ['ステータス / Status', reservation.status],
        ['発行日 / Issued', datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]

    table = Table(data, colWidths=[100*mm, 80*mm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(
        '※ この予約票は施設利用時に提示してください。 / Please present this voucher when using the facility.',
        normal_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
