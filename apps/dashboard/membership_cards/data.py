"""
Data adapter for ASCAI membership card PDFs.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse

from django.conf import settings as django_settings
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
    association: str = "ASCAI Lazio"
    community: str = "General Community"
    legalName: str = "Association of Cameroonian Students and Academics in Lazio"
    address: str = "Rome and the Lazio region, Italy"
    email: str = "info@ascai.org"
    phone: str = ""
    website: str = "ascai.org"
    social: str = "ascai.org"
    verificationEmail: str = "info@ascai.org"


def _social_handle_from_url(url: str) -> str:
    if not url:
        return "ascai.org"
    parsed = urlparse(url.strip())
    path = parsed.path.strip("/")
    host = (parsed.netloc or "").lower()
    if "instagram.com" in host and path:
        return f"@{path.split('/')[0]}"
    if "facebook.com" in host and path:
        return f"facebook.com/{path.split('/')[0]}"
    if "linkedin.com" in host and path:
        return f"linkedin.com/{path.split('/')[0]}"
    if "tiktok.com" in host and path:
        handle = path.split("/")[0]
        return f"@{handle}" if not handle.startswith("@") else handle
    if "youtube.com" in host or "youtu.be" in host:
        return url.replace("https://", "").replace("http://", "").rstrip("/")
    return url.replace("https://", "").replace("http://", "").rstrip("/")


def _association_contact_defaults() -> dict[str, str]:
    """Load public contact details from site settings (ascai.org source of truth)."""
    email = getattr(django_settings, "CONTACT_EMAIL", "info@ascai.org") or "info@ascai.org"
    location = "Rome and the Lazio region, Italy"
    legal_name = "Association of Cameroonian Students and Academics in Lazio"
    association = "ASCAI Lazio"
    social = "ascai.org"

    try:
        from apps.core.models import AssociationSettings

        assoc = AssociationSettings.load()
        if assoc.public_email:
            email = assoc.public_email
        if assoc.public_location:
            location = assoc.public_location
        if assoc.tagline:
            legal_name = assoc.tagline
        if assoc.site_name:
            association = assoc.site_name
        for social_url in (
            assoc.instagram_url,
            assoc.facebook_url,
            assoc.linkedin_url,
            assoc.tiktok_url,
            assoc.youtube_url,
        ):
            if social_url:
                social = _social_handle_from_url(social_url)
                break
    except Exception:
        pass

    return {
        "association": association,
        "legalName": legal_name,
        "address": location,
        "email": email,
        "phone": "",
        "website": "ascai.org",
        "social": social,
        "verificationEmail": email,
    }


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
    contact = _association_contact_defaults()

    qr_payload = {
        "association": "ASCAI",
        "member_id": member_id,
        "name": full_name,
        "status": status,
        "website": "https://ascai.org",
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
        **contact,
    )
