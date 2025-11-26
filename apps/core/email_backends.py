"""
Custom email backend using SendGrid API instead of SMTP.
This bypasses Railway's SMTP blocking issues.
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid library not installed. Install with: pip install sendgrid")


class SendGridBackend(BaseEmailBackend):
    """
    SendGrid API email backend to bypass SMTP blocking.
    Uses SendGrid's HTTP API instead of SMTP.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError('SENDGRID_API_KEY setting is required')
        if not SENDGRID_AVAILABLE:
            if not self.fail_silently:
                raise ImportError('sendgrid library is required. Install with: pip install sendgrid')
    
    def send_messages(self, email_messages):
        """
        Send messages using SendGrid API.
        """
        if not email_messages:
            return 0
        
        if not self.api_key or not SENDGRID_AVAILABLE:
            logger.error("SendGrid API key not configured or library not available")
            return 0
        
        sg = SendGridAPIClient(self.api_key)
        sent_count = 0
        
        for message in email_messages:
            try:
                # Determine content type
                is_html = message.content_subtype == 'html'
                
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                )
                
                # Set content based on type
                if is_html:
                    mail.html_content = message.body
                else:
                    mail.plain_text_content = message.body
                
                # Add CC and BCC if present
                if message.cc:
                    for cc_email in message.cc:
                        mail.add_cc(cc_email)
                if message.bcc:
                    for bcc_email in message.bcc:
                        mail.add_bcc(bcc_email)
                
                # Add reply-to if present
                if message.reply_to:
                    mail.reply_to = message.reply_to[0]
                
                # Send via API
                response = sg.send(mail)
                
                if response.status_code in [200, 202]:
                    sent_count += 1
                    logger.info(f"Email sent successfully via SendGrid API to {message.to}")
                else:
                    logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
                    if not self.fail_silently:
                        raise Exception(f"SendGrid API error: {response.status_code} - {response.body}")
                        
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid API: {str(e)}", exc_info=True)
                if not self.fail_silently:
                    raise
        
        return sent_count

