"""
Signals for dashboard workflows.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BureauMessage
from .services import send_bureau_message_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BureauMessage)
def send_bureau_message_email(sender, instance, created, **kwargs):
    """Send a notification whenever a new bureau message is created."""
    if not created:
        return

    try:
        send_bureau_message_notification(instance)
    except Exception:
        logger.exception(
            "Bureau message email notification failed for message_id=%s",
            instance.pk,
        )
