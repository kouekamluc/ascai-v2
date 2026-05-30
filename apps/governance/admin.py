"""
Admin configuration for governance app.
"""
from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin, TabularInline
from .forms import ExecutivePositionForm
from .models import (
    Member, MembershipStatus,
    ExecutiveBoard, ExecutivePosition, BoardMeeting,
    GeneralAssembly, ExtraordinaryAssemblyRequest, AgendaItem, AssemblyAttendance, AssemblyVote,
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
class MemberAdmin(BaseAdmin):
    list_display = ['user', 'member_type', 'verification_badge', 'is_active_member', 'lazio_residence_verified',
                    'cameroonian_origin_verified', 'registration_date']
    list_filter = ['member_type', 'is_active_member', 'lazio_residence_verified', 
                   'cameroonian_origin_verified', 'registration_date']
    search_fields = ['user__username', 'user__email', 'user__full_name']
    search_help_text = _('Search members by username, email, or full name.')
    readonly_fields = ['registration_date', 'created_at', 'updated_at']
    autocomplete_fields = ['user']
    list_per_page = 25
    actions = ['verify_eligibility', 'activate_members', 'deactivate_members']
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

    def verification_badge(self, obj):
        if obj.lazio_residence_verified and obj.cameroonian_origin_verified:
            return format_html(
                '<span style="background:#166534;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">VERIFIED</span>'
            )
        return format_html(
            '<span style="background:#b91c1c;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">CHECK ELIGIBILITY</span>'
        )
    verification_badge.short_description = _('Eligibility')
    verification_badge.admin_order_field = 'lazio_residence_verified'

    def verify_eligibility(self, request, queryset):
        updated = queryset.update(lazio_residence_verified=True, cameroonian_origin_verified=True)
        self.message_user(request, _('{} member(s) marked eligibility verified.').format(updated))
    verify_eligibility.short_description = _('Verify Lazio residence and Cameroonian origin')

    def activate_members(self, request, queryset):
        updated = queryset.update(is_active_member=True, membership_start_date=timezone.now().date())
        self.message_user(request, _('{} member(s) activated.').format(updated))
    activate_members.short_description = _('Activate selected members')

    def deactivate_members(self, request, queryset):
        updated = queryset.update(is_active_member=False, membership_end_date=timezone.now().date())
        self.message_user(request, _('{} member(s) deactivated.').format(updated))
    deactivate_members.short_description = _('Deactivate selected members')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending_count = Member.objects.filter(
            Q(lazio_residence_verified=False) | Q(cameroonian_origin_verified=False)
        ).count()
        if pending_count:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('{} member(s) need eligibility review').format(pending_count)
        return super().changelist_view(request, extra_context)


@admin.register(MembershipStatus)
class MembershipStatusAdmin(ModelAdmin):
    list_display = ['member', 'status', 'effective_date', 'last_payment_date']
    list_filter = ['status', 'effective_date']
    search_fields = ['member__user__username', 'member__user__email']
    autocomplete_fields = ['member']
    list_per_page = 25
    readonly_fields = ['created_at']
    date_hierarchy = 'effective_date'


# ============================================================================
# EXECUTIVE BOARD ADMIN
# ============================================================================

class ExecutivePositionInline(TabularInline):
    model = ExecutivePosition
    form = ExecutivePositionForm
    extra = 0
    fields = ['position', 'user', 'start_date', 'end_date', 'status']


@admin.register(ExecutiveBoard)
class ExecutiveBoardAdmin(BaseAdmin):
    list_display = ['__str__', 'term_start_date', 'term_end_date', 'is_renewed', 'status']
    list_filter = ['status', 'is_renewed', 'term_start_date']
    search_fields = ['notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ExecutivePositionInline]
    date_hierarchy = 'term_start_date'
    list_per_page = 20


@admin.register(ExecutivePosition)
class ExecutivePositionAdmin(ModelAdmin):
    form = ExecutivePositionForm
    list_display = ['board', 'position_label', 'user', 'start_date', 'status']
    list_filter = ['status', 'board']
    search_fields = ['position', 'user__username', 'user__email', 'user__full_name']
    search_help_text = _('Search by role title or board member name.')
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['board', 'user']
    list_per_page = 25

    def position_label(self, obj):
        return obj.get_position_display()
    position_label.short_description = _('Position')


@admin.register(BoardMeeting)
class BoardMeetingAdmin(BaseAdmin):
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
class GeneralAssemblyAdmin(BaseAdmin):
    list_display = ['__str__', 'assembly_type', 'date', 'location', 'status', 'convocation_date']
    list_filter = ['assembly_type', 'status', 'date']
    search_fields = ['location', 'minutes_en', 'minutes_fr', 'minutes_it']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AgendaItemInline]
    date_hierarchy = 'date'
    list_per_page = 20
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


@admin.register(ExtraordinaryAssemblyRequest)
class ExtraordinaryAssemblyRequestAdmin(ModelAdmin):
    list_display = ['member', 'status', 'requested_at', 'updated_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['member__user__username', 'member__user__email', 'member__user__full_name', 'reason']
    autocomplete_fields = ['member']
    readonly_fields = ['requested_at', 'updated_at']
    actions = ['mark_withdrawn', 'mark_converted']

    def mark_withdrawn(self, request, queryset):
        updated = queryset.update(status='withdrawn')
        self.message_user(request, _('{} request(s) marked withdrawn.').format(updated))
    mark_withdrawn.short_description = _('Mark selected requests withdrawn')

    def mark_converted(self, request, queryset):
        updated = queryset.update(status='converted')
        self.message_user(request, _('{} request(s) marked converted.').format(updated))
    mark_converted.short_description = _('Mark selected requests converted to assembly')


@admin.register(AgendaItem)
class AgendaItemAdmin(BaseAdmin):
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
class AssemblyVoteAdmin(BaseAdmin):
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
class FinancialTransactionAdmin(BaseAdmin):
    list_display = ['__str__', 'transaction_type', 'category', 'amount', 'date', 'status']
    list_filter = ['transaction_type', 'category', 'status', 'date']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ExpenseApprovalInline]
    date_hierarchy = 'date'


@admin.register(MembershipDues)
class MembershipDuesAdmin(ModelAdmin):
    list_display = ['member', 'year', 'amount', 'due_date', 'payment_date', 'status', 'valid_from', 'valid_until']
    list_filter = ['status', 'year', 'payment_method']
    search_fields = ['member__user__username', 'member__user__email']
    date_hierarchy = 'due_date'
    readonly_fields = ['valid_from', 'valid_until']
    autocomplete_fields = ['member']
    list_per_page = 30


@admin.register(Contribution)
class ContributionAdmin(BaseAdmin):
    list_display = ['member', 'contribution_type', 'amount', 'date']
    list_filter = ['contribution_type', 'date']
    search_fields = ['member__user__username', 'purpose']
    date_hierarchy = 'date'


@admin.register(FinancialReport)
class FinancialReportAdmin(BaseAdmin):
    list_display = ['__str__', 'report_type', 'period_start', 'period_end', 
                    'total_income', 'total_expenses', 'balance', 'verified_by']
    list_filter = ['report_type', 'period_start', 'period_end']
    search_fields = ['report_content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_end'
    autocomplete_fields = ['generated_by', 'verified_by']
    list_per_page = 20


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
class ElectoralCommissionAdmin(BaseAdmin):
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
    autocomplete_fields = ['commission', 'user']
    list_per_page = 25


@admin.register(Election)
class ElectionAdmin(BaseAdmin):
    list_display = ['__str__', 'election_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'election_type', 'start_date']
    search_fields = ['notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled']

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, _('{} election(s) marked in progress.').format(updated))
    mark_in_progress.short_description = _('Mark selected elections in progress')

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, _('{} election(s) completed.').format(updated))
    mark_completed.short_description = _('Mark selected elections completed')

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, _('{} election(s) cancelled.').format(updated))
    mark_cancelled.short_description = _('Cancel selected elections')


