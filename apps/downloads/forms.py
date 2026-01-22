"""
Forms for downloads app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Document


class DocumentFilterForm(forms.Form):
    """Form for filtering documents."""
    category = forms.ChoiceField(
        choices=[('', _('All Categories'))] + Document.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Tags (comma-separated)')
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green',
            'placeholder': _('Search documents...')
        })
    )
    sort = forms.ChoiceField(
        choices=[
            ('recent', _('Most Recent')),
            ('popular', _('Most Popular')),
            ('name', _('Name (A-Z)'))
        ],
        required=False,
        initial='recent',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green'
        })
    )
