"""
Forms for dashboard app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    SupportTicket, TicketReply, GroupDiscussion, UserStorySubmission,
    StudentQuestion, OrientationSession, StoryImage
)
from apps.accounts.models import User, UserDocument
from apps.universities.models import University

# Import CKEditor 5 widget for rich text editing
try:
    from django_ckeditor_5.widgets import CKEditor5Widget
except ImportError:
    CKEditor5Widget = None


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'phone', 'city_in_lazio', 'university',
            'field_of_study', 'profession', 'occupation', 'arrival_year',
            'date_of_birth', 'language_preference', 'bio', 'avatar'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'autocomplete': 'name',
                'autocorrect': 'on',
                'autocapitalize': 'words'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'autocomplete': 'email',
                'autocorrect': 'off',
                'autocapitalize': 'none',
                'spellcheck': 'false'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'autocomplete': 'tel',
                'autocorrect': 'off',
                'autocapitalize': 'none',
                'spellcheck': 'false'
            }),
            'city_in_lazio': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'university': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'profession': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'occupation': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'arrival_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'language_preference': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'bio': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 4
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
        }


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading user documents."""
    
    class Meta:
        model = UserDocument
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }


class SupportTicketForm(forms.ModelForm):
    """Form for creating support tickets."""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'placeholder': _('Enter ticket subject')
            }),
            'message': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 6,
                'placeholder': _('Describe your issue or question')
            }),
        }


class GroupDiscussionForm(forms.ModelForm):
    """Form for creating group discussions."""
    
    class Meta:
        model = GroupDiscussion
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'content': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 6
            }),
        }


class StorySubmissionForm(forms.ModelForm):
    """Form for submitting diaspora stories."""
    
    class Meta:
        model = UserStorySubmission
        fields = ['title', 'story', 'is_anonymous', 'documents']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'story': CKEditor5Widget(config_name='extends') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 10
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-cameroon-green border-gray-300 rounded focus:ring-cameroon-green'
            }),
            'documents': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
        }


class StudentQuestionForm(forms.ModelForm):
    """Form for submitting student questions."""
    
    class Meta:
        model = StudentQuestion
        fields = ['subject', 'question', 'category']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'question': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 6
            }),
            'category': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'placeholder': _('e.g., Residence Permit, University Enrollment')
            }),
        }


class OrientationBookingForm(forms.ModelForm):
    """Form for booking orientation sessions."""
    
    class Meta:
        model = OrientationSession
        fields = ['preferred_date', 'preferred_time', 'topics']
        widgets = {
            'preferred_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'preferred_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green'
            }),
            'topics': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 4,
                'placeholder': _('What topics would you like to discuss?')
            }),
        }


class TicketReplyForm(forms.ModelForm):
    """Form for replying to support tickets."""
    
    class Meta:
        model = TicketReply
        fields = ['message']
        widgets = {
            'message': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
                'rows': 6,
                'placeholder': _('Type your reply here...')
            }),
        }


class NotificationPreferencesForm(forms.Form):
    """Form for notification preferences."""
    email_notifications = forms.BooleanField(
        required=False,
        label=_('Email Notifications'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-cameroon-green border-gray-300 rounded focus:ring-cameroon-green'
        })
    )
    ticket_updates = forms.BooleanField(
        required=False,
        label=_('Support Ticket Updates'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-cameroon-green border-gray-300 rounded focus:ring-cameroon-green'
        })
    )
    event_reminders = forms.BooleanField(
        required=False,
        label=_('Event Reminders'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-cameroon-green border-gray-300 rounded focus:ring-cameroon-green'
        })
    )
    group_announcements = forms.BooleanField(
        required=False,
        label=_('Group Announcements'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-cameroon-green border-gray-300 rounded focus:ring-cameroon-green'
        })
    )
