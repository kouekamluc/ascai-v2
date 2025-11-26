"""
Forms for contact app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    """Contact form."""
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-colors duration-200 bg-white text-gray-900',
                'placeholder': _('Your name'),
                'autocomplete': 'name',
                'autocorrect': 'on',
                'autocapitalize': 'words',
                'spellcheck': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-colors duration-200 bg-white text-gray-900',
                'placeholder': _('Your email'),
                'autocomplete': 'email',
                'autocorrect': 'off',
                'autocapitalize': 'none',
                'spellcheck': 'false'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-colors duration-200 bg-white text-gray-900',
                'placeholder': _('Subject'),
                'autocomplete': 'off',
                'autocorrect': 'on',
                'autocapitalize': 'sentences',
                'spellcheck': 'true'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-colors duration-200 resize-y bg-white text-gray-900',
                'rows': 6,
                'placeholder': _('Your message'),
                'autocomplete': 'off',
                'autocorrect': 'on',
                'autocapitalize': 'sentences',
                'spellcheck': 'true'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['subject'].required = True
        self.fields['message'].required = True

