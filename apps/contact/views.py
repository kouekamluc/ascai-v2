"""
Views for contact app.
"""
from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.email_utils import send_branded_email

from .models import ContactSubmission
from .forms import ContactForm


class ContactView(FormView):
    """Contact form view."""
    form_class = ContactForm
    template_name = 'contact/index.html'
    success_url = reverse_lazy('contact:success')
    
    def form_valid(self, form):
        # Save submission
        submission = form.save()
        
        # Send email
        try:
            # Prepare email content
            email_body = f"""
New contact form submission from ASCAI Lazio website:

From: {submission.name}
Email: {submission.email}
{f'Phone: {submission.phone}' if submission.phone else ''}
Subject: {submission.subject}

Message:
{submission.message}

---
This message was sent from the ASCAI Lazio contact form.
Submitted on: {submission.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Get contact email from settings (defaults to info@ascai.org)
            contact_email = getattr(settings, 'CONTACT_EMAIL', 'info@ascai.org')
            
            send_branded_email(
                subject=f"ASCAI Lazio Contact: {submission.subject}",
                text_body=email_body,
                template_name='email/generic_message.html',
                context={
                    'email_title': _('New Contact Form Submission'),
                    'greeting': _('Hello,'),
                    'body_paragraphs': [
                        _('A new message has been submitted from the ASCAI Lazio website contact form.'),
                    ],
                    'detail_rows': [
                        {'label': _('From'), 'value': submission.name},
                        {'label': _('Email'), 'value': submission.email},
                        {'label': _('Phone'), 'value': submission.phone or '-'},
                        {'label': _('Subject'), 'value': submission.subject},
                        {'label': _('Submitted'), 'value': submission.created_at.strftime('%Y-%m-%d %H:%M:%S')},
                    ],
                    'message_body': submission.message,
                    'closing_paragraphs': [
                        _('This message was sent from the ASCAI Lazio contact form.'),
                    ],
                },
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_email],
                fail_silently=False,
                request=self.request,
            )
        except Exception as e:
            # Log error but don't fail the submission
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send contact email: {str(e)}")
        
        # Handle HTMX requests
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'contact/partials/success_message.html')
        
        messages.success(self.request, _('Thank you for your message! We will get back to you soon.'))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'contact/partials/contact_form.html', {
                'form': form
            }, status=400)
        return super().form_invalid(form)


class ContactSuccessView(TemplateView):
    """Contact success page."""
    template_name = 'contact/success.html'
