"""
Shared governance business rules and role resolution helpers.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import (
    AuditorMember,
    CommissionMember,
    ExecutiveBoard,
    ExecutivePosition,
    Member,
    MembershipDues,
    MembershipStatus,
)


def get_active_board():
    today = timezone.now().date()
    return (
        ExecutiveBoard.objects.filter(
            status="active",
            term_start_date__lte=today,
            term_end_date__gte=today,
        )
        .order_by("-term_start_date")
        .first()
    )


def get_user_governance_roles(user):
    roles = set()
    if not user.is_authenticated:
        return roles

    if user.is_superuser or user.is_staff:
        roles.add("staff")

    current_board = get_active_board()
    if current_board:
        roles.update(
            current_board.positions.filter(user=user, status="active").values_list(
                "position", flat=True
            )
        )

    if CommissionMember.objects.filter(
        user=user, commission__status="active"
    ).exists():
        roles.add("electoral_commission")

    if AuditorMember.objects.filter(user=user, board__status="active").exists():
        roles.add("board_of_auditors")

    return roles


def user_has_governance_access(user, permission_codename):
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.has_perm(permission_codename):
        return True

    roles = get_user_governance_roles(user)
    role_map = {
        "governance.manage_executive_board": {
            "staff",
            "president",
            "vice_president",
            "secretary_general",
        },
        "governance.manage_assembly": {
            "staff",
            "president",
            "vice_president",
            "secretary_general",
        },
        "governance.manage_finances": {
            "staff",
            "president",
            "treasurer",
            "statutory_auditor",
            "board_of_auditors",
        },
        "governance.approve_expense": {
            "staff",
            "president",
            "treasurer",
            "statutory_auditor",
        },
        "governance.manage_elections": {
            "staff",
            "president",
            "vice_president",
            "secretary_general",
            "electoral_commission",
        },
        "governance.apply_sanctions": {
            "staff",
            "president",
            "vice_president",
            "secretary_general",
        },
    }
    return bool(roles & role_map.get(permission_codename, set()))


def can_publish_communication(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.has_perm("governance.manage_communications"):
        return True

    roles = get_user_governance_roles(user)
    return bool(
        roles
        & {"staff", "president", "vice_president", "communication_culture_manager"}
    )


def get_membership_validity_window(year):
    """Membership runs from January 1 to December 31 of the dues year."""
    return date(year, 1, 1), date(year, 12, 31)


def get_membership_due_date(year):
    """Annual dues are due on March 31."""
    return date(year, 3, 31)


def get_expected_dues_amount(member):
    """Standard annual dues amount based on member type."""
    if member.member_type == "sympathizer":
        return Decimal("5.00")
    return Decimal("10.00")


def ensure_current_year_dues(member, year=None):
    """Create the current year's dues record if it doesn't exist yet."""
    target_year = year or timezone.now().year
    dues, _created = MembershipDues.objects.get_or_create(
        member=member,
        year=target_year,
        defaults={
            "amount": get_expected_dues_amount(member),
            "due_date": get_membership_due_date(target_year),
            "status": "pending",
        },
    )
    return dues


def get_member_resource_access(user):
    """
    Resolve whether a user can access dues-gated association resources.
    """
    access = {
        "is_authenticated": bool(getattr(user, "is_authenticated", False)),
        "has_member_profile": False,
        "is_paid_member": False,
        "status": "login_required",
        "member": None,
        "current_dues": None,
        "active_due": None,
        "reason": _(
            "Create an account, register with ASCAI, and pay your dues to unlock "
            "member-only association resources."
        ),
        "cta_url": reverse("account_signup"),
        "cta_label": _("Create account"),
    }

    if not access["is_authenticated"]:
        return access

    try:
        member = user.member_profile
    except Member.DoesNotExist:
        access.update(
            status="registration_required",
            reason=_(
                "Register as a member or sympathizer first, then complete your dues "
                "payment to unlock member resources."
            ),
            cta_url=reverse("governance:member_register"),
            cta_label=_("Register membership"),
        )
        return access

    today = timezone.now().date()
    current_year = today.year
    current_dues = member.dues.filter(year=current_year).first()
    active_due = (
        member.dues.filter(status="paid")
        .filter(
            Q(valid_from__lte=today, valid_until__gte=today)
            | Q(valid_from__isnull=True, valid_until__isnull=True, year=current_year)
        )
        .order_by("-year", "-payment_date", "-updated_at")
        .first()
    )

    access.update(
        has_member_profile=True,
        member=member,
        current_dues=current_dues,
        active_due=active_due,
        status="dues_required",
        cta_url=reverse("governance:my_dues"),
        cta_label=_("Pay my dues"),
    )

    if active_due:
        access.update(
            is_paid_member=True,
            status="granted",
            reason=_("Your dues are up to date. Member-only resources are unlocked."),
            cta_url=reverse("downloads:index"),
            cta_label=_("Browse resources"),
        )
        return access

    if current_dues and current_dues.status != "paid":
        access["reason"] = _(
            "Your %(year)s dues are not marked as paid yet. Complete payment to "
            "unlock ASCAI's member-only resources."
        ) % {"year": current_year}
    else:
        access["reason"] = _(
            "Pay your current dues to unlock ASCAI's member-only resources, practical "
            "toolkits, and premium association materials."
        )

    return access


def user_can_access_member_resources(user):
    """
    Boolean helper for dues-gated resource access.
    """
    return get_member_resource_access(user)["is_paid_member"]


def sync_membership_state_from_dues(dues):
    """
    Centralizes dues-driven membership activation and expiry logic.
    """
    member = dues.member
    today = timezone.now().date()

    if dues.status == "paid" and dues.payment_date:
        latest_status = member.status_history.first()
        if latest_status:
            latest_status.last_payment_date = dues.payment_date
            latest_status.save(update_fields=["last_payment_date"])

        valid_from, valid_until = get_membership_validity_window(dues.year)
        updates = []
        if dues.valid_from != valid_from:
            dues.valid_from = valid_from
            updates.append("valid_from")
        if dues.valid_until != valid_until:
            dues.valid_until = valid_until
            updates.append("valid_until")
        if updates:
            dues.save(update_fields=updates)

        member.membership_start_date = valid_from
        member.membership_end_date = valid_until

        member.is_active_member = True
        member.save(
            update_fields=["is_active_member", "membership_start_date", "membership_end_date"]
        )
        MembershipStatus.objects.create(
            member=member,
            status="active",
            effective_date=dues.payment_date,
            last_payment_date=dues.payment_date,
            reason=f"Dues paid for {dues.year}",
        )
        return

    if dues.valid_until and today > dues.valid_until and member.is_active_member:
        member.is_active_member = False
        member.save(update_fields=["is_active_member"])
        MembershipStatus.objects.create(
            member=member,
            status="inactive",
            effective_date=dues.valid_until,
            reason=f"Membership validity expired on {dues.valid_until}",
        )
        return

    if dues.status != "paid" and dues.due_date:
        expiry_date = dues.due_date + timedelta(days=90)
        if today > expiry_date and member.is_active_member:
            member.is_active_member = False
            member.save(update_fields=["is_active_member"])
            MembershipStatus.objects.create(
                member=member,
                status="inactive",
                effective_date=expiry_date,
                reason="Non-payment of annual dues (3 months after due date)",
            )