@admin.register(Candidacy)
class CandidacyAdmin(BaseAdmin):
    list_display = ['candidate', 'election', 'position', 'status_badge',
                    'seniority_verified', 'lazio_residence_verified', 'cameroonian_origin_verified']
    list_filter = ['position', 'status', 'election', 'seniority_verified', 
                   'lazio_residence_verified', 'cameroonian_origin_verified']
    search_fields = ['candidate__username', 'candidate__email', 'eligibility_notes']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['candidate', 'election']
    list_per_page = 25
    actions = ['verify_eligibility', 'approve_candidacies', 'reject_candidacies']

    def status_badge(self, obj):
        colors = {
            'approved': '#166534',
            'rejected': '#b91c1c',
            'withdrawn': '#6b7280',
            'pending': '#b45309',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">{}</span>',
            colors.get(obj.status, '#374151'),
            obj.get_status_display().upper(),
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def verify_eligibility(self, request, queryset):
        updated = queryset.update(
            seniority_verified=True,
            lazio_residence_verified=True,
            cameroonian_origin_verified=True,
        )
        self.message_user(request, _('{} candidacy record(s) marked eligible.').format(updated))
    verify_eligibility.short_description = _('Verify selected candidacy eligibility')

    def approve_candidacies(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, _('{} candidacy record(s) approved.').format(updated))
    approve_candidacies.short_description = _('Approve selected candidacies')

    def reject_candidacies(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, _('{} candidacy record(s) rejected.').format(updated))
    reject_candidacies.short_description = _('Reject selected candidacies')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending_count = Candidacy.objects.filter(status='pending').count()
        if pending_count:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('{} candidacy record(s) need review').format(pending_count)
        return super().changelist_view(request, extra_context)


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
class BoardOfAuditorsAdmin(BaseAdmin):
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
    autocomplete_fields = ['board', 'user']
    list_per_page = 25


@admin.register(AuditReport)
class AuditReportAdmin(BaseAdmin):
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
class DisciplinaryCaseAdmin(BaseAdmin):
    list_display = ['member', 'violation_type', 'reported_by', 'reported_date', 'status']
    list_filter = ['violation_type', 'status', 'reported_date']
    search_fields = ['description', 'evidence', 'member__user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DisciplinarySanctionInline]
    date_hierarchy = 'reported_date'
    autocomplete_fields = ['member', 'reported_by']
    list_per_page = 25


@admin.register(DisciplinarySanction)
class DisciplinarySanctionAdmin(BaseAdmin):
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
class AssociationEventAdmin(BaseAdmin):
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
class AssociationDocumentAdmin(BaseAdmin):
    list_display = ['title', 'document_type', 'language', 'version', 'publication_date', 'is_active']
    list_filter = ['document_type', 'language', 'is_active', 'publication_date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'
    list_per_page = 20


@admin.register(Communication)
class CommunicationAdmin(BaseAdmin):
    list_display = ['title', 'communication_type', 'target_audience', 
                    'publication_channels', 'is_published', 'president_approved', 'publication_date']
    list_filter = ['communication_type', 'target_audience', 'publication_channels', 
                   'is_published', 'president_approved', 'publication_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'
    autocomplete_fields = ['published_by', 'president_approved_by']
    list_per_page = 20

