"""
Governance models for ASCAI Association management.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()

# Executive Position choices (defined at module level for reuse)
EXECUTIVE_POSITION_CHOICES = [
    ('president', _('President')),
    ('vice_president', _('Vice-President')),
    ('secretary_general', _('Secretary General')),
    ('deputy_secretary_general', _('Deputy Secretary General')),
    ('treasurer', _('Treasurer')),
    ('statutory_auditor', _('Statutory Auditor')),
    ('communication_culture_manager', _('Communication and Culture Manager')),
]


# ============================================================================
# MEMBERSHIP MANAGEMENT
# ============================================================================

class Member(models.Model):
    """
    ASCAI Association member profile extending User model.
    """
    MEMBER_TYPE_CHOICES = [
        ('student', _('Student Member')),
        ('active', _('Active Member')),
        ('sympathizer', _('Sympathizer')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile',
        verbose_name=_('User')
    )
    
    member_type = models.CharField(
        max_length=20,
        choices=MEMBER_TYPE_CHOICES,
        default='student',
        verbose_name=_('Member Type')
    )
    
    registration_date = models.DateField(
        auto_now_add=True,
        verbose_name=_('Registration Date')
    )
    
    membership_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Membership Start Date')
    )
    
    membership_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Membership End Date')
    )
    
    # Verification fields
    lazio_residence_verified = models.BooleanField(
        default=False,
        verbose_name=_('Lazio Residence Verified'),
        help_text=_('Verified that member lives in Lazio region')
    )
    
    cameroonian_origin_verified = models.BooleanField(
        default=False,
        verbose_name=_('Cameroonian Origin Verified'),
        help_text=_('Verified that member is Cameroonian or of Cameroonian origin')
    )
    
    # Active member criteria (Article 2)
    is_active_member = models.BooleanField(
        default=False,
        verbose_name=_('Active Member'),
        help_text=_('Regularly participates in General Assemblies and pays contributions')
    )
    
    last_assembly_attendance = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last Assembly Attendance')
    )
    
    is_founding_member = models.BooleanField(
        default=False,
        verbose_name=_('Founding Member'),
        help_text=_('Founding member of ASCAI Association (automatically included in Board of Auditors per Article 8)')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes'),
        help_text=_('Internal notes about this member')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.get_display_name()} ({self.get_member_type_display()})"
    
    def get_absolute_url(self):
        return reverse('governance:member_detail', kwargs={'pk': self.pk})
    
    @property
    def is_currently_active(self):
        """Check if member is currently active based on participation and contributions."""
        if not self.is_active_member:
            return False
        
        # Check if membership hasn't expired
        if self.membership_end_date and self.membership_end_date < timezone.now().date():
            return False
        
        return True


class MembershipStatus(models.Model):
    """
    Track membership lifecycle and status changes.
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended')),
        ('expelled', _('Expelled')),
    ]
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Member')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    effective_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Effective Date')
    )
    
    last_payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last Payment Date')
    )
    
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason'),
        help_text=_('Reason for status change')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Membership Status')
        verbose_name_plural = _('Membership Statuses')
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.member} - {self.get_status_display()} ({self.effective_date})"


# ============================================================================
# EXECUTIVE BOARD MANAGEMENT
# ============================================================================

