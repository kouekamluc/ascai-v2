"""
Views for contact app.
"""
from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
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
            send_mail(
                subject=f"ASCAI Lazio Contact: {submission.subject}",
                message=f"From: {submission.name} ({submission.email})\n\n{submission.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail the submission
            pass
        
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

