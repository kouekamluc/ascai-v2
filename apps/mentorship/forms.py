"""
Forms for mentorship app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import MentorProfile, MentorshipRequest, MentorshipMessage


class MentorProfileForm(forms.ModelForm):
    """Form for creating mentor profile."""
    
    class Meta:
        model = MentorProfile
        fields = ['specialization', 'years_experience', 'bio', 'availability_status']
        widgets = {
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('e.g., Engineering, Medicine, Law')
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 8
            }),
            'availability_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }


class MentorshipRequestForm(forms.ModelForm):
    """Form for creating mentorship request."""
    
    class Meta:
        model = MentorshipRequest
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 6
            }),
        }


class MentorshipMessageForm(forms.ModelForm):
    """Form for sending mentorship messages."""
    
    class Meta:
        model = MentorshipMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': _('Type your message...')
            }),
        }