class ExecutiveBoard(models.Model):
    """
    Executive Board of ASCAI Association.
    Term: 2 years, renewable once (Article 13, 14, 15, 16).
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('terminated', _('Terminated')),
    ]
    
    term_start_date = models.DateField(
        verbose_name=_('Term Start Date')
    )
    
    term_end_date = models.DateField(
        verbose_name=_('Term End Date'),
        help_text=_('2 years from start date, renewable once')
    )
    
    is_renewed = models.BooleanField(
        default=False,
        verbose_name=_('Renewed Term'),
        help_text=_('Whether this is a renewed term (max 1 renewal allowed)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Executive Board')
        verbose_name_plural = _('Executive Boards')
        ordering = ['-term_start_date']
    
    def __str__(self):
        return f"Executive Board {self.term_start_date.year}-{self.term_end_date.year}"
    
    @property
    def is_current(self):
        """Check if this is the current active board."""
        today = timezone.now().date()
        return (self.status == 'active' and 
                self.term_start_date <= today <= self.term_end_date)


class ExecutivePosition(models.Model):
    """
    Executive Board positions (Article 13).
    """
    POSITION_CHOICES = EXECUTIVE_POSITION_CHOICES
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('resigned', _('Resigned')),
        ('replaced', _('Replaced')),
    ]
    
    board = models.ForeignKey(
        ExecutiveBoard,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('Executive Board')
    )
    
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        verbose_name=_('Position')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='executive_positions',
        verbose_name=_('User')
    )
    
    start_date = models.DateField(
        verbose_name=_('Start Date')
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('End Date')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    resignation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Resignation Date')
    )
    
    resignation_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Resignation Reason')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Executive Position')
        verbose_name_plural = _('Executive Positions')
        ordering = ['board', 'position']
        unique_together = [['board', 'position']]
    
    def __str__(self):
        return f"{self.get_position_display()} - {self.user.get_display_name() if self.user else 'Vacant'}"


class BoardMeeting(models.Model):
    """
    Executive Board meetings.
    """
    board = models.ForeignKey(
        ExecutiveBoard,
        on_delete=models.CASCADE,
        related_name='meetings',
        verbose_name=_('Executive Board')
    )
    
    meeting_date = models.DateTimeField(
        verbose_name=_('Meeting Date')
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Location')
    )
    
    agenda = models.TextField(
        verbose_name=_('Agenda')
    )
    
    minutes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Minutes')
    )
    
    decisions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Decisions Made')
    )
    
    attendees = models.ManyToManyField(
        User,
        related_name='board_meetings_attended',
        blank=True,
        verbose_name=_('Attendees')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Board Meeting')
        verbose_name_plural = _('Board Meetings')
        ordering = ['-meeting_date']
    
    def __str__(self):
        return f"Board Meeting - {self.meeting_date.strftime('%Y-%m-%d')}"


# ============================================================================
# GENERAL ASSEMBLY SYSTEM
# ============================================================================

class GeneralAssembly(models.Model):
    """
    General Assembly meetings (Article 2, 6, 7).
    Types: AGM (Ordinary), AGEX (Extraordinary), EGM (Elective).
    """
    ASSEMBLY_TYPE_CHOICES = [
        ('agm', _('Ordinary General Assembly (AGM)')),
        ('agex', _('Extraordinary General Assembly (AGEX)')),
        ('egm', _('Elective General Assembly (EGM)')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    assembly_type = models.CharField(
        max_length=10,
        choices=ASSEMBLY_TYPE_CHOICES,
        verbose_name=_('Assembly Type')
    )
    
    date = models.DateTimeField(
        verbose_name=_('Assembly Date')
    )
    
    location = models.CharField(
        max_length=200,
        verbose_name=_('Location')
    )
    
    convocation_date = models.DateField(
        verbose_name=_('Convocation Date'),
        help_text=_('Date when notice was published (must be at least 10 days before assembly)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('Status')
    )
    
    # Minutes in multiple languages (Article 25)
    minutes_en = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Minutes (English)')
    )
    
    minutes_fr = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Minutes (Français)')
    )
    
    minutes_it = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Minutes (Italiano)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('General Assembly')
        verbose_name_plural = _('General Assemblies')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_assembly_type_display()} - {self.date.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        return reverse('governance:assembly_detail', kwargs={'pk': self.pk})
    
    @property
    def notice_period_days(self):
        """Calculate days between convocation and assembly date."""
        if self.convocation_date and self.date:
            delta = self.date.date() - self.convocation_date
            return delta.days
        return None


class AgendaItem(models.Model):
    """
    Agenda items for General Assemblies (Article 20, 21, 22).
    """
    ITEM_TYPE_CHOICES = [
        ('finance', _('Finance')),
        ('activities', _('Activities')),
        ('miscellaneous', _('Miscellaneous')),
        ('statute_amendment', _('Statute Amendment')),
        ('election', _('Election')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('proposed', _('Proposed')),
        ('approved', _('Approved')),
        ('discussed', _('Discussed')),
        ('resolved', _('Resolved')),
    ]
    
    assembly = models.ForeignKey(
        GeneralAssembly,
        on_delete=models.CASCADE,
        related_name='agenda_items',
        verbose_name=_('General Assembly')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    description = models.TextField(
        verbose_name=_('Description')
    )
    
    item_type = models.CharField(
        max_length=30,
        choices=ITEM_TYPE_CHOICES,
        default='miscellaneous',
        verbose_name=_('Item Type')
    )
    
    proposed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proposed_agenda_items',
        verbose_name=_('Proposed By')
    )
    
    proposal_date = models.DateField(
        verbose_name=_('Proposal Date'),
        help_text=_('Must be at least 14 days before assembly')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed',
        verbose_name=_('Status')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
        help_text=_('Display order in agenda')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Agenda Item')
        verbose_name_plural = _('Agenda Items')
        ordering = ['assembly', 'order', 'title']
    
    def __str__(self):
        return f"{self.assembly} - {self.title}"


class RulesOfProcedureAmendment(models.Model):
    """
    Rules of Procedure amendment proposals (Article 47).
    Members can propose amendments 30 days before assembly.
    """
    STATUS_CHOICES = [
        ('proposed', _('Proposed')),
        ('approved', _('Approved for Assembly')),
        ('rejected', _('Rejected')),
        ('discussed', _('Discussed')),
        ('adopted', _('Adopted')),
        ('withdrawn', _('Withdrawn')),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Amendment Title')
    )
    
    description = models.TextField(
        verbose_name=_('Amendment Description'),
        help_text=_('Detailed description of the proposed amendment')
    )
    
    proposed_article = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Article Number'),
        help_text=_('Article number being amended (if applicable)')
    )
    
    proposed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proposed_amendments',
        verbose_name=_('Proposed By')
    )
    
    proposal_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Proposal Date')
    )
    
    target_assembly = models.ForeignKey(
        GeneralAssembly,
        on_delete=models.CASCADE,
        related_name='amendment_proposals',
        verbose_name=_('Target Assembly'),
        help_text=_('Assembly where this amendment will be discussed')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed',
        verbose_name=_('Status')
    )
    
    # Validation: must be proposed 30 days before assembly (Article 47)
    meets_deadline = models.BooleanField(
        default=False,
        verbose_name=_('Meets 30-Day Deadline'),
        help_text=_('Proposed at least 30 days before assembly')
    )
    
    discussion_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Discussion Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Rules of Procedure Amendment')
        verbose_name_plural = _('Rules of Procedure Amendments')
        ordering = ['-proposal_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.target_assembly}"
    
    def check_30_day_deadline(self):
        """Check if proposal meets 30-day deadline requirement (Article 47)."""
        if not self.target_assembly or not self.target_assembly.date:
            return False
        
        days_before = (self.target_assembly.date.date() - self.proposal_date).days
        return days_before >= 30
    
    def save(self, *args, **kwargs):
        """Auto-check 30-day deadline on save."""
        self.meets_deadline = self.check_30_day_deadline()
        super().save(*args, **kwargs)


class AssemblyAttendance(models.Model):
    """
    Track attendance at General Assemblies (Article 5).
    """
    ATTENDEE_TYPE_CHOICES = [
        ('member', _('Member')),
        ('active_member', _('Active Member')),
        ('sympathizer', _('Sympathizer')),
        ('guest', _('Guest')),
        ('authority', _('Authority/Institution')),
    ]
    
    assembly = models.ForeignKey(
        GeneralAssembly,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('General Assembly')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assembly_attendances',
        null=True,
        blank=True,
        verbose_name=_('User')
    )
    
    attendee_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Attendee Name'),
        help_text=_('Name if not a registered user')
    )
    
    attendee_type = models.CharField(
        max_length=20,
        choices=ATTENDEE_TYPE_CHOICES,
        verbose_name=_('Attendee Type')
    )
    
    attended = models.BooleanField(
        default=True,
        verbose_name=_('Attended')
    )
    
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Registered At')
    )
    
    class Meta:
        verbose_name = _('Assembly Attendance')
        verbose_name_plural = _('Assembly Attendances')
        unique_together = [['assembly', 'user']]
        ordering = ['assembly', 'attendee_type', 'user']
    
    def __str__(self):
        name = self.user.get_display_name() if self.user else self.attendee_name
        return f"{self.assembly} - {name}"


class AssemblyVote(models.Model):
    """
    Voting records for General Assemblies (Article 24, 32, 36).
    """
    VOTE_TYPE_CHOICES = [
        ('resolution', _('Resolution')),
        ('election', _('Election')),
        ('amendment', _('Amendment')),
        ('other', _('Other')),
    ]
    
    VOTING_METHOD_CHOICES = [
        ('show_of_hands', _('Show of Hands')),
        ('secret_ballot', _('Secret Ballot')),
    ]
    
    assembly = models.ForeignKey(
        GeneralAssembly,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name=_('General Assembly')
    )
    
    agenda_item = models.ForeignKey(
        AgendaItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='votes',
        verbose_name=_('Agenda Item')
    )
    
    vote_type = models.CharField(
        max_length=20,
        choices=VOTE_TYPE_CHOICES,
        verbose_name=_('Vote Type')
    )
    
    voting_method = models.CharField(
        max_length=20,
        choices=VOTING_METHOD_CHOICES,
        default='show_of_hands',
        verbose_name=_('Voting Method')
    )
    
    question = models.TextField(
        verbose_name=_('Question/Proposal')
    )
    
    # Vote results
    votes_yes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Votes Yes')
    )
    
    votes_no = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Votes No')
    )
    
    votes_abstain = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Votes Abstain')
    )
    
    result = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Result'),
        help_text=_('e.g., "Approved", "Rejected"')
    )
    
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Published'),
        help_text=_('Published within 30 days as per Article 24')
    )
    
    published_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Published Date')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Assembly Vote')
        verbose_name_plural = _('Assembly Votes')
        ordering = ['assembly', '-created_at']
    
    def __str__(self):
        return f"{self.assembly} - {self.question[:50]}"
    
    @property
    def total_votes(self):
        """Calculate total votes cast."""
        return self.votes_yes + self.votes_no + self.votes_abstain
    
    @property
    def days_since_assembly(self):
        """Calculate days since assembly date (for 30-day publication deadline - Article 24)."""
        if self.assembly and self.assembly.date:
            delta = timezone.now().date() - self.assembly.date.date()
            return delta.days
        return None
    
    @property
    def is_publication_overdue(self):
        """Check if vote results publication is overdue (Article 24 - 30 days)."""
        if self.is_published:
            return False
        days = self.days_since_assembly
        return days is not None and days > 30
    
    @property
    def days_until_publication_deadline(self):
        """Calculate days remaining until 30-day publication deadline."""
        if self.is_published:
            return None
        days = self.days_since_assembly
        if days is not None:
            return max(0, 30 - days)
        return None


class AssemblyVoteRecord(models.Model):
    """
    Individual vote records for assembly votes.
    Tracks who voted and their choice (for show of hands) or just that they voted (for secret ballot).
    """
    vote = models.ForeignKey(
        AssemblyVote,
        on_delete=models.CASCADE,
        related_name='vote_records',
        verbose_name=_('Assembly Vote')
    )
    
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assembly_vote_records',
        verbose_name=_('Voter')
    )
    
    choice = models.CharField(
        max_length=10,
        choices=[('yes', _('Yes')), ('no', _('No')), ('abstain', _('Abstain'))],
        verbose_name=_('Choice')
    )
    
    vote_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Vote Timestamp')
    )
    
    class Meta:
        verbose_name = _('Assembly Vote Record')
        verbose_name_plural = _('Assembly Vote Records')
        unique_together = [['vote', 'voter']]
        ordering = ['vote', 'vote_timestamp']
    
    def __str__(self):
        return f"{self.voter.get_display_name()} - {self.get_choice_display()} ({self.vote})"


# ============================================================================
# FINANCIAL MANAGEMENT
# ============================================================================

class FinancialTransaction(models.Model):
    """
    All financial transactions (Article 39, 44).
    Expenses require 3 signatures: President, Treasurer, Statutory Auditor.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', _('Income')),
        ('expense', _('Expense')),
    ]
    
    CATEGORY_CHOICES = [
        ('membership_fees', _('Membership Fees')),
        ('event_proceeds', _('Event Proceeds')),
        ('donations', _('Donations')),
        ('bequests', _('Bequests')),
        ('financial_aid', _('Financial Aid')),
        ('operational', _('Operational Expenses')),
        ('event_expenses', _('Event Expenses')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('completed', _('Completed')),
        ('rejected', _('Rejected')),
    ]
    
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name=_('Transaction Type')
    )
    
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Category')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount')
    )
    
    date = models.DateField(
        default=timezone.now,
        verbose_name=_('Date')
    )
    
    description = models.TextField(
        verbose_name=_('Description')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # For expenses: requires 3 signatures
    requires_approval = models.BooleanField(
        default=False,
        verbose_name=_('Requires Approval'),
        help_text=_('Expenses require 3 signatures: President, Treasurer, Statutory Auditor')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_transactions',
        verbose_name=_('Created By')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Financial Transaction')
        verbose_name_plural = _('Financial Transactions')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - €{self.amount} - {self.date}"
    
    def save(self, *args, **kwargs):
        """Set requires_approval for expenses."""
        if self.transaction_type == 'expense':
            self.requires_approval = True
        super().save(*args, **kwargs)


class MembershipDues(models.Model):
    """
    Annual membership dues (Article 40, 43).
    Members: €10/year, Sympathizers: €5/year
    Due date: March 31
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('waived', _('Waived')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('bank_transfer', _('Bank Transfer')),
        ('online', _('Online Payment')),
        ('other', _('Other')),
    ]
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='dues',
        verbose_name=_('Member')
    )
    
    year = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2100)],
        verbose_name=_('Year')
    )
    
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount'),
        help_text=_('€10 for members, €5 for sympathizers')
    )
    
    due_date = models.DateField(
        verbose_name=_('Due Date'),
        help_text=_('March 31 of the year')
    )
    
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Payment Date')
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('Payment Method')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Membership Dues')
        verbose_name_plural = _('Membership Dues')
        unique_together = [['member', 'year']]
        ordering = ['-year', 'member']
    
    def __str__(self):
        return f"{self.member} - {self.year} - €{self.amount}"
    
    @property
    def is_overdue(self):
        """Check if dues are overdue (3 months after due date = membership loss)."""
        if self.status == 'paid':
            return False
        if self.due_date:
            three_months_later = self.due_date + timedelta(days=90)
            return timezone.now().date() > three_months_later
        return False


class Contribution(models.Model):
    """
    Member contributions (Article 39).
    """
    CONTRIBUTION_TYPE_CHOICES = [
        ('annual_dues', _('Annual Dues')),
        ('event_contribution', _('Event Contribution')),
        ('donation', _('Donation')),
        ('other', _('Other')),
    ]
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='contributions',
        verbose_name=_('Member')
    )
    
    contribution_type = models.CharField(
        max_length=30,
        choices=CONTRIBUTION_TYPE_CHOICES,
        verbose_name=_('Contribution Type')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount')
    )
    
    date = models.DateField(
        default=timezone.now,
        verbose_name=_('Date')
    )
    
    purpose = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Purpose')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Contribution')
        verbose_name_plural = _('Contributions')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.member} - €{self.amount} - {self.date}"


class FinancialReport(models.Model):
    """
    Financial reports (Article 17, 18, 45).
    Quarterly, annual, and event-based reports.
    """
    REPORT_TYPE_CHOICES = [
        ('quarterly', _('Quarterly')),
        ('annual', _('Annual')),
        ('event_based', _('Event-Based')),
        ('other', _('Other')),
    ]
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name=_('Report Type')
    )
    
    period_start = models.DateField(
        verbose_name=_('Period Start')
    )
    
    period_end = models.DateField(
        verbose_name=_('Period End')
    )
    
    # Summary fields
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Income')
    )
    
    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Expenses')
    )
    
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Balance')
    )
    
    report_content = models.TextField(
        verbose_name=_('Report Content')
    )
    
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name=_('Generated By'),
        help_text=_('Treasurer')
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_reports',
        verbose_name=_('Verified By'),
        help_text=_('Statutory Auditor')
    )
    
    verified_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Verified Date')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Financial Report')
        verbose_name_plural = _('Financial Reports')
        ordering = ['-period_end', '-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} Report - {self.period_start} to {self.period_end}"
    
    @property
    def days_since_period_end(self):
        """Calculate days since report period ended."""
        if self.period_end:
            delta = timezone.now().date() - self.period_end
            return delta.days
        return None


class ExpenseApproval(models.Model):
    """
    Multi-signature approval for expenses (Article 44).
    Requires: President, Treasurer, Statutory Auditor.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('signed', _('Signed')),
        ('rejected', _('Rejected')),
    ]
    
    transaction = models.ForeignKey(
        FinancialTransaction,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name=_('Transaction')
    )
    
    signer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expense_approvals',
        verbose_name=_('Signer')
    )
    
    signature_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Signature Date')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Expense Approval')
        verbose_name_plural = _('Expense Approvals')
        unique_together = [['transaction', 'signer']]
        ordering = ['transaction', 'created_at']
    
    def __str__(self):
        return f"{self.transaction} - {self.signer.get_display_name()} - {self.get_status_display()}"


