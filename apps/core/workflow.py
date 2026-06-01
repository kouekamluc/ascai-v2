"""
User workflow state helpers shared by dashboard and navigation surfaces.
"""
from dataclasses import dataclass

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


@dataclass(frozen=True)
class UserWorkflowState:
    is_authenticated: bool = False
    is_approved: bool = False
    is_student: bool = False
    is_mentor: bool = False
    has_mentor_profile: bool = False
    mentor_profile_approved: bool = False
    mentor_profile_pending: bool = False
    has_member_profile: bool = False
    member_active: bool = False
    dues_due: bool = False
    dues_paid: bool = False
    is_governance_staff: bool = False
    needs_profile_completion: bool = False
    needs_membership_registration: bool = False
    unread_bureau_messages: int = 0


def get_user_workflow_state(user):
    """
    Resolve the user's product state for role-aware workflow decisions.
    """
    if not getattr(user, "is_authenticated", False):
        return UserWorkflowState()

    is_superuser = getattr(user, "is_superuser", False)
    is_staff = getattr(user, "is_staff", False)
    is_approved = bool(getattr(user, "is_approved", False) or is_superuser)
    is_student = bool(getattr(user, "is_student", False))
    is_mentor = bool(getattr(user, "is_mentor", False))

    has_mentor_profile = False
    mentor_profile_approved = False
    if is_mentor:
        try:
            mentor_profile = user.mentor_profile
            has_mentor_profile = True
            mentor_profile_approved = bool(mentor_profile.is_approved)
        except ObjectDoesNotExist:
            pass

    has_member_profile = False
    member_active = False
    dues_due = False
    dues_paid = False
    try:
        member = user.member_profile
        if getattr(user, "email_verified", False):
            has_member_profile = True
            member_active = bool(member.is_active_member)
            today = timezone.now().date()
            current_dues = member.dues.filter(year=today.year).order_by("-due_date").first()
            if current_dues:
                dues_paid = current_dues.status == "paid"
                dues_due = current_dues.status != "paid"
    except ObjectDoesNotExist:
        pass

    unread_bureau_messages = 0
    try:
        from apps.dashboard.models import BureauMessage
        unread_bureau_messages = BureauMessage.objects.filter(
            recipient=user,
            is_read=False,
        ).count()
    except Exception:
        unread_bureau_messages = 0

    has_governance_permission = False
    try:
        has_governance_permission = any(
            user.has_perm(permission)
            for permission in (
                "governance.view_member",
                "governance.manage_executive_board",
                "governance.manage_assembly",
                "governance.manage_elections",
                "governance.manage_finances",
            )
        )
    except Exception:
        has_governance_permission = False

    return UserWorkflowState(
        is_authenticated=True,
        is_approved=is_approved,
        is_student=is_student,
        is_mentor=is_mentor,
        has_mentor_profile=has_mentor_profile,
        mentor_profile_approved=mentor_profile_approved,
        mentor_profile_pending=has_mentor_profile and not mentor_profile_approved,
        has_member_profile=has_member_profile,
        member_active=member_active,
        dues_due=dues_due,
        dues_paid=dues_paid,
        is_governance_staff=bool(is_staff or is_superuser or has_governance_permission),
        needs_profile_completion=not bool(getattr(user, "full_name", "")),
        needs_membership_registration=is_approved and getattr(user, "email_verified", False) and not has_member_profile,
        unread_bureau_messages=unread_bureau_messages,
    )


def workflow_state(request):
    """Template context processor for role-aware navigation."""
    return {"workflow": get_user_workflow_state(request.user)}
