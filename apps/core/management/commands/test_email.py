"""
Management command to test email configuration by sending a test email.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys


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
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully sent test email to {recipient}'
                )
            )
            self.stdout.write('='*60)
            self.stdout.write('\nPlease check your inbox (and spam folder) for the test email.')
            self.stdout.write('If you received the email, your configuration is working correctly!\n')
            
        except Exception as e:
            self.stdout.write('\n' + '='*60)
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email: {str(e)}')
            )
            self.stdout.write('='*60)
            self.stdout.write('\nTroubleshooting Tips:')
            self.stdout.write('1. Check that EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set correctly')
            self.stdout.write('2. Verify your email provider credentials')
            self.stdout.write('3. For Gmail: Make sure you\'re using an App Password, not your regular password')
            self.stdout.write('4. For SendGrid: Make sure EMAIL_HOST_USER is set to "apikey"')
            self.stdout.write('5. Check your email provider\'s SMTP settings')
            self.stdout.write('6. Verify firewall/network isn\'t blocking port 587 or 465')
            self.stdout.write('7. Review the EMAIL_IMPLEMENTATION_GUIDE.md for detailed setup instructions\n')
            sys.exit(1)

