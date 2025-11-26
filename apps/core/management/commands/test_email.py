"""
Management command to test email configuration by sending a test email.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
import sys
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send a test email to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='Test Email from ASCAI Lazio',
            help='Subject line for the test email (default: "Test Email from ASCAI Lazio")',
        )

    def handle(self, *args, **options):
        recipient = options['email']
        subject = options['subject']
        
        # Display current email configuration
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Email Configuration Test'))
        self.stdout.write('='*60)
        self.stdout.write(f'\nCurrent Email Settings:')
        self.stdout.write(f'  Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  Host: {getattr(settings, "EMAIL_HOST", "N/A")}')
        self.stdout.write(f'  Port: {getattr(settings, "EMAIL_PORT", "N/A")}')
        self.stdout.write(f'  Use TLS: {getattr(settings, "EMAIL_USE_TLS", "N/A")}')
        self.stdout.write(f'  From Email: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'  Recipient: {recipient}')
        self.stdout.write('='*60 + '\n')
        
        # Validate email configuration
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: Using console email backend. Emails will be printed to console, not actually sent.'
                )
            )
            self.stdout.write('   To send real emails, set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend\n')
        elif settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
            # Validate SMTP settings
            email_host = getattr(settings, 'EMAIL_HOST', '')
            email_user = getattr(settings, 'EMAIL_HOST_USER', '')
            email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            
            if not email_host:
                self.stdout.write(
                    self.style.ERROR('ERROR: EMAIL_HOST is not set!')
                )
                sys.exit(1)
            
            if not email_user:
                self.stdout.write(
                    self.style.ERROR('ERROR: EMAIL_HOST_USER is not set!')
                )
                sys.exit(1)
            
            if not email_password:
                self.stdout.write(
                    self.style.ERROR('ERROR: EMAIL_HOST_PASSWORD is not set!')
                )
                sys.exit(1)
            
            self.stdout.write(
                self.style.SUCCESS('Email configuration validated')
            )
            self.stdout.write(f'  SMTP Host: {email_host}')
            self.stdout.write(f'  SMTP User: {email_user}')
            self.stdout.write(f'  SMTP Password: {"*" * len(email_password)} (hidden)\n')
        
        # Compose email message
        message = f"""This is a test email from the ASCAI Lazio Django application.

If you received this email, your email configuration is working correctly!

Email Configuration Details:
- Backend: {settings.EMAIL_BACKEND}
- Host: {getattr(settings, "EMAIL_HOST", "N/A")}
- Port: {getattr(settings, "EMAIL_PORT", "N/A")}
- From: {settings.DEFAULT_FROM_EMAIL}

This email was sent to verify that email functionality is properly configured.
"""
        
        try:
            self.stdout.write(f'Sending test email to {recipient}...')
            
            # Log the attempt
            logger.info(f"Attempting to send test email to {recipient}")
            
            # Test connection first
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
                try:
                    connection = get_connection()
                    connection.open()
                    self.stdout.write(self.style.SUCCESS('SMTP connection established'))
                    connection.close()
                except Exception as conn_error:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to establish SMTP connection: {str(conn_error)}')
                    )
                    raise
            
            # Send the email
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            # Log success
            logger.info(f"Test email sent successfully to {recipient}")
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent test email to {recipient}'
                )
            )
            self.stdout.write('='*60)
            self.stdout.write('\nPlease check your inbox (and spam folder) for the test email.')
            self.stdout.write('If you received the email, your configuration is working correctly!\n')
            
        except Exception as e:
            # Log the error
            logger.error(f"Failed to send test email to {recipient}: {str(e)}", exc_info=True)
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )
            self.stdout.write('='*60)
            self.stdout.write('\nTroubleshooting Tips:')
            self.stdout.write('1. Check that EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set correctly')
            self.stdout.write('2. Verify your email provider credentials')
            self.stdout.write('3. For Gmail: Make sure you\'re using an App Password, not your regular password')
            self.stdout.write('   - Remove ALL SPACES from the App Password')
            self.stdout.write('4. For SendGrid: Make sure EMAIL_HOST_USER is set to "apikey"')
            self.stdout.write('5. Check your email provider\'s SMTP settings')
            self.stdout.write('6. Verify firewall/network isn\'t blocking port 587 or 465')
            self.stdout.write('7. Check Railway logs for detailed error messages')
            self.stdout.write('8. Review the EMAIL_IMPLEMENTATION_GUIDE.md for detailed setup instructions\n')
            sys.exit(1)