# ============================================================================
# ELECTORAL SYSTEM
# ============================================================================

class ElectoralCommission(models.Model):
    """
    Electoral Commission for elections (Article 9, 31).
    Members: President, Vice-President, Secretary, Communication Officer, Advisor, 2 Scrutineers.
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('Commission Name'),
        help_text=_('e.g., "2024 Electoral Commission"')
    )
    
    start_date = models.DateField(
        verbose_name=_('Start Date')
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('End Date')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Electoral Commission')
        verbose_name_plural = _('Electoral Commissions')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


class CommissionMember(models.Model):
    """
    Members of the Electoral Commission.
    """
    ROLE_CHOICES = [
        ('president', _('President')),
        ('vice_president', _('Vice-President')),
        ('secretary', _('Secretary')),
        ('communication_officer', _('Communication Officer')),
        ('advisor', _('Advisor')),
        ('scrutineer', _('Scrutineer')),
    ]
    
    commission = models.ForeignKey(
        ElectoralCommission,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('Electoral Commission')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commission_memberships',
        verbose_name=_('User')
    )
    
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        verbose_name=_('Role')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Commission Member')
        verbose_name_plural = _('Commission Members')
        unique_together = [['commission', 'user']]
        ordering = ['commission', 'role']
    
    def __str__(self):
        return f"{self.commission} - {self.user.get_display_name()} ({self.get_role_display()})"


class Election(models.Model):
    """
    Election process (Article 7, 31, 34).
    Executive Board elections every 2 years.
    """
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    ELECTION_TYPE_CHOICES = [
        ('executive_board', _('Executive Board')),
    ]
    
    commission = models.ForeignKey(
        ElectoralCommission,
        on_delete=models.SET_NULL,
        null=True,
        related_name='elections',
        verbose_name=_('Electoral Commission')
    )
    
    election_type = models.CharField(
        max_length=50,
        choices=ELECTION_TYPE_CHOICES,
        default='executive_board',
        verbose_name=_('Election Type'),
        help_text=_('Currently only Executive Board elections')
    )
    
    start_date = models.DateField(
        verbose_name=_('Start Date')
    )
    
    end_date = models.DateField(
        verbose_name=_('End Date'),
        help_text=_('Must be within 90 days of commission formation')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Election')
        verbose_name_plural = _('Elections')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.get_election_type_display()} - {self.start_date.year}"


class Candidacy(models.Model):
    """
    Candidate applications for elections (Article 33).
    Eligibility: 1+ year seniority, Lazio residence, Cameroonian origin.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('withdrawn', _('Withdrawn')),
    ]
    
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='candidacies',
        verbose_name=_('Election')
    )
    
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='candidacies',
        verbose_name=_('Candidate')
    )
    
    position = models.CharField(
        max_length=50,
        choices=EXECUTIVE_POSITION_CHOICES,
        verbose_name=_('Position')
    )
    
    application_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Application Date')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Eligibility verification
    seniority_verified = models.BooleanField(
        default=False,
        verbose_name=_('Seniority Verified'),
        help_text=_('1+ year seniority in association')
    )
    
    lazio_residence_verified = models.BooleanField(
        default=False,
        verbose_name=_('Lazio Residence Verified')
    )
    
    cameroonian_origin_verified = models.BooleanField(
        default=False,
        verbose_name=_('Cameroonian Origin Verified')
    )
    
    eligibility_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Eligibility Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Candidacy')
        verbose_name_plural = _('Candidacies')
        unique_together = [['election', 'candidate', 'position']]
        ordering = ['election', 'position', 'application_date']
    
    def __str__(self):
        return f"{self.candidate.get_display_name()} - {self.get_position_display()} ({self.election})"


