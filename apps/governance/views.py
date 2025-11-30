"""
Views for governance app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

from .mixins import (
    GovernanceRequiredMixin, ExecutiveBoardRequiredMixin,
    AssemblyManagementRequiredMixin, FinancialManagementRequiredMixin,
    ExpenseApprovalRequiredMixin
)
from .models import (
    Member, MembershipStatus, ExecutiveBoard, ExecutivePosition, BoardMeeting,
    GeneralAssembly, AgendaItem, AssemblyAttendance, AssemblyVote,
    FinancialTransaction, MembershipDues, Contribution, FinancialReport, ExpenseApproval,
    ElectoralCommission, Election, Candidacy, ElectionVote,
    BoardOfAuditors, AuditReport,
    DisciplinaryCase, DisciplinarySanction,
    AssociationEvent, EventOrganizingCommittee,
    AssociationDocument, Communication,
)
from .forms import (
    MemberForm, GeneralAssemblyForm, AgendaItemForm, AssemblyAttendanceForm,
    AssemblyVoteForm, FinancialTransactionForm, MembershipDuesForm, ContributionForm,
    ExecutiveBoardForm, ExecutivePositionForm, BoardMeetingForm,
    ElectionForm, CandidacyForm, CommunicationForm, AssociationEventForm,
)


# ============================================================================
# MEMBERSHIP VIEWS
# ============================================================================

class MemberListView(GovernanceRequiredMixin, ListView):
    """Member directory."""
    model = Member
    template_name = 'governance/members/list.html'
    context_object_name = 'members'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Member.objects.select_related('user').all()
        
        # Filtering
        member_type = self.request.GET.get('member_type')
        if member_type:
            queryset = queryset.filter(member_type=member_type)
        
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active_member=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active_member=False)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__full_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_types'] = Member.MEMBER_TYPE_CHOICES
        return context


class MemberDetailView(GovernanceRequiredMixin, DetailView):
    """Member detail view."""
    model = Member
    template_name = 'governance/members/detail.html'
    context_object_name = 'member'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.get_object()
        context['status_history'] = member.status_history.all()[:10]
        context['dues'] = member.dues.all()[:10]
        context['contributions'] = member.contributions.all()[:10]
        context['assembly_attendances'] = member.user.assembly_attendances.all()[:10]
        return context


class MemberCreateView(GovernanceRequiredMixin, CreateView):
    """Create new member."""
    model = Member
    form_class = MemberForm
    template_name = 'governance/members/form.html'
    success_url = reverse_lazy('governance:member_list')


class MemberUpdateView(GovernanceRequiredMixin, UpdateView):
    """Update member."""
    model = Member
    form_class = MemberForm
    template_name = 'governance/members/form.html'
    success_url = reverse_lazy('governance:member_list')


# ============================================================================
# EXECUTIVE BOARD VIEWS
# ============================================================================

class ExecutiveBoardListView(GovernanceRequiredMixin, ListView):
    """List executive boards."""
    model = ExecutiveBoard
    template_name = 'governance/executive_board/list.html'
    context_object_name = 'boards'
    
    def get_queryset(self):
        return ExecutiveBoard.objects.prefetch_related('positions__user').all()


class ExecutiveBoardDetailView(GovernanceRequiredMixin, DetailView):
    """Executive board detail."""
    model = ExecutiveBoard
    template_name = 'governance/executive_board/detail.html'
    context_object_name = 'board'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()
        context['positions'] = board.positions.select_related('user').all()
        context['meetings'] = board.meetings.all()[:10]
        return context


class ExecutiveBoardCreateView(ExecutiveBoardRequiredMixin, CreateView):
    """Create executive board."""
    model = ExecutiveBoard
    form_class = ExecutiveBoardForm
    template_name = 'governance/executive_board/form.html'
    success_url = reverse_lazy('governance:executive_board_list')


class ExecutivePositionCreateView(ExecutiveBoardRequiredMixin, CreateView):
    """Create executive position."""
    model = ExecutivePosition
    form_class = ExecutivePositionForm
    template_name = 'governance/executive_board/position_form.html'
    success_url = reverse_lazy('governance:executive_board_list')


class BoardMeetingCreateView(ExecutiveBoardRequiredMixin, CreateView):
    """Create board meeting."""
    model = BoardMeeting
    form_class = BoardMeetingForm
    template_name = 'governance/executive_board/meeting_form.html'
    success_url = reverse_lazy('governance:executive_board_list')


# ============================================================================
# GENERAL ASSEMBLY VIEWS
# ============================================================================

class GeneralAssemblyListView(GovernanceRequiredMixin, ListView):
    """List general assemblies."""
    model = GeneralAssembly
    template_name = 'governance/assemblies/list.html'
    context_object_name = 'assemblies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = GeneralAssembly.objects.all()
        
        assembly_type = self.request.GET.get('assembly_type')
        if assembly_type:
            queryset = queryset.filter(assembly_type=assembly_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-date')


class GeneralAssemblyDetailView(GovernanceRequiredMixin, DetailView):
    """General assembly detail."""
    model = GeneralAssembly
    template_name = 'governance/assemblies/detail.html'
    context_object_name = 'assembly'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assembly = self.get_object()
        context['agenda_items'] = assembly.agenda_items.all()
        context['attendances'] = assembly.attendances.select_related('user').all()
        context['votes'] = assembly.votes.all()
        return context


class GeneralAssemblyCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create general assembly."""
    model = GeneralAssembly
    form_class = GeneralAssemblyForm
    template_name = 'governance/assemblies/form.html'
    success_url = reverse_lazy('governance:assembly_list')
    
    def form_valid(self, form):
        """Set convocation date if not provided."""
        if not form.cleaned_data.get('convocation_date'):
            # Default to 10 days before assembly date
            assembly_date = form.cleaned_data.get('date')
            if assembly_date:
                form.instance.convocation_date = assembly_date.date() - timedelta(days=10)
        return super().form_valid(form)


class AgendaItemCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create agenda item."""
    model = AgendaItem
    form_class = AgendaItemForm
    template_name = 'governance/assemblies/agenda_item_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        assembly_id = self.request.GET.get('assembly')
        if assembly_id:
            try:
                assembly = GeneralAssembly.objects.get(pk=assembly_id)
                initial['assembly'] = assembly
                initial['proposed_by'] = self.request.user
            except GeneralAssembly.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('governance:assembly_detail', kwargs={'pk': self.object.assembly.pk})


class AssemblyAttendanceCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Record assembly attendance."""
    model = AssemblyAttendance
    form_class = AssemblyAttendanceForm
    template_name = 'governance/assemblies/attendance_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        assembly_id = self.request.GET.get('assembly')
        if assembly_id:
            try:
                assembly = GeneralAssembly.objects.get(pk=assembly_id)
                initial['assembly'] = assembly
            except GeneralAssembly.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('governance:assembly_detail', kwargs={'pk': self.object.assembly.pk})


class AssemblyVoteCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Record assembly vote."""
    model = AssemblyVote
    form_class = AssemblyVoteForm
    template_name = 'governance/assemblies/vote_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        assembly_id = self.request.GET.get('assembly')
        if assembly_id:
            try:
                assembly = GeneralAssembly.objects.get(pk=assembly_id)
                initial['assembly'] = assembly
            except GeneralAssembly.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('governance:assembly_detail', kwargs={'pk': self.object.assembly.pk})


# ============================================================================
# FINANCIAL VIEWS
# ============================================================================

class FinancialTransactionListView(FinancialManagementRequiredMixin, ListView):
    """List financial transactions."""
    model = FinancialTransaction
    template_name = 'governance/finances/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = FinancialTransaction.objects.select_related('created_by').all()
        
        transaction_type = self.request.GET.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate totals
        transactions = self.get_queryset()
        context['total_income'] = transactions.filter(transaction_type='income').aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        context['total_expenses'] = transactions.filter(transaction_type='expense').aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        return context


class FinancialTransactionCreateView(FinancialManagementRequiredMixin, CreateView):
    """Create financial transaction."""
    model = FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = 'governance/finances/transaction_form.html'
    success_url = reverse_lazy('governance:financial_transactions')


class MembershipDuesListView(FinancialManagementRequiredMixin, ListView):
    """List membership dues."""
    model = MembershipDues
    template_name = 'governance/finances/dues.html'
    context_object_name = 'dues'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = MembershipDues.objects.select_related('member__user').all()
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('-year', '-due_date')


class MembershipDuesCreateView(FinancialManagementRequiredMixin, CreateView):
    """Create membership dues record."""
    model = MembershipDues
    form_class = MembershipDuesForm
    template_name = 'governance/finances/dues_form.html'
    success_url = reverse_lazy('governance:membership_dues')


class ExpenseApprovalView(ExpenseApprovalRequiredMixin, DetailView):
    """Expense approval view."""
    model = FinancialTransaction
    template_name = 'governance/finances/expense_approval.html'
    context_object_name = 'transaction'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()
        approvals = transaction.approvals.select_related('signer').all()
        context['approvals'] = approvals
        context['signed_count'] = approvals.filter(status='signed').count()
        context['required_signatures'] = 3
        return context


@login_required
def approve_expense(request, pk):
    """Approve expense (sign)."""
    transaction = get_object_or_404(FinancialTransaction, pk=pk)
    
    if transaction.transaction_type != 'expense':
        messages.error(request, _('This is not an expense transaction.'))
        return redirect('governance:financial_transactions')
    
    # Check if user has permission
    if not request.user.has_perm('governance.approve_expense'):
        messages.error(request, _('You do not have permission to approve expenses.'))
        return redirect('governance:financial_transactions')
    
    # Get or create approval
    approval, created = ExpenseApproval.objects.get_or_create(
        transaction=transaction,
        signer=request.user,
        defaults={'status': 'pending'}
    )
    
    if approval.status == 'signed':
        messages.info(request, _('You have already signed this expense.'))
    else:
        approval.status = 'signed'
        approval.signature_date = timezone.now()
        approval.save()
        messages.success(request, _('Expense approved successfully.'))
    
    return redirect('governance:expense_approval', pk=pk)


# ============================================================================
# DASHBOARD VIEWS
# ============================================================================

class GovernanceDashboardView(GovernanceRequiredMixin, TemplateView):
    """Main governance dashboard."""
    template_name = 'governance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Statistics
        context['stats'] = {
            'total_members': Member.objects.count(),
            'active_members': Member.objects.filter(is_active_member=True).count(),
            'current_board': ExecutiveBoard.objects.filter(status='active').first(),
            'upcoming_assemblies': GeneralAssembly.objects.filter(
                status='scheduled',
                date__gte=timezone.now()
            ).count(),
            'pending_dues': MembershipDues.objects.filter(status='pending').count(),
            'pending_expenses': FinancialTransaction.objects.filter(
                transaction_type='expense',
                status='pending'
            ).count(),
        }
        
        # Recent activity
        context['recent_assemblies'] = GeneralAssembly.objects.all()[:5]
        context['recent_transactions'] = FinancialTransaction.objects.all()[:10]
        
        return context

