"""
Forms for mentorship app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import MentorProfile, MentorshipRequest, MentorshipMessage, MentorRating


class MentorProfileForm(forms.ModelForm):
    """Form for creating mentor profile."""
    
    class Meta:
        model = MentorProfile
        fields = ['specialization', 'years_experience', 'bio', 'availability_status']
        widgets = {
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('e.g., Engineering, Medicine, Law')
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 8
            }),
            'availability_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
        }


class MentorshipRequestForm(forms.ModelForm):
    """Form for creating mentorship request."""
    
    class Meta:
        model = MentorshipRequest
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
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
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 4,
                'placeholder': _('Type your message...')
            }),
        }


class MentorRatingForm(forms.ModelForm):
    """Form for rating a mentor."""
    
    class Meta:
        model = MentorRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 4,
                'placeholder': _('Share your experience (optional)...')
            }),
        }


class MentorProfileUpdateForm(forms.ModelForm):
    """Form for updating mentor profile."""
    
    class Meta:
        model = MentorProfile
        fields = ['specialization', 'years_experience', 'bio', 'availability_status']
        widgets = {
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('e.g., Engineering, Medicine, Law')
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 8
            }),
            'availability_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
        }

