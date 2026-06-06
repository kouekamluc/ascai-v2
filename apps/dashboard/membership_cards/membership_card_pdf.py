"""
WeasyPrint HTML/CSS membership card PDF generation for ASCAI.
"""
from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string

from .assets import (
    make_logo_data_uri,
    make_photo_data_uri,
    make_qr_data_uri,
    resolve_css_path,
    resolve_logo_static_url,
    resolve_watermark_data_uri,
)
from .data import MemberCardData, build_member_card_data

logger = logging.getLogger(__name__)


def membership_card_filename(card_data: MemberCardData) -> str:
    return f"ascai-membership-card-{card_data.memberId}.pdf"


def build_card_context(dues, request=None) -> dict:
    card = build_member_card_data(dues, request)
    css_path = resolve_css_path()
    logo_data_uri = make_logo_data_uri()
    return {
        "card": card,
        "logo_url": logo_data_uri,
        "logo_static_url": resolve_logo_static_url(),
        "photo_url": make_photo_data_uri(card.photoField, card.fullName),
        "qr_url": make_qr_data_uri(card.qrCodeData),
        "watermark_url": resolve_watermark_data_uri(),
        "css_path": Path(css_path).resolve().as_uri(),
    }


def _weasyprint_base_url(request) -> str:
    if request is not None:
        return request.build_absolute_uri("/")
    return settings.BASE_DIR.as_uri() + "/"


def _render_pdf(html_string: str, request) -> bytes:
    try:
        from weasyprint import CSS, HTML
    except (ImportError, OSError) as exc:
        raise RuntimeError(f"WeasyPrint unavailable: {exc}") from exc

    css_path = resolve_css_path()
    return HTML(
        string=html_string,
        base_url=_weasyprint_base_url(request),
    ).write_pdf(stylesheets=[CSS(filename=css_path)])


def generate_membership_card_pdf(dues, request=None) -> BytesIO:
    """Generate an A4 landscape preview PDF with front/back side-by-side."""
    context = build_card_context(dues, request)
    html_string = render_to_string("members/cards/membership_card_pdf.html", context)
    try:
        pdf_bytes = _render_pdf(html_string, request)
    except Exception as exc:
        logger.warning("WeasyPrint failed, falling back to ReportLab: %s", exc)
        from .pdf_reportlab import generate_membership_card_pdf as reportlab_generate

        return reportlab_generate(dues, request)

    output = BytesIO(pdf_bytes)
    output.seek(0)
    return output


def generate_membership_card_print_pdf(dues, request=None) -> BytesIO:
    """Generate print-ready card pages at exact 85.6mm × 54mm."""
    context = build_card_context(dues, request)
    html_string = render_to_string("members/cards/membership_card_print.html", context)
    try:
        pdf_bytes = _render_pdf(html_string, request)
    except Exception as exc:
        logger.warning("WeasyPrint print PDF failed, falling back to ReportLab: %s", exc)
        from .pdf_reportlab import generate_membership_card_print_pdf as reportlab_generate

        return reportlab_generate(dues, request)

    output = BytesIO(pdf_bytes)
    output.seek(0)
    return output