class ElectionVote(models.Model):
    """
    Secret ballot votes in elections (Article 32, 36).
    """
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name=_('Election')
    )
    
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='election_votes',
        verbose_name=_('Voter')
    )
    
    candidate = models.ForeignKey(
        Candidacy,
        on_delete=models.CASCADE,
        related_name='votes_received',
        verbose_name=_('Candidate')
    )
    
    position = models.CharField(
        max_length=50,
        choices=EXECUTIVE_POSITION_CHOICES,
        verbose_name=_('Position')
    )
    
    vote_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Vote Timestamp')
    )
    
    class Meta:
        verbose_name = _('Election Vote')
        verbose_name_plural = _('Election Votes')
        unique_together = [['election', 'voter', 'position']]
        ordering = ['election', 'position', 'vote_timestamp']
    
    def __str__(self):
        return f"{self.voter.get_display_name()} → {self.candidate.candidate.get_display_name()} ({self.get_position_display()})"


# ============================================================================
# BOARD OF AUDITORS
# ============================================================================

class BoardOfAuditors(models.Model):
    """
    Board of Auditors (Article 8).
    3-5 members, 2-year term, renewable.
    Includes founding members and former presidents automatically.
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('Board Name'),
        help_text=_('e.g., "2024-2026 Board of Auditors"')
    )
    
    term_start = models.DateField(
        verbose_name=_('Term Start')
    )
    
    term_end = models.DateField(
        verbose_name=_('Term End'),
        help_text=_('2 years from start, renewable')
    )
    
    is_renewed = models.BooleanField(
        default=False,
        verbose_name=_('Renewed Term')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Board of Auditors')
        verbose_name_plural = _('Boards of Auditors')
        ordering = ['-term_start']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-include founding members and former presidents when board is created (Article 8)."""
        created = self.pk is None
        super().save(*args, **kwargs)
        
        if created:
            # Auto-add founding members
            founding_members = Member.objects.filter(is_founding_member=True)
            for member in founding_members:
                AuditorMember.objects.get_or_create(
                    board=self,
                    user=member.user,
                    defaults={
                        'is_founding_member': True,
                    }
                )
            
            # Auto-add former presidents (from ExecutivePosition history)
            former_presidents = ExecutivePosition.objects.filter(
                position='president',
                status__in=['resigned', 'replaced'],
                end_date__isnull=False
            ).select_related('user').distinct('user')
            
            for position in former_presidents:
                if position.user:
                    AuditorMember.objects.get_or_create(
                        board=self,
                        user=position.user,
                        defaults={
                            'is_former_president': True,
                        }
                    )


