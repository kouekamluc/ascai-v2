"""
Shared mentorship workflow services.
"""
from dataclasses import dataclass

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import MentorProfile, MentorshipMessage, MentorshipRequest


@dataclass
class MentorshipStateResult:
    request: MentorshipRequest
    changed: bool = True


def get_request_queryset_for_user(user):
    return MentorshipRequest.objects.filter(
        Q(student=user) | Q(mentor__user=user)
    ).select_related("mentor", "mentor__user", "student")


def get_requests_for_mentor(user):
    return MentorshipRequest.objects.filter(mentor__user=user).select_related(
        "mentor", "mentor__user", "student"
    )


def get_requests_for_student(user):
    return MentorshipRequest.objects.filter(student=user).select_related(
        "mentor", "mentor__user", "student"
    )


def create_request(*, student, mentor, subject, message):
    if not getattr(student, "is_student", False):
        raise PermissionDenied(_("Only students can create mentorship requests."))

    if mentor.user_id == student.id:
        raise ValidationError(_("You cannot request mentorship from yourself."))

    existing_request = MentorshipRequest.objects.filter(
        student=student,
        mentor=mentor,
        status__in=["pending", "accepted"],
    ).first()
    if existing_request:
        raise ValidationError(_("You already have an active request with this mentor."))

    return MentorshipRequest.objects.create(
        student=student,
        mentor=mentor,
        subject=subject,
        message=message,
    )


def send_message(*, mentorship_request, sender, content):
    if mentorship_request.status != "accepted":
        raise ValidationError(_("Request must be accepted to send messages."))

    if mentorship_request.student != sender and mentorship_request.mentor.user != sender:
        raise PermissionDenied(_("Access denied."))

    return MentorshipMessage.objects.create(
        request=mentorship_request,
        sender=sender,
        content=content,
    )


def accept_request(*, mentorship_request, actor):
    if mentorship_request.mentor.user != actor:
        raise PermissionDenied(_("You do not have permission to accept this request."))
    if mentorship_request.status != "pending":
        raise ValidationError(_("Only pending requests can be accepted."))

    mentorship_request.status = "accepted"
    mentorship_request.responded_at = timezone.now()
    mentorship_request.save(update_fields=["status", "responded_at"])
    return MentorshipStateResult(request=mentorship_request)


def reject_request(*, mentorship_request, actor):
    if mentorship_request.mentor.user != actor:
        raise PermissionDenied(_("You do not have permission to reject this request."))
    if mentorship_request.status != "pending":
        raise ValidationError(_("Only pending requests can be rejected."))

    mentorship_request.status = "rejected"
    mentorship_request.responded_at = timezone.now()
    mentorship_request.save(update_fields=["status", "responded_at"])
    return MentorshipStateResult(request=mentorship_request)


def complete_request(*, mentorship_request, actor):
    if mentorship_request.student != actor and mentorship_request.mentor.user != actor:
        raise PermissionDenied(_("Access denied."))
    if not mentorship_request.can_be_completed():
        raise ValidationError(_("Only accepted requests can be completed."))

    mentorship_request.status = "completed"
    mentorship_request.responded_at = timezone.now()
    mentorship_request.save(update_fields=["status", "responded_at"])

    if mentorship_request.mentor.user == actor:
        mentorship_request.mentor.increment_students_helped()
    mentorship_request.mentor.calculate_success_rate()

    return MentorshipStateResult(request=mentorship_request)


def update_availability(*, mentor_profile, actor, new_status):
    if mentor_profile.user != actor:
        raise PermissionDenied(_("Access denied."))
    if new_status not in dict(MentorProfile.AVAILABILITY_CHOICES):
        raise ValidationError(_("Invalid availability status."))

    mentor_profile.availability_status = new_status
    mentor_profile.save(update_fields=["availability_status"])
    return mentor_profile
