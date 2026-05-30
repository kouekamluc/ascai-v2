"""
Service helpers for dashboard workflows.
"""
import logging

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.email_utils import get_site_url, send_branded_email

logger = logging.getLogger(__name__)


def send_bureau_message_notification(message, request=None):
    """Send and audit the email notification for a bureau direct message."""
    if not message.recipient.email:
        message.email_delivery_status = 'skipped'
        message.email_delivery_error = _('Recipient has no email address.')
        message.save(update_fields=['email_delivery_status', 'email_delivery_error', 'updated_at'])
        return 0

    site_url = get_site_url(request=request)
    message_url = f"{site_url}{reverse('dashboard:message_detail', kwargs={'pk': message.pk})}"
    sender_name = message.sender.get_display_name() if message.sender else _('ASCAI Lazio Bureau')
    text_body = _(
        'Hello {name},\n\n'
        'You have received a new message from the ASCAI Lazio bureau.\n\n'
        'Subject: {subject}\n\n'
        '{body}\n\n'
        'Open it here: {url}\n\n'
        'ASCAI Lazio'
    ).format(
        name=message.recipient.get_display_name(),
        subject=message.subject,
        body=message.body,
        url=message_url,
    )

    try:
        sent_count = send_branded_email(
            subject=_('New message from ASCAI Lazio bureau: {}').format(message.subject),
            text_body=text_body,
            template_name='email/generic_message.html',
            context={
                'email_title': _('New message from ASCAI Lazio bureau'),
                'greeting': _('Hello {}').format(message.recipient.get_display_name()),
                'body_paragraphs': [
                    _('You have received a new direct message from the ASCAI Lazio bureau.'),
                    _('You can read it and reply from your dashboard.'),
                ],
                'detail_rows': [
                    {'label': _('Subject'), 'value': message.subject},
                    {'label': _('From'), 'value': sender_name},
                ],
                'message_body': message.body,
                'button_url': message_url,
                'button_label': _('Open message'),
                'closing_paragraphs': [_('Thank you, ASCAI Lazio')],
            },
            recipient_list=[message.recipient.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
            request=request,
            site_url=site_url,
        )
    except Exception as exc:
        error = str(exc)
        logger.exception(
            "Failed to send bureau message notification for message_id=%s to %s",
            message.pk,
            message.recipient.email,
        )
        message.email_delivery_status = 'failed'
        message.email_delivery_error = error[:2000]
        message.save(update_fields=['email_delivery_status', 'email_delivery_error', 'updated_at'])
        raise

    if sent_count < 1:
        error = _('Email backend returned 0 sent messages.')
        logger.error(
            "Bureau message notification was not accepted by email backend: message_id=%s recipient=%s",
            message.pk,
            message.recipient.email,
        )
        message.email_delivery_status = 'failed'
        message.email_delivery_error = error
        message.save(update_fields=['email_delivery_status', 'email_delivery_error', 'updated_at'])
        return 0

    message.email_sent_at = timezone.now()
    message.email_delivery_status = 'sent'
    message.email_delivery_error = ''
    message.save(update_fields=['email_sent_at', 'email_delivery_status', 'email_delivery_error', 'updated_at'])
    return sent_count
