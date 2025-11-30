"""
Forms for governance app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import (
    Member, GeneralAssembly, AgendaItem, AssemblyAttendance, AssemblyVote,
    FinancialTransaction, MembershipDues, Contribution,
    ExecutiveBoard, ExecutivePosition, BoardMeeting,
    Election, Candidacy, Communication, AssociationEvent,
)


class MemberForm(forms.ModelForm):
    """Form for member registration/editing (admin)."""
    
    class Meta:
        model = Member
        fields = ['member_type', 'lazio_residence_verified', 'cameroonian_origin_verified', 
                  'membership_start_date', 'membership_end_date', 'notes']
        widgets = {
            'member_type': forms.Select(attrs={'class': 'form-input'}),
            'lazio_residence_verified': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'cameroonian_origin_verified': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'membership_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'membership_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
        }


class MemberSelfRegistrationForm(forms.ModelForm):
    """Form for users to register themselves as ASCAI members."""
    
    class Meta:
        model = Member
        fields = ['member_type']
        widgets = {
            'member_type': forms.Select(attrs={'class': 'form-input'}),
        }
        labels = {
            'member_type': _('Member Type'),
        }
        help_texts = {
            'member_type': _('Select your membership type'),
        }


class GeneralAssemblyForm(forms.ModelForm):
    """Form for General Assembly creation/editing."""
    
    class Meta:
        model = GeneralAssembly
        fields = ['assembly_type', 'date', 'location', 'convocation_date', 'status',
                  'minutes_en', 'minutes_fr', 'minutes_it']
        widgets = {
            'assembly_type': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'convocation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'minutes_en': forms.Textarea(attrs={'rows': 10, 'class': 'form-textarea'}),
            'minutes_fr': forms.Textarea(attrs={'rows': 10, 'class': 'form-textarea'}),
            'minutes_it': forms.Textarea(attrs={'rows': 10, 'class': 'form-textarea'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        convocation_date = cleaned_data.get('convocation_date')
        date = cleaned_data.get('date')
        
        if convocation_date and date:
            # Check 10-day notice requirement (Article 4)
            notice_days = (date.date() - convocation_date).days
            if notice_days < 10:
                raise forms.ValidationError(
                    _('Convocation date must be at least 10 days before assembly date (Article 4).')
                )
        
        return cleaned_data


class AgendaItemForm(forms.ModelForm):
    """Form for agenda item creation/editing."""
    
    class Meta:
        model = AgendaItem
        fields = ['assembly', 'title', 'description', 'item_type', 'proposed_by', 'proposal_date', 
                  'status', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'proposal_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make assembly field required
        self.fields['assembly'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        proposal_date = cleaned_data.get('proposal_date')
        assembly = cleaned_data.get('assembly')
        
        if proposal_date and assembly and assembly.date:
            # Check 14-day advance notice requirement (Article 22)
            notice_days = (assembly.date.date() - proposal_date).days
            if notice_days < 14:
                raise forms.ValidationError(
                    _('Proposal date must be at least 14 days before assembly date (Article 22).')
                )
        
        return cleaned_data


class AssemblyAttendanceForm(forms.ModelForm):
    """Form for assembly attendance."""
    
    class Meta:
        model = AssemblyAttendance
        fields = ['assembly', 'user', 'attendee_name', 'attendee_type', 'attended']
        widgets = {
            'assembly': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make assembly field required
        self.fields['assembly'].required = True
        # Make user field optional if attendee_name is provided
        self.fields['user'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        attendee_name = cleaned_data.get('attendee_name')
        
        if not user and not attendee_name:
            raise forms.ValidationError(
                _('Either user or attendee name must be provided.')
            )
        
        return cleaned_data


class AssemblyVoteForm(forms.ModelForm):
    """Form for recording assembly votes."""
    
    class Meta:
        model = AssemblyVote
        fields = ['assembly', 'agenda_item', 'vote_type', 'voting_method', 'question',
                  'votes_yes', 'votes_no', 'votes_abstain', 'result', 'is_published']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make assembly field required
        self.fields['assembly'].required = True
        # Make agenda_item optional
        self.fields['agenda_item'].required = False


class FinancialTransactionForm(forms.ModelForm):
    """Form for financial transactions."""
    
    class Meta:
        model = FinancialTransaction
        fields = ['transaction_type', 'category', 'amount', 'date', 'description', 'status']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


class MembershipDuesForm(forms.ModelForm):
    """Form for membership dues."""
    
    class Meta:
        model = MembershipDues
        fields = ['member', 'year', 'amount', 'due_date', 'payment_date', 
                  'payment_method', 'status', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-input'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'payment_method': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }


class ContributionForm(forms.ModelForm):
    """Form for contributions."""
    
    class Meta:
        model = Contribution
        fields = ['member', 'contribution_type', 'amount', 'date', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }


class ExecutiveBoardForm(forms.ModelForm):
    """Form for executive board creation/editing."""
    
    class Meta:
        model = ExecutiveBoard
        fields = ['term_start_date', 'term_end_date', 'is_renewed', 'status', 'notes']
        widgets = {
            'term_start_date': forms.DateInput(attrs={'type': 'date'}),
            'term_end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        term_start = cleaned_data.get('term_start_date')
        term_end = cleaned_data.get('term_end_date')
        
        if term_start and term_end:
            # Check 2-year term requirement
            term_days = (term_end - term_start).days
            if term_days != 730:  # Approximately 2 years
                raise forms.ValidationError(
                    _('Executive board term must be exactly 2 years (730 days).')
                )
        
        return cleaned_data


class ExecutivePositionForm(forms.ModelForm):
    """Form for executive position assignment."""
    
    class Meta:
        model = ExecutivePosition
        fields = ['board', 'position', 'user', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class BoardMeetingForm(forms.ModelForm):
    """Form for board meetings."""
    
    class Meta:
        model = BoardMeeting
        fields = ['board', 'meeting_date', 'location', 'agenda', 'minutes', 'decisions']
        widgets = {
            'meeting_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'agenda': forms.Textarea(attrs={'rows': 5}),
            'minutes': forms.Textarea(attrs={'rows': 10}),
            'decisions': forms.Textarea(attrs={'rows': 5}),
        }


class ElectionForm(forms.ModelForm):
    """Form for elections."""
    
    class Meta:
        model = Election
        fields = ['commission', 'election_type', 'start_date', 'end_date', 'status', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            # Check 90-day requirement (Article 11)
            days = (end_date - start_date).days
            if days > 90:
                raise forms.ValidationError(
                    _('Election must be completed within 90 days of commission formation (Article 11).')
                )
        
        return cleaned_data


class CandidacyForm(forms.ModelForm):
    """Form for candidacy applications."""
    
    class Meta:
        model = Candidacy
        fields = ['election', 'position', 'application_date', 'status',
                  'seniority_verified', 'lazio_residence_verified', 
                  'cameroonian_origin_verified', 'eligibility_notes']
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date'}),
            'eligibility_notes': forms.Textarea(attrs={'rows': 4}),
        }


class CommunicationForm(forms.ModelForm):
    """Form for communications."""
    
    class Meta:
        model = Communication
        fields = ['communication_type', 'title', 'content', 'target_audience',
                  'publication_channels', 'is_published', 'requires_president_approval',
                  'president_approved']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'publication_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AssociationEventForm(forms.ModelForm):
    """Form for association events."""
    
    class Meta:
        model = AssociationEvent
        fields = ['title', 'event_type', 'description', 'start_date', 'end_date',
                  'location', 'budget', 'revenue', 'expenses', 'diaspora_event', 'report']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'report': forms.Textarea(attrs={'rows': 10}),
        }