class AuditorMember(models.Model):
    """
    Members of the Board of Auditors.
    """
    board = models.ForeignKey(
        BoardOfAuditors,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('Board of Auditors')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auditor_memberships',
        verbose_name=_('User')
    )
    
    is_president = models.BooleanField(
        default=False,
        verbose_name=_('President'),
        help_text=_('President of the Board of Auditors')
    )
    
    is_founding_member = models.BooleanField(
        default=False,
        verbose_name=_('Founding Member'),
        help_text=_('Automatically included as founding member')
    )
    
    is_former_president = models.BooleanField(
        default=False,
        verbose_name=_('Former President'),
        help_text=_('Automatically included as former president')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Auditor Member')
        verbose_name_plural = _('Auditor Members')
        unique_together = [['board', 'user']]
        ordering = ['board', '-is_president', 'user']
    
    def __str__(self):
        return f"{self.board} - {self.user.get_display_name()}"


class AuditReport(models.Model):
    """
    Financial audit reports (Article 18).
    Quarterly verification of financial situation.
    """
    board = models.ForeignKey(
        BoardOfAuditors,
        on_delete=models.CASCADE,
        related_name='audit_reports',
        verbose_name=_('Board of Auditors')
    )
    
    period_start = models.DateField(
        verbose_name=_('Period Start')
    )
    
    period_end = models.DateField(
        verbose_name=_('Period End')
    )
    
    report_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Report Date')
    )
    
    findings = models.TextField(
        verbose_name=_('Findings')
    )
    
    recommendations = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Recommendations')
    )
    
    financial_verification_status = models.CharField(
        max_length=50,
        default='pending',
        verbose_name=_('Financial Verification Status'),
        help_text=_('e.g., "Verified", "Issues Found", "Pending Review"')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Audit Report')
        verbose_name_plural = _('Audit Reports')
        ordering = ['-report_date', '-period_end']
    
    def __str__(self):
        return f"Audit Report - {self.period_start} to {self.period_end}"


# ============================================================================
# DISCIPLINARY SYSTEM
# ============================================================================

class DisciplinaryCase(models.Model):
    """
    Disciplinary cases (Article 27, 28).
    """
    VIOLATION_TYPE_CHOICES = [
        ('forum_confusion', _('Confusion in Forums/Social Networks/Debates')),
        ('public_insult', _('Public Insult')),
        ('assault_battery', _('Intentional Assault and Battery')),
        ('non_compliance', _('Non-compliance with Statutes and Rules')),
        ('indiscipline', _('General Indiscipline')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('under_review', _('Under Review')),
        ('resolved', _('Resolved')),
        ('dismissed', _('Dismissed')),
    ]
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='disciplinary_cases',
        verbose_name=_('Member')
    )
    
    violation_type = models.CharField(
        max_length=30,
        choices=VIOLATION_TYPE_CHOICES,
        verbose_name=_('Violation Type')
    )
    
    description = models.TextField(
        verbose_name=_('Description')
    )
    
    evidence = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Evidence'),
        help_text=_('Links, screenshots, or other evidence')
    )
    
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_cases',
        verbose_name=_('Reported By')
    )
    
    reported_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Reported Date')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Disciplinary Case')
        verbose_name_plural = _('Disciplinary Cases')
        ordering = ['-reported_date', '-created_at']
    
    def __str__(self):
        return f"{self.member} - {self.get_violation_type_display()} ({self.get_status_display()})"


