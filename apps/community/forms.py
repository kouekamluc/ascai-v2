"""
Forms for community app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ForumThread, ForumPost, ForumCategory


class ThreadForm(forms.ModelForm):
    """Form for creating forum threads."""
    
    class Meta:
        model = ForumThread
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': _('Thread title')
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
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
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 5,
                'placeholder': _('Your reply...')
            }),
        }

