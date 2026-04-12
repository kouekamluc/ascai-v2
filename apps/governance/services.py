"""
Shared governance business rules and role resolution helpers.
"""
from datetime import date, timedelta

from django.utils import timezone

from .models import (
    AuditorMember,
    CommissionMember,
    ExecutiveBoard,
    ExecutivePosition,
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

        if float(dues.amount) == 10.0:
            valid_from = date(dues.year, 1, 1)
            valid_until = date(dues.year, 12, 31)
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