class DisciplinarySanction(models.Model):
    """
    Disciplinary sanctions (Article 28, 29).
    Scale: Request for explanation → Warning → Blame → Exclusion
    """
    SANCTION_TYPE_CHOICES = [
        ('request_explanation', _('Request for Explanation')),
        ('warning', _('Warning')),
        ('blame', _('Blame')),
        ('exclusion', _('Exclusion')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('appealed', _('Appealed')),
        ('resolved', _('Resolved')),
        ('expired', _('Expired')),
    ]
    
    case = models.ForeignKey(
        DisciplinaryCase,
        on_delete=models.CASCADE,
        related_name='sanctions',
        verbose_name=_('Disciplinary Case')
    )
    
    sanction_type = models.CharField(
        max_length=30,
        choices=SANCTION_TYPE_CHOICES,
        verbose_name=_('Sanction Type')
    )
    
    applied_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Applied Date')
    )
    
    applied_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='applied_sanctions',
        verbose_name=_('Applied By'),
        help_text=_('Executive Board')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Expiration Date'),
        help_text=_('For temporary sanctions')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Disciplinary Sanction')
        verbose_name_plural = _('Disciplinary Sanctions')
        ordering = ['-applied_date', '-created_at']
    
    def __str__(self):
        return f"{self.case.member} - {self.get_sanction_type_display()} ({self.applied_date})"


