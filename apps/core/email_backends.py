"""
Custom email backend using SendGrid API instead of SMTP.
This bypasses Railway's SMTP blocking issues.
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging
import re

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
            logger.error('SENDGRID_API_KEY setting is required for SendGrid API backend')
            if not self.fail_silently:
                raise ValueError('SENDGRID_API_KEY setting is required')
        elif not SENDGRID_AVAILABLE:
            logger.error('sendgrid library is required. Install with: pip install sendgrid')
            if not self.fail_silently:
                raise ImportError('sendgrid library is required. Install with: pip install sendgrid')
        else:
            logger.info('SendGrid API backend initialized successfully (bypasses SMTP blocking)')
    
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
                # Extract email from "Name <email>" format if present
                from_email = message.from_email
                if '<' in from_email and '>' in from_email:
                    # Extract email from "Name <email@example.com>" format
                    from_email = from_email.split('<')[1].split('>')[0].strip()
                
                # Ensure to_emails is a list (Django's message.to can be string or list)
                to_emails = message.to
                if isinstance(to_emails, str):
                    to_emails = [to_emails]
                elif not isinstance(to_emails, (list, tuple)):
                    to_emails = list(to_emails)
                
                # Determine content type
                is_html = message.content_subtype == 'html'
                
                # SendGrid requires at least one content type (html or plain text)
                # Ensure body is not empty
                body = message.body or '(No content)'
                
                if is_html:
                    html_content = body
                    # For HTML emails, also provide plain text fallback
                    plain_text_content = body.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
                    # Remove HTML tags for plain text version (simple approach)
                    plain_text_content = re.sub(r'<[^>]+>', '', plain_text_content).strip()
                    if not plain_text_content:
                        plain_text_content = 'Please view this email in an HTML-compatible email client.'
                else:
                    html_content = None
                    plain_text_content = body
                
                # Create Mail object - SendGrid requires at least one content type
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_emails,
                    subject=message.subject or '(No Subject)',
                )
                
                # Set content (SendGrid requires at least one)
                if html_content:
                    mail.html_content = html_content
                if plain_text_content:
                    mail.plain_text_content = plain_text_content
                
                # Add CC if present
                if message.cc:
                    cc_list = message.cc if isinstance(message.cc, (list, tuple)) else [message.cc]
                    for cc_email in cc_list:
                        mail.add_cc(cc_email)
                
                # Add BCC if present
                if message.bcc:
                    bcc_list = message.bcc if isinstance(message.bcc, (list, tuple)) else [message.bcc]
                    for bcc_email in bcc_list:
                        mail.add_bcc(bcc_email)
                
                # Add reply-to if present
                if message.reply_to:
                    reply_to = message.reply_to[0] if isinstance(message.reply_to, (list, tuple)) else message.reply_to
                    # Extract email if in "Name <email>" format
                    if '<' in reply_to and '>' in reply_to:
                        reply_to = reply_to.split('<')[1].split('>')[0].strip()
                    mail.reply_to = reply_to
                
                # Send via API
                response = sg.send(mail)
                
                if response.status_code in [200, 202]:
                    sent_count += 1
                    logger.info(f"Email sent successfully via SendGrid API to {to_emails}")
                else:
                    # Log detailed error response
                    error_body = ""
                    try:
                        error_body = response.body.decode('utf-8') if response.body else "No error body"
                    except:
                        error_body = str(response.body)
                    
                    logger.error(f"SendGrid API error: {response.status_code} - {error_body}")
                    logger.error(f"Email details - From: {from_email}, To: {to_emails}, Subject: {message.subject}")
                    if not self.fail_silently:
                        raise Exception(f"SendGrid API error: {response.status_code} - {error_body}")
                        
            except Exception as e:
                # Try to extract more details from SendGrid exceptions
                error_details = str(e)
                error_type = type(e).__name__
                
                # Log comprehensive error information
                logger.error("=" * 60)
                logger.error("SENDGRID API ERROR DETAILS")
                logger.error("=" * 60)
                logger.error(f"Error Type: {error_type}")
                logger.error(f"Error Message: {error_details}")
                logger.error(f"From Email: {message.from_email}")
                logger.error(f"To Emails: {message.to}")
                logger.error(f"Subject: {message.subject}")
                logger.error(f"Content Type: {message.content_subtype}")
                logger.error(f"Body Length: {len(message.body) if message.body else 0} characters")
                
                # Try to extract SendGrid error response if available
                if hasattr(e, 'body') and e.body:
                    try:
                        if isinstance(e.body, bytes):
                            error_body = e.body.decode('utf-8')
                        else:
                            error_body = str(e.body)
                        logger.error(f"SendGrid Error Response: {error_body}")
                    except:
                        logger.error(f"SendGrid Error Response (raw): {e.body}")
                
                # Check for common issues
                if '400' in error_details or 'Bad Request' in error_details:
                    logger.error("=" * 60)
                    logger.error("LIKELY CAUSE: Sender email not verified in SendGrid!")
                    logger.error("ACTION REQUIRED:")
                    logger.error("1. Go to SendGrid Dashboard → Settings → Sender Authentication")
                    logger.error("2. Click 'Verify a Single Sender'")
                    logger.error("3. Verify the email address in DEFAULT_FROM_EMAIL")
                    logger.error(f"4. Current FROM email: {message.from_email}")
                    logger.error("=" * 60)
                
                if not self.fail_silently:
                    raise
        
        return sent_count

