"""
Forms for diaspora app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event
from apps.dashboard.models import UserStorySubmission, StoryImage

# Import CKEditor 5 widget for rich text editing
try:
    from django_ckeditor_5.widgets import CKEditor5Widget
except ImportError:
    CKEditor5Widget = None


class EventFilterForm(forms.Form):
    """Form for filtering events."""
    event_type = forms.ChoiceField(
        choices=[('', _('All Types'))] + Event.EVENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
    date_filter = forms.ChoiceField(
        choices=[
            ('upcoming', _('Upcoming')),
            ('past', _('Past'))
        ],
        required=False,
        initial='upcoming',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Location...')
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Search events...')
        })
    )


class EventSearchForm(forms.Form):
    """Form for searching events."""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Search events...')
        })
    )


class StorySubmissionForm(forms.ModelForm):
    """Multi-step form for story submission."""
    
    class Meta:
        model = UserStorySubmission
        fields = ['title', 'story', 'cover_image', 'submission_type', 'tags', 'location', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'story': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'rows': 12
            }),
            'submission_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('e.g., student, rome, success')
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('e.g., Rome, Italy')
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-cameroon-green border-gray-300 rounded focus:ring-cameroon-green'
            }),
        }


class StoryImageForm(forms.ModelForm):
    """Form for uploading story images."""
    
    class Meta:
        model = StoryImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
                'placeholder': _('Image caption (optional)')
            }),
        }