# ============================================================================
# EVENTS & ACTIVITIES COORDINATION
# ============================================================================

class AssociationEvent(models.Model):
    """
    Events organized by ASCAI (Article 37, 38, 42).
    """
    EVENT_TYPE_CHOICES = [
        ('cultural', _('Cultural')),
        ('educational', _('Educational')),
        ('social', _('Social')),
        ('national_day_feb11', _('National Day - February 11')),
        ('national_day_may20', _('National Day - May 20')),
        ('march8', _('March 8 - Women\'s Day')),
        ('december31', _('December 31')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        verbose_name=_('Event Type')
    )
    
    description = models.TextField(
        verbose_name=_('Description')
    )
    
    start_date = models.DateTimeField(
        verbose_name=_('Start Date')
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('End Date')
    )
    
    location = models.CharField(
        max_length=200,
        verbose_name=_('Location')
    )
    
    # Financial tracking
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Budget')
    )
    
    revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name=_('Revenue')
    )
    
    expenses = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name=_('Expenses')
    )
    
    # Link to diaspora Event if exists
    diaspora_event = models.ForeignKey(
        'diaspora.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='association_events',
        verbose_name=_('Diaspora Event')
    )
    
    report = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Post-Event Report'),
        help_text=_('Required after each event')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Association Event')
        verbose_name_plural = _('Association Events')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('governance:event_detail', kwargs={'pk': self.pk})


