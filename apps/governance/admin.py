"""
Admin configuration for governance app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    Member, MembershipStatus,
    ExecutiveBoard, ExecutivePosition, BoardMeeting,
    GeneralAssembly, AgendaItem, AssemblyAttendance, AssemblyVote,
    FinancialTransaction, MembershipDues, Contribution, FinancialReport, ExpenseApproval,
    ElectoralCommission, CommissionMember, Election, Candidacy, ElectionVote,
    BoardOfAuditors, AuditorMember, AuditReport,
    DisciplinaryCase, DisciplinarySanction,
    AssociationEvent, EventOrganizingCommittee,
    AssociationDocument, Communication,
)


# ============================================================================
# MEMBERSHIP ADMIN
# ============================================================================

@admin.register(Member)
class MemberAdmin(ModelAdmin):
    list_display = ['user', 'member_type', 'is_active_member', 'lazio_residence_verified', 
                    'cameroonian_origin_verified', 'registration_date']
    list_filter = ['member_type', 'is_active_member', 'lazio_residence_verified', 
                   'cameroonian_origin_verified', 'registration_date']
    search_fields = ['user__username', 'user__email', 'user__full_name']
    readonly_fields = ['registration_date', 'created_at', 'updated_at']
    fieldsets = (
        (_('Member Information'), {
            'fields': ('user', 'member_type', 'is_active_member')
        }),
        (_('Verification'), {
            'fields': ('lazio_residence_verified', 'cameroonian_origin_verified')
        }),
        (_('Dates'), {
            'fields': ('registration_date', 'membership_start_date', 'membership_end_date', 'last_assembly_attendance')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MembershipStatus)
class MembershipStatusAdmin(ModelAdmin):
    list_display = ['member', 'status', 'effective_date', 'last_payment_date']
    list_filter = ['status', 'effective_date']
    search_fields = ['member__user__username', 'member__user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'effective_date'


# ============================================================================
# EXECUTIVE BOARD ADMIN
# ============================================================================

class ExecutivePositionInline(TabularInline):
    model = ExecutivePosition
    extra = 0
    fields = ['position', 'user', 'start_date', 'end_date', 'status']


@admin.register(ExecutiveBoard)
class ExecutiveBoardAdmin(ModelAdmin):
    list_display = ['__str__', 'term_start_date', 'term_end_date', 'is_renewed', 'status']
    list_filter = ['status', 'is_renewed', 'term_start_date']
    search_fields = ['notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ExecutivePositionInline]
    date_hierarchy = 'term_start_date'


@admin.register(ExecutivePosition)
class ExecutivePositionAdmin(ModelAdmin):
    list_display = ['board', 'position', 'user', 'start_date', 'status']
    list_filter = ['position', 'status', 'board']
    search_fields = ['user__username', 'user__email', 'user__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BoardMeeting)
class BoardMeetingAdmin(ModelAdmin):
    list_display = ['board', 'meeting_date', 'location']
    list_filter = ['board', 'meeting_date']
    search_fields = ['agenda', 'minutes', 'decisions']
    filter_horizontal = ['attendees']
    date_hierarchy = 'meeting_date'


# ============================================================================
# GENERAL ASSEMBLY ADMIN
# ============================================================================

class AgendaItemInline(TabularInline):
    model = AgendaItem
    extra = 0
    fields = ['title', 'item_type', 'proposed_by', 'status', 'order']


@admin.register(GeneralAssembly)
class GeneralAssemblyAdmin(ModelAdmin):
    list_display = ['__str__', 'assembly_type', 'date', 'location', 'status', 'convocation_date']
    list_filter = ['assembly_type', 'status', 'date']
    search_fields = ['location', 'minutes_en', 'minutes_fr', 'minutes_it']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AgendaItemInline]
    date_hierarchy = 'date'
    fieldsets = (
        (_('Assembly Information'), {
            'fields': ('assembly_type', 'date', 'location', 'convocation_date', 'status')
        }),
        (_('Minutes (English)'), {
            'fields': ('minutes_en',)
        }),
        (_('Minutes (Français)'), {
            'fields': ('minutes_fr',)
        }),
        (_('Minutes (Italiano)'), {
            'fields': ('minutes_it',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AgendaItem)
class AgendaItemAdmin(ModelAdmin):
    list_display = ['assembly', 'title', 'item_type', 'proposed_by', 'status', 'order']
    list_filter = ['item_type', 'status', 'assembly']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AssemblyAttendance)
class AssemblyAttendanceAdmin(ModelAdmin):
    list_display = ['assembly', 'user', 'attendee_type', 'attended']
    list_filter = ['attendee_type', 'attended', 'assembly']
    search_fields = ['user__username', 'attendee_name']


@admin.register(AssemblyVote)
class AssemblyVoteAdmin(ModelAdmin):
    list_display = ['assembly', 'vote_type', 'voting_method', 'votes_yes', 'votes_no', 
                    'votes_abstain', 'is_published']
    list_filter = ['vote_type', 'voting_method', 'is_published', 'assembly']
    search_fields = ['question', 'result']
    readonly_fields = ['created_at', 'updated_at']


# ============================================================================
# FINANCIAL ADMIN
# ============================================================================

class ExpenseApprovalInline(TabularInline):
    model = ExpenseApproval
    extra = 0
    fields = ['signer', 'status', 'signature_date', 'notes']
    readonly_fields = ['signature_date']


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(ModelAdmin):
    list_display = ['__str__', 'transaction_type', 'category', 'amount', 'date', 'status']
    list_filter = ['transaction_type', 'category', 'status', 'date']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ExpenseApprovalInline]
    date_hierarchy = 'date'


@admin.register(MembershipDues)
class MembershipDuesAdmin(ModelAdmin):
    list_display = ['member', 'year', 'amount', 'due_date', 'payment_date', 'status']
    list_filter = ['status', 'year', 'payment_method']
    search_fields = ['member__user__username', 'member__user__email']
    date_hierarchy = 'due_date'


@admin.register(Contribution)
class ContributionAdmin(ModelAdmin):
    list_display = ['member', 'contribution_type', 'amount', 'date']
    list_filter = ['contribution_type', 'date']
    search_fields = ['member__user__username', 'purpose']
    date_hierarchy = 'date'


@admin.register(FinancialReport)
class FinancialReportAdmin(ModelAdmin):
    list_display = ['__str__', 'report_type', 'period_start', 'period_end', 
                    'total_income', 'total_expenses', 'balance', 'verified_by']
    list_filter = ['report_type', 'period_start', 'period_end']
    search_fields = ['report_content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_end'


@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(ModelAdmin):
    list_display = ['transaction', 'signer', 'status', 'signature_date']
    list_filter = ['status', 'signature_date']
    search_fields = ['transaction__description', 'signer__username']


# ============================================================================
# ELECTORAL SYSTEM ADMIN
# ============================================================================

class CommissionMemberInline(TabularInline):
    model = CommissionMember
    extra = 0
    fields = ['user', 'role']


@admin.register(ElectoralCommission)
class ElectoralCommissionAdmin(ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommissionMemberInline]
    date_hierarchy = 'start_date'


@admin.register(CommissionMember)
class CommissionMemberAdmin(ModelAdmin):
    list_display = ['commission', 'user', 'role']
    list_filter = ['role', 'commission']
    search_fields = ['user__username', 'user__email']


@admin.register(Election)
class ElectionAdmin(ModelAdmin):
    list_display = ['__str__', 'election_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'election_type', 'start_date']
    search_fields = ['notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(Candidacy)
class CandidacyAdmin(ModelAdmin):
    list_display = ['candidate', 'election', 'position', 'status', 
                    'seniority_verified', 'lazio_residence_verified', 'cameroonian_origin_verified']
    list_filter = ['position', 'status', 'election', 'seniority_verified', 
                   'lazio_residence_verified', 'cameroonian_origin_verified']
    search_fields = ['candidate__username', 'candidate__email', 'eligibility_notes']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ElectionVote)
class ElectionVoteAdmin(ModelAdmin):
    list_display = ['election', 'voter', 'candidate', 'position', 'vote_timestamp']
    list_filter = ['election', 'position', 'vote_timestamp']
    search_fields = ['voter__username', 'candidate__candidate__username']
    readonly_fields = ['vote_timestamp']
    date_hierarchy = 'vote_timestamp'


# ============================================================================
# BOARD OF AUDITORS ADMIN
# ============================================================================

class AuditorMemberInline(TabularInline):
    model = AuditorMember
    extra = 0
    fields = ['user', 'is_president', 'is_founding_member', 'is_former_president']


@admin.register(BoardOfAuditors)
class BoardOfAuditorsAdmin(ModelAdmin):
    list_display = ['name', 'term_start', 'term_end', 'is_renewed', 'status']
    list_filter = ['status', 'is_renewed', 'term_start']
    search_fields = ['name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AuditorMemberInline]
    date_hierarchy = 'term_start'


@admin.register(AuditorMember)
class AuditorMemberAdmin(ModelAdmin):
    list_display = ['board', 'user', 'is_president', 'is_founding_member', 'is_former_president']
    list_filter = ['is_president', 'is_founding_member', 'is_former_president', 'board']
    search_fields = ['user__username', 'user__email']


@admin.register(AuditReport)
class AuditReportAdmin(ModelAdmin):
    list_display = ['__str__', 'board', 'period_start', 'period_end', 
                    'report_date', 'financial_verification_status']
    list_filter = ['financial_verification_status', 'report_date', 'board']
    search_fields = ['findings', 'recommendations']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'report_date'


# ============================================================================
# DISCIPLINARY SYSTEM ADMIN
# ============================================================================

class DisciplinarySanctionInline(TabularInline):
    model = DisciplinarySanction
    extra = 0
    fields = ['sanction_type', 'applied_date', 'applied_by', 'status', 'expiration_date']


@admin.register(DisciplinaryCase)
class DisciplinaryCaseAdmin(ModelAdmin):
    list_display = ['member', 'violation_type', 'reported_by', 'reported_date', 'status']
    list_filter = ['violation_type', 'status', 'reported_date']
    search_fields = ['description', 'evidence', 'member__user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DisciplinarySanctionInline]
    date_hierarchy = 'reported_date'


@admin.register(DisciplinarySanction)
class DisciplinarySanctionAdmin(ModelAdmin):
    list_display = ['case', 'sanction_type', 'applied_date', 'applied_by', 'status']
    list_filter = ['sanction_type', 'status', 'applied_date']
    search_fields = ['case__member__user__username', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'applied_date'


# ============================================================================
# EVENTS ADMIN
# ============================================================================

class EventOrganizingCommitteeInline(TabularInline):
    model = EventOrganizingCommittee
    extra = 0
    filter_horizontal = ['members']


@admin.register(AssociationEvent)
class AssociationEventAdmin(ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'location', 'budget', 'revenue', 'expenses']
    list_filter = ['event_type', 'start_date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EventOrganizingCommitteeInline]
    date_hierarchy = 'start_date'


@admin.register(EventOrganizingCommittee)
class EventOrganizingCommitteeAdmin(ModelAdmin):
    list_display = ['event', 'role']
    list_filter = ['event']
    filter_horizontal = ['members']


# ============================================================================
# COMMUNICATION & DOCUMENTATION ADMIN
# ============================================================================

@admin.register(AssociationDocument)
class AssociationDocumentAdmin(ModelAdmin):
    list_display = ['title', 'document_type', 'language', 'version', 'publication_date', 'is_active']
    list_filter = ['document_type', 'language', 'is_active', 'publication_date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'


@admin.register(Communication)
class CommunicationAdmin(ModelAdmin):
    list_display = ['title', 'communication_type', 'target_audience', 
                    'publication_channels', 'is_published', 'president_approved', 'publication_date']
    list_filter = ['communication_type', 'target_audience', 'publication_channels', 
                   'is_published', 'president_approved', 'publication_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'

