"""
Forms for community app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ForumThread, ForumPost, ForumCategory

# Import CKEditor 5 widget for rich text editing
try:
    from django_ckeditor_5.widgets import CKEditor5Widget
except ImportError:
    CKEditor5Widget = None


class ThreadForm(forms.ModelForm):
    """Form for creating forum threads."""
    
    class Meta:
        model = ForumThread
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-transparent',
                'placeholder': _('Thread title')
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-transparent'
            }),
            'content': CKEditor5Widget(config_name='extends') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-transparent',
                'rows': 10,
                'placeholder': _('Thread content')
            }),
        }


class PostForm(forms.ModelForm):
    """Form for creating forum posts."""
    
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': CKEditor5Widget(config_name='default') if CKEditor5Widget else forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-transparent',
                'rows': 5,
                'placeholder': _('Your reply...')
            }),
        }

