"""
Data adapter for ASCAI membership card PDFs.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from django.utils import timezone


@dataclass(frozen=True)
class MemberCardData:
    fullName: str
    memberId: str
    role: str
    nationality: str
    issuedDate: str
    expiryDate: str
    photoField: object
    qrCodeData: str
    status: str
    association: str = "ASCAI"
    community: str = "General Community"
    legalName: str = "Associazione Studenti Camerunesi del Lazio"
    address: str = "Via dei Laterani, 10 - 00184 Roma, Italia"
    email: str = "info@ascai.it"
    phone: str = "+39 351 123 4567"
    website: str = "www.ascai.it"
    social: str = "@ascai.lazio"
    verificationEmail: str = "verify@ascai.it"


def _month_year(value: date | None, fallback: date) -> str:
    return (value or fallback).strftime("%m/%Y")


def build_member_card_data(dues, request=None) -> MemberCardData:
    member = dues.member
    user = member.user
    full_name = user.get_display_name()
    member_id = f"ASC-{dues.year}-{member.pk:03d}"
    issued = dues.payment_date or timezone.now().date()
    expiry = dues.valid_until or dues.due_date.replace(month=12, day=31)
    status = "active"
    role = "Member" if member.member_type != "sympathizer" else "Sympathizer"

    qr_payload = {
        "association": "ASCAI",
        "member_id": member_id,
        "name": full_name,
        "status": status,
    }
    qr_data = json.dumps(qr_payload, separators=(",", ":"))

    return MemberCardData(
        fullName=full_name,
        memberId=member_id,
        role=role,
        nationality="Cameroonian",
        issuedDate=_month_year(issued, timezone.now().date()),
        expiryDate=_month_year(expiry, expiry),
        photoField=getattr(user, "avatar", None),
        qrCodeData=qr_data,
        status=status,
    )