class EventOrganizingCommittee(models.Model):
    """
    Organizing committee for association events (Article 37).
    Executive Board + additional members.
    """
    event = models.ForeignKey(
        AssociationEvent,
        on_delete=models.CASCADE,
        related_name='organizing_committees',
        verbose_name=_('Event')
    )
    
    members = models.ManyToManyField(
        User,
        related_name='event_committees',
        verbose_name=_('Committee Members')
    )
    
    role = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Role/Responsibility')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Event Organizing Committee')
        verbose_name_plural = _('Event Organizing Committees')
    
    def __str__(self):
        return f"{self.event} - Organizing Committee"


# ============================================================================
# COMMUNICATION & DOCUMENTATION
# ============================================================================

class AssociationDocument(models.Model):
    """
    Official association documents (Article 25, 46, 47).
    Statutes, Rules of Procedure, Minutes, Reports, etc.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('statute', _('Statute')),
        ('rules_of_procedure', _('Rules of Procedure')),
        ('minutes', _('Minutes')),
        ('report', _('Report')),
        ('financial_report', _('Financial Report')),
        ('audit_report', _('Audit Report')),
        ('other', _('Other')),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name=_('Document Type')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Version')
    )
    
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    
    file = models.FileField(
        upload_to='governance/documents/%Y/%m/',
        verbose_name=_('File')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    
    publication_date = models.DateField(
        default=timezone.now,
        verbose_name=_('Publication Date')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether this is the current active version')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Association Document')
        verbose_name_plural = _('Association Documents')
        ordering = ['-publication_date', 'document_type']
    
    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"


class Communication(models.Model):
    """
    Official communications (Article 19).
    Published by Communication Manager on WhatsApp forum and social networks.
    """
    COMMUNICATION_TYPE_CHOICES = [
        ('announcement', _('Announcement')),
        ('notice', _('Notice')),
        ('report', _('Report')),
        ('other', _('Other')),
    ]
    
    TARGET_AUDIENCE_CHOICES = [
        ('all_members', _('All Members')),
        ('active_members', _('Active Members')),
        ('executive_board', _('Executive Board')),
        ('general_assembly', _('General Assembly')),
        ('public', _('Public')),
    ]
    
    PUBLICATION_CHANNEL_CHOICES = [
        ('whatsapp_forum', _('WhatsApp Forum')),
        ('social_networks', _('Social Networks')),
        ('both', _('Both')),
        ('internal', _('Internal Only')),
    ]
    
    communication_type = models.CharField(
        max_length=20,
        choices=COMMUNICATION_TYPE_CHOICES,
        verbose_name=_('Communication Type')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    content = models.TextField(
        verbose_name=_('Content')
    )
    
    target_audience = models.CharField(
        max_length=30,
        choices=TARGET_AUDIENCE_CHOICES,
        default='all_members',
        verbose_name=_('Target Audience')
    )
    
    publication_channels = models.CharField(
        max_length=20,
        choices=PUBLICATION_CHANNEL_CHOICES,
        default='both',
        verbose_name=_('Publication Channels')
    )
    
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='published_communications',
        verbose_name=_('Published By'),
        help_text=_('Communication and Culture Manager')
    )
    
    publication_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Publication Date')
    )
    
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Published'),
        help_text=_('Whether this has been published')
    )
    
    requires_president_approval = models.BooleanField(
        default=True,
        verbose_name=_('Requires President Approval'),
        help_text=_('As per Article 19')
    )
    
    president_approved = models.BooleanField(
        default=False,
        verbose_name=_('President Approved')
    )
    
    president_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_communications',
        verbose_name=_('Approved By')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Communication')
        verbose_name_plural = _('Communications')
        ordering = ['-publication_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_communication_type_display()}"
    
    def get_absolute_url(self):
        return reverse('governance:communication_detail', kwargs={'pk': self.pk})

