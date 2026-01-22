"""
Forms for mentorship app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    MentorProfile, MentorshipRequest, MentorshipMessage,
    MentorRating, MentorshipSession
)

# Import CKEditor 5 widget for rich text editing
try:
    from django_ckeditor_5.widgets import CKEditor5Widget
except ImportError:
    CKEditor5Widget = None


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
            'bio': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
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
            'message': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
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
            'content': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
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
            'comment': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 4,
                'placeholder': _('Share your experience (optional)...')
            }),
        }


class MentorProfileUpdateForm(forms.ModelForm):
    """Form for updating mentor profile."""
    
    class Meta:
        model = MentorProfile
        fields = ['specialization', 'specializations', 'years_experience', 'bio', 'profile_image', 
                  'availability_status', 'availability_calendar', 'response_time']
        widgets = {
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('e.g., Engineering, Medicine, Law')
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'bio': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 8
            }),
            'availability_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'response_time': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('e.g., "Within 24 hours"')
            }),
        }


class MentorshipSessionForm(forms.ModelForm):
    """Form for scheduling a mentorship session."""
    
    class Meta:
        model = MentorshipSession
        fields = ['scheduled_at', 'duration', 'location', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'duration': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('Physical location or video call link')
            }),
            'notes': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 4,
                'placeholder': _('Session agenda or notes...')
            }),
        }


class MentorFilterForm(forms.Form):
    """Form for filtering mentors."""
    specialization = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label=_('All Specializations'),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
    availability = forms.ChoiceField(
        choices=[('', _('All Availability'))] + MentorProfile.AVAILABILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
    min_rating = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Min rating'),
            'step': '0.1'
        })
    )
    min_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Min years')
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Search mentors...')
        })
    )
    sort = forms.ChoiceField(
        choices=[
            ('rating', _('Rating')),
            ('experience', _('Experience')),
            ('students', _('Students Helped')),
            ('success', _('Success Rate'))
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import MentorSpecialization
        self.fields['specialization'].queryset = MentorSpecialization.objects.all().order_by('order', 'name')

