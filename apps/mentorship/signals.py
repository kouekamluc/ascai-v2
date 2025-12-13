"""
Signals for mentorship app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
import logging

from .models import MentorshipRequest, MentorshipMessage

logger = logging.getLogger(__name__)


def get_site_url():
    """Get the site URL for email links."""
    try:
        site = Site.objects.get_current()
        site_domain = site.domain
        if site_domain == 'ascai.org' or site_domain == 'ascailazio.org':
            site_domain = 'ascai.up.railway.app'
        site_url = f"https://{site_domain}" if not site_domain.startswith('http') else site_domain
    except Exception:
        site_url = getattr(settings, 'SITE_URL', 'https://ascai.up.railway.app')
    return site_url


@receiver(post_save, sender=MentorshipRequest)
def notify_mentorship_request(sender, instance, created, **kwargs):
    """Send email notification when mentorship request is created or status changes."""
    if created:
        # New request - notify mentor
        try:
            if not instance.mentor:
                return  # Skip if mentor doesn't exist
            site_url = get_site_url()
            mentor = instance.mentor.user
            student = instance.student
            
            subject = _('New Mentorship Request')
            message = _(
                'You have received a new mentorship request from {student_name}.\n\n'
                'Subject: {subject}\n\n'
                'Message: {message}\n\n'
                'View and respond to the request:\n'
                'Dashboard: {dashboard_url}\n'
                'Direct: {direct_url}'
            ).format(
                student_name=student.get_full_name() or student.username,
                subject=instance.subject,
                message=instance.message,
                dashboard_url=f"{site_url}/dashboard/mentorship/requests/{instance.pk}/",
                direct_url=f"{site_url}/mentorship/requests/{instance.pk}/"
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[mentor.email],
                fail_silently=True,
            )
            logger.info(f"Sent mentorship request notification to {mentor.email}")
        except Exception as e:
            logger.error(f"Failed to send mentorship request notification: {e}")
    else:
        # Status changed - notify student
        try:
            if not instance.mentor:
                return  # Skip if mentor doesn't exist
            site_url = get_site_url()
            mentor = instance.mentor.user
            student = instance.student
            
            if instance.status == 'accepted':
                subject = _('Mentorship Request Accepted')
                message = _(
                    'Great news! {mentor_name} has accepted your mentorship request.\n\n'
                    'Subject: {subject}\n\n'
                    'You can now start messaging:\n'
                    'Dashboard: {dashboard_url}\n'
                    'Direct: {direct_url}'
                ).format(
                    mentor_name=mentor.get_full_name() or mentor.username,
                    subject=instance.subject,
                    dashboard_url=f"{site_url}/dashboard/mentorship/requests/{instance.pk}/",
                    direct_url=f"{site_url}/mentorship/requests/{instance.pk}/"
                )
            elif instance.status == 'rejected':
                subject = _('Mentorship Request Update')
                message = _(
                    '{mentor_name} has declined your mentorship request.\n\n'
                    'Subject: {subject}\n\n'
                    'You can find other mentors:\n'
                    'Dashboard: {dashboard_url}\n'
                    'Direct: {direct_url}'
                ).format(
                    mentor_name=mentor.get_full_name() or mentor.username,
                    subject=instance.subject,
                    dashboard_url=f"{site_url}/dashboard/mentorship/browse/",
                    direct_url=f"{site_url}/mentorship/"
                )
            elif instance.status == 'completed':
                subject = _('Mentorship Completed')
                message = _(
                    'Your mentorship with {mentor_name} has been marked as completed.\n\n'
                    'Subject: {subject}\n\n'
                    'Please rate your mentor:\n'
                    'Dashboard: {dashboard_url}\n'
                    'Direct: {direct_url}'
                ).format(
                    mentor_name=mentor.get_full_name() or mentor.username,
                    subject=instance.subject,
                    dashboard_url=f"{site_url}/dashboard/mentorship/requests/{instance.pk}/",
                    direct_url=f"{site_url}/mentorship/requests/{instance.pk}/rate/"
                )
            else:
                return  # Don't send email for other status changes
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )
            logger.info(f"Sent mentorship status notification to {student.email}")
        except Exception as e:
            logger.error(f"Failed to send mentorship status notification: {e}")


@receiver(post_save, sender=MentorshipMessage)
def notify_new_message(sender, instance, created, **kwargs):
    """Send email notification when a new message is sent."""
    if created:
        try:
            site_url = get_site_url()
            request = instance.request
            
            # Determine recipient (the other person in the conversation)
            if not request.mentor:
                return  # Skip if mentor doesn't exist
            if instance.sender == request.student:
                recipient = request.mentor.user
                sender_name = request.student.get_full_name() or request.student.username
            else:
                recipient = request.student
                sender_name = request.mentor.user.get_full_name() or request.mentor.user.username
            
            subject = _('New Message in Mentorship Request')
            message = _(
                'You have received a new message from {sender_name}.\n\n'
                'Request: {subject}\n\n'
                'Message: {content}\n\n'
                'Reply:\n'
                'Dashboard: {dashboard_url}\n'
                'Direct: {direct_url}'
            ).format(
                sender_name=sender_name,
                subject=request.subject,
                content=instance.content[:200],  # Truncate long messages
                dashboard_url=f"{site_url}/dashboard/mentorship/requests/{request.pk}/",
                direct_url=f"{site_url}/mentorship/requests/{request.pk}/"
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True,
            )
            logger.info(f"Sent new message notification to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send new message notification: {e}")

