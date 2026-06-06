"""
Server-side ReportLab PDF generation for ASCAI membership cards.
"""
from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .assets import load_logo_reader
from .data import build_member_card_data
from .drawing import CARD_H, CARD_W, draw_membership_card_back, draw_membership_card_front


def membership_card_filename(card_data) -> str:
    return f"ascai-membership-card-{card_data.memberId}.pdf"


def generate_membership_card_pdf(dues, request) -> BytesIO:
    """Generate an A4 landscape preview with front/back side-by-side."""
    card_data = build_member_card_data(dues, request)
    logo = load_logo_reader()
    output = BytesIO()
    page_w, page_h = landscape(A4)
    pdf = canvas.Canvas(output, pagesize=(page_w, page_h))
    pdf.setTitle(membership_card_filename(card_data))

    preview_scale = 1.38
    gap = 16 * mm
    total_w = CARD_W * preview_scale * 2 + gap
    start_x = (page_w - total_w) / 2
    card_y = (page_h - CARD_H * preview_scale) / 2 - 2 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(page_w / 2, page_h - 18 * mm, "ASCAI Membership Card Preview")
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(page_w / 2, page_h - 23 * mm, "Preview is enlarged for review. Use Download Print Version for exact 85.6mm x 54mm card pages.")
    pdf.saveState()
    pdf.translate(start_x, card_y)
    pdf.scale(preview_scale, preview_scale)
    draw_membership_card_front(pdf, 0, 0, card_data, logo)
    pdf.restoreState()
    pdf.saveState()
    pdf.translate(start_x + CARD_W * preview_scale + gap, card_y)
    pdf.scale(preview_scale, preview_scale)
    draw_membership_card_back(pdf, 0, 0, card_data, logo)
    pdf.restoreState()
    pdf.setFont("Helvetica", 7)
    pdf.drawString(start_x, card_y - 6 * mm, "FRONT")
    pdf.drawString(start_x + CARD_W * preview_scale + gap, card_y - 6 * mm, "BACK")
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output


def generate_membership_card_print_pdf(dues, request) -> BytesIO:
    """Generate print-ready card pages: page 1 front, page 2 back."""
    card_data = build_member_card_data(dues, request)
    logo = load_logo_reader()
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=(CARD_W, CARD_H))
    pdf.setTitle(membership_card_filename(card_data))

    draw_membership_card_front(pdf, 0, 0, card_data, logo)
    pdf.showPage()
    draw_membership_card_back(pdf, 0, 0, card_data, logo)
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output
