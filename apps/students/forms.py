"""
Forms for students app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import StudentGuideProgress


class GuideProgressForm(forms.ModelForm):
    """Form for saving guide progress."""
    
    class Meta:
        model = StudentGuideProgress
        fields = ['is_completed']
        widgets = {
            'is_completed': forms.HiddenInput()
        }
