"""
Portable PDF generation for digital ASCAI membership cards.
"""
from __future__ import annotations

from io import BytesIO

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .assets import load_logo_reader
from .data import build_member_card_data
from .drawing import CARD_H, CARD_W, draw_membership_card_back, draw_membership_card_front
from .membership_card_pdf import membership_card_filename


def _draw_card(pdf, draw, card_data, logo):
    """Keep decorative ribbons and watermarks inside the physical card edge."""
    pdf.saveState()
    boundary = pdf.beginPath()
    boundary.roundRect(0, 0, CARD_W, CARD_H, 3.6 * mm)
    pdf.clipPath(boundary, stroke=0, fill=0)
    draw(pdf, 0, 0, card_data, logo)
    pdf.restoreState()


def generate_membership_card_pdf(dues, request) -> BytesIO:
    card_data = build_member_card_data(dues, request)
    logo = load_logo_reader()
    output = BytesIO()
    page_w, page_h = 190 * mm, 80 * mm
    pdf = canvas.Canvas(output, pagesize=(page_w, page_h))
    pdf.setTitle(membership_card_filename(card_data))

    preview_scale = 1
    gap = 6 * mm
    total_w = CARD_W * preview_scale * 2 + gap
    start_x = (page_w - total_w) / 2
    card_y = (page_h - CARD_H * preview_scale) / 2 - 2 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(page_w / 2, page_h - 8 * mm, "ASCAI Lazio | Digital membership card")
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        page_w / 2,
        page_h - 12 * mm,
        "Front and back | Keep this PDF with you. Validity dates are shown on the card.",
    )
    pdf.saveState()
    pdf.translate(start_x, card_y)
    pdf.scale(preview_scale, preview_scale)
    _draw_card(pdf, draw_membership_card_front, card_data, logo)
    pdf.restoreState()
    pdf.saveState()
    pdf.translate(start_x + CARD_W * preview_scale + gap, card_y)
    pdf.scale(preview_scale, preview_scale)
    _draw_card(pdf, draw_membership_card_back, card_data, logo)
    pdf.restoreState()
    pdf.setFont("Helvetica", 7)
    pdf.drawString(start_x, card_y - 6 * mm, "FRONT")
    pdf.drawString(start_x + CARD_W * preview_scale + gap, card_y - 6 * mm, "BACK")
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output


def generate_membership_card_print_pdf(dues, request) -> BytesIO:
    card_data = build_member_card_data(dues, request)
    logo = load_logo_reader()
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=(CARD_W, CARD_H))
    pdf.setTitle(membership_card_filename(card_data, print_ready=True))

    _draw_card(pdf, draw_membership_card_front, card_data, logo)
    pdf.showPage()
    _draw_card(pdf, draw_membership_card_back, card_data, logo)
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output
