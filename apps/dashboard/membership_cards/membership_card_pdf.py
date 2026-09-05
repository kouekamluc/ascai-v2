"""
Portable membership card PDF generation for ASCAI.
"""
from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path


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


class MembershipCardPDFError(RuntimeError):
    """Raised when the card PDF engines are unavailable or fail."""


def membership_card_filename(card_data: MemberCardData, *, print_ready: bool = False) -> str:
    suffix = "-print" if print_ready else ""
    return f"ascai-membership-card-{card_data.memberId}{suffix}.pdf"


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


def _generate_pdf(dues, request, *, print_ready=False) -> BytesIO:
    """Use one portable renderer so preview and downloads do not vary by server."""
    try:
        from . import pdf_reportlab

        renderer = (
            pdf_reportlab.generate_membership_card_print_pdf
            if print_ready else pdf_reportlab.generate_membership_card_pdf
        )
        return renderer(dues, request)
    except Exception as exc:
        logger.exception("Membership card PDF generation failed.")
        raise MembershipCardPDFError("Membership card PDF generation failed.") from exc


def generate_membership_card_pdf(dues, request=None) -> BytesIO:
    """Generate a compact digital PDF showing both sides at actual card size."""
    return _generate_pdf(dues, request)


def generate_membership_card_print_pdf(dues, request=None) -> BytesIO:
    """Generate two pages at exactly 85.6mm x 54mm for future card printing."""
    return _generate_pdf(dues, request, print_ready=True)
