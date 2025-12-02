"""
Views for governance app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django import forms

from .mixins import (
    GovernanceRequiredMixin, ExecutiveBoardRequiredMixin,
    AssemblyManagementRequiredMixin, FinancialManagementRequiredMixin,
    ExpenseApprovalRequiredMixin
)
from .models import (
    Member, MembershipStatus, ExecutiveBoard, ExecutivePosition, BoardMeeting,
    GeneralAssembly, AgendaItem, AssemblyAttendance, AssemblyVote, AssemblyVoteRecord,
    FinancialTransaction, MembershipDues, Contribution, FinancialReport, ExpenseApproval,
    ElectoralCommission, CommissionMember, Election, Candidacy, ElectionVote,
    BoardOfAuditors, AuditorMember, AuditReport,
    DisciplinaryCase, DisciplinarySanction,
    AssociationEvent, EventOrganizingCommittee,
    AssociationDocument, Communication,
    EXECUTIVE_POSITION_CHOICES,
)
from .utils import (
    calculate_assembly_vote_results, calculate_election_results,
    check_candidacy_eligibility, check_voting_eligibility,
    check_membership_loss_criteria, calculate_member_seniority,
    check_executive_board_vacancy, get_executive_board_vacancies,
    calculate_financial_summary, check_expense_approval_status,
    check_extraordinary_assembly_quorum, check_assembly_notice_period,
    check_agenda_item_proposal_deadline
)
from .forms import (
    MemberForm, MemberSelfRegistrationForm, GeneralAssemblyForm, AgendaItemForm, AssemblyAttendanceForm,
    AssemblyVoteForm, FinancialTransactionForm, MembershipDuesForm, ContributionForm,
    ExecutiveBoardForm, ExecutivePositionForm, BoardMeetingForm,
    ElectionForm, CandidacyForm, CommunicationForm, AssociationEventForm,
)


# ============================================================================
# USER-FACING MEMBER PORTAL VIEWS
# ============================================================================

class MemberPortalView(LoginRequiredMixin, TemplateView):
    """Member portal - user's personal membership dashboard."""
    template_name = 'governance/member_portal/index.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has a member profile, if not redirect to registration
        if not hasattr(request.user, 'member_profile'):
            messages.info(request, _('Please register as an ASCAI member to access the member portal.'))
            return redirect('governance:member_register')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get member profile (guaranteed to exist due to dispatch check)
        member = user.member_profile
        
        # Get current year dues
        current_year = timezone.now().year
        current_dues = MembershipDues.objects.filter(
            member=member,
            year=current_year
        ).first()
        
        # Create current year dues if it doesn't exist and member is active
        if not current_dues and member.is_active_member:
            # Determine amount based on member type
            amount = 10.00 if member.member_type == 'student' else 5.00
            current_dues = MembershipDues.objects.create(
                member=member,
                year=current_year,
                amount=amount,
                due_date=timezone.datetime(current_year, 3, 31).date(),
                status='pending'
            )
        
        # Get all dues
        all_dues = MembershipDues.objects.filter(member=member).order_by('-year')
        
        # Get upcoming assemblies
        upcoming_assemblies = GeneralAssembly.objects.filter(
            status='scheduled',
            date__gte=timezone.now()
        ).order_by('date')[:5]
        
        # Get user's assembly attendances
        attendances = AssemblyAttendance.objects.filter(
            user=user
        ).select_related('assembly').order_by('-assembly__date')[:10]
        
        # Get assemblies user can vote in
        assemblies_with_votes = GeneralAssembly.objects.filter(
            status='scheduled',
            date__gte=timezone.now()
        ).prefetch_related('agenda_items', 'votes')
        
        context.update({
            'member': member,
            'current_dues': current_dues,
            'all_dues': all_dues,
            'upcoming_assemblies': upcoming_assemblies,
            'attendances': attendances,
            'assemblies_with_votes': assemblies_with_votes,
        })
        return context


class MemberSelfRegistrationView(LoginRequiredMixin, CreateView):
    """Allow users to register themselves as ASCAI members."""
    model = Member
    form_class = MemberSelfRegistrationForm
    template_name = 'governance/member_portal/register.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user already has a member profile
        if hasattr(request.user, 'member_profile'):
            messages.info(request, _('You are already registered as a member.'))
            return redirect('governance:member_portal')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Automatically link to current user
        member = form.save(commit=False)
        member.user = self.request.user
        member.registration_date = timezone.now().date()
        member.membership_start_date = timezone.now().date()
        
        # Set default values - verification will be done by admin
        
        # Verification fields are set to False initially - admin will verify
        member.lazio_residence_verified = False
        member.cameroonian_origin_verified = False
        member.is_active_member = False  # Will be activated after verification and payment
        
        member.save()
        
        # Create initial membership status record
        MembershipStatus.objects.create(
            member=member,
            status='pending',
            notes=_('Initial registration - pending admin verification')
        )
        
        messages.success(
            self.request,
            _('Successfully registered as ASCAI member! Your membership is pending admin verification. Once verified and you pay your dues, you will have full member privileges.')
        )
        return redirect('governance:member_portal')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-fill some fields based on user data
        kwargs['initial'] = {
            'member_type': 'student',
        }
        return kwargs


class MyDuesView(LoginRequiredMixin, TemplateView):
    """User's dues management page."""
    template_name = 'governance/member_portal/my_dues.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            member = user.member_profile
        except Member.DoesNotExist:
            messages.warning(self.request, _('Please register as a member first.'))
            return redirect('governance:member_register')
        
        current_year = timezone.now().year
        dues = MembershipDues.objects.filter(member=member).order_by('-year')
        current_dues = dues.filter(year=current_year).first()
        
        # Create current year dues if it doesn't exist
        if not current_dues:
            current_dues = MembershipDues.objects.create(
                member=member,
                year=current_year,
                amount=10.00 if member.member_type == 'student' else 5.00,
                due_date=timezone.datetime(current_year, 3, 31).date(),
                status='pending'
            )
        
        context.update({
            'member': member,
            'current_dues': current_dues,
            'all_dues': dues,
        })
        return context


@login_required
def request_dues_payment(request, dues_id):
    """User requests to pay their dues (admin will mark as paid)."""
    dues = get_object_or_404(MembershipDues, pk=dues_id, member__user=request.user)
    
    if dues.status == 'paid':
        messages.info(request, _('This dues payment has already been completed.'))
        return redirect('governance:my_dues')
    
    # Update notes to indicate payment request
    if dues.notes:
        dues.notes += f"\n\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] Payment requested by user."
    else:
        dues.notes = f"[{timezone.now().strftime('%Y-%m-%d %H:%M')}] Payment requested by user."
    
    dues.status = 'pending'  # Ensure it's pending
    dues.save()
    
    messages.success(
        request,
        _('Payment request submitted! An administrator will process your payment and update your status.')
    )
    return redirect('governance:my_dues')


class AssemblyParticipationView(LoginRequiredMixin, DetailView):
    """View for users to participate in assemblies (attendance, voting)."""
    model = GeneralAssembly
    template_name = 'governance/member_portal/assembly_participate.html'
    context_object_name = 'assembly'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Check if user is a member
        try:
            member = user.member_profile
        except Member.DoesNotExist:
            context['not_member'] = True
            return context
        
        assembly = self.get_object()
        
        # Check attendance
        attendance = AssemblyAttendance.objects.filter(
            assembly=assembly,
            user=user
        ).first()
        
        # Get agenda items
        agenda_items = assembly.agenda_items.all().order_by('order')
        
        # Get votes for this assembly
        votes = assembly.votes.all()
        
        # Check which items user has voted on
        user_votes = {}
        for vote in votes:
            vote_record = AssemblyVoteRecord.objects.filter(vote=vote, voter=user).first()
            if vote_record:
                user_votes[vote.id] = vote_record.choice
        
        context.update({
            'member': member,
            'attendance': attendance,
            'agenda_items': agenda_items,
            'votes': votes,
            'user_votes': user_votes,
        })
        return context


@login_required
def register_attendance(request, assembly_id):
    """User registers their attendance at an assembly."""
    assembly = get_object_or_404(GeneralAssembly, pk=assembly_id)
    user = request.user
    
    try:
        member = user.member_profile
    except Member.DoesNotExist:
        messages.error(request, _('You must be a registered member to attend assemblies.'))
        return redirect('governance:member_register')
    
    # Check if already registered
    attendance, created = AssemblyAttendance.objects.get_or_create(
        assembly=assembly,
        user=user,
        defaults={
            'attended': True,
            'attendee_type': 'member' if member.is_active_member else 'sympathizer',
            'registration_date': timezone.now(),
        }
    )
    
    if not created:
        attendance.attended = True
        attendance.save()
        messages.info(request, _('Attendance updated.'))
    else:
        messages.success(request, _('Successfully registered attendance!'))
    
    return redirect('governance:assembly_participate', pk=assembly_id)


class MemberDirectoryView(LoginRequiredMixin, ListView):
    """Public member directory - visible to all logged-in members."""
    model = Member
    template_name = 'governance/member_portal/directory.html'
    context_object_name = 'members'
    paginate_by = 20
    
    def get_queryset(self):
        # Only show active, verified members to regular users
        queryset = Member.objects.filter(
            is_active_member=True,
            cameroonian_origin_verified=True
        ).select_related('user')
        
        # Filtering
        member_type = self.request.GET.get('member_type')
        if member_type:
            queryset = queryset.filter(member_type=member_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__full_name__icontains=search)
            )
        
        return queryset.order_by('-registration_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_types'] = Member.MEMBER_TYPE_CHOICES
        return context


@login_required
def cast_vote(request, vote_id):
    """User casts a vote on an assembly item."""
    vote = get_object_or_404(AssemblyVote, pk=vote_id)
    user = request.user
    
    # Check if user is a member
    try:
        member = user.member_profile
        if not member.is_active_member:
            messages.error(request, _('Only active members can vote.'))
            return redirect('governance:assembly_participate', pk=vote.assembly.pk)
    except Member.DoesNotExist:
        messages.error(request, _('You must be a registered member to vote.'))
        return redirect('governance:member_register')
    
    # Check if already voted
    existing_vote = AssemblyVoteRecord.objects.filter(vote=vote, voter=user).first()
    if existing_vote:
        messages.warning(request, _('You have already voted on this item.'))
        return redirect('governance:assembly_participate', pk=vote.assembly.pk)
    
    # Get vote choice from POST
    choice = request.POST.get('choice')
    if choice not in ['yes', 'no', 'abstain']:
        messages.error(request, _('Invalid vote choice.'))
        return redirect('governance:assembly_participate', pk=vote.assembly.pk)
    
    # Create vote record
    AssemblyVoteRecord.objects.create(
        vote=vote,
        voter=user,
        choice=choice
    )
    
    # Update vote counts
    if choice == 'yes':
        vote.votes_yes += 1
    elif choice == 'no':
        vote.votes_no += 1
    else:
        vote.votes_abstain += 1
    vote.save()
    
    messages.success(request, _('Vote cast successfully!'))
    return redirect('governance:assembly_participate', pk=vote.assembly.pk)


# ============================================================================
# ADMIN MEMBERSHIP VIEWS
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
    paginate_by = 10


class ExecutiveBoardDetailView(GovernanceRequiredMixin, DetailView):
    """Executive board detail."""
    model = ExecutiveBoard
    template_name = 'governance/executive_board/detail.html'
    context_object_name = 'board'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()
        context['positions'] = board.positions.all().select_related('user')
        context['meetings'] = board.meetings.all()[:10]
        
        # Check for vacancies
        context['vacancies'] = get_executive_board_vacancies(board)
        
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
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by type
        assembly_type = self.request.GET.get('assembly_type')
        if assembly_type:
            queryset = queryset.filter(assembly_type=assembly_type)
        
        return queryset.order_by('-date')


class GeneralAssemblyDetailView(GovernanceRequiredMixin, DetailView):
    """General assembly detail."""
    model = GeneralAssembly
    template_name = 'governance/assemblies/detail.html'
    context_object_name = 'assembly'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assembly = self.get_object()
        context['agenda_items'] = assembly.agenda_items.all().order_by('order')
        context['attendances'] = assembly.attendances.all().select_related('user')[:50]
        context['votes'] = assembly.votes.all()
        
        # Calculate vote results for each vote
        vote_results = {}
        for vote in context['votes']:
            vote_results[vote.id] = calculate_assembly_vote_results(vote)
        context['vote_results'] = vote_results
        
        # Check notice period compliance
        context['notice_compliance'] = check_assembly_notice_period(assembly)
        
        return context


class GeneralAssemblyCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create general assembly."""
    model = GeneralAssembly
    form_class = GeneralAssemblyForm
    template_name = 'governance/assemblies/form.html'
    success_url = reverse_lazy('governance:assembly_list')


class AgendaItemCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create agenda item."""
    model = AgendaItem
    form_class = AgendaItemForm
    template_name = 'governance/assemblies/agenda_item_form.html'
    success_url = reverse_lazy('governance:assembly_list')
    
    def get_initial(self):
        initial = super().get_initial()
        assembly_id = self.request.GET.get('assembly')
        if assembly_id:
            initial['assembly'] = assembly_id
        return initial
    
    def form_valid(self, form):
        # Set proposed_by to current user if not set
        if not form.instance.proposed_by:
            form.instance.proposed_by = self.request.user
        return super().form_valid(form)


class AssemblyAttendanceCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create assembly attendance record."""
    model = AssemblyAttendance
    form_class = AssemblyAttendanceForm
    template_name = 'governance/assemblies/attendance_form.html'
    success_url = reverse_lazy('governance:assembly_list')
    
    def get_initial(self):
        initial = super().get_initial()
        assembly_id = self.request.GET.get('assembly')
        if assembly_id:
            initial['assembly'] = assembly_id
        return initial


class AssemblyVoteCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create assembly vote."""
    model = AssemblyVote
    form_class = AssemblyVoteForm
    template_name = 'governance/assemblies/vote_form.html'
    success_url = reverse_lazy('governance:assembly_list')
    
    def get_initial(self):
        initial = super().get_initial()
        assembly_id = self.request.GET.get('assembly')
        if assembly_id:
            initial['assembly'] = assembly_id
        return initial


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
        queryset = FinancialTransaction.objects.all()
        
        # Filter by type
        transaction_type = self.request.GET.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_queryset()
        
        context['total_income'] = transactions.filter(
            transaction_type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        context['total_expenses'] = abs(transactions.filter(
            transaction_type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        
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
        queryset = MembershipDues.objects.select_related('member', 'member__user').all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by year
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('-year', '-due_date')


class MembershipDuesCreateView(FinancialManagementRequiredMixin, CreateView):
    """Create membership dues."""
    model = MembershipDues
    form_class = MembershipDuesForm
    template_name = 'governance/finances/dues_form.html'
    success_url = reverse_lazy('governance:membership_dues')


class ExpenseApprovalView(ExpenseApprovalRequiredMixin, DetailView):
    """Expense approval page (3 signatures required)."""
    model = FinancialTransaction
    template_name = 'governance/finances/expense_approval.html'
    context_object_name = 'transaction'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()
        approvals = transaction.approvals.select_related('signer').all()
        context['approvals'] = approvals
        approval_status = check_expense_approval_status(transaction)
        context['approval_status'] = approval_status
        context['signed_count'] = approval_status['signed_count']
        context['required_signatures'] = approval_status['required']
        context['is_approved'] = approval_status['is_approved']
        return context


@login_required
def approve_expense(request, pk):
    """Sign an expense approval."""
    transaction = get_object_or_404(FinancialTransaction, pk=pk)
    
    # Check if user has permission
    if not (request.user.has_perm('governance.approve_expense') or request.user.is_staff):
        messages.error(request, _('You do not have permission to approve expenses.'))
        return redirect('governance:expense_approval', pk=pk)
    
    # Check if already signed
    approval, created = ExpenseApproval.objects.get_or_create(
        transaction=transaction,
        signer=request.user,
        defaults={
            'status': 'signed',
            'signature_date': timezone.now(),
        }
    )
    
    if not created:
        if approval.status == 'signed':
            messages.warning(request, _('You have already signed this expense.'))
        else:
            approval.status = 'signed'
            approval.signature_date = timezone.now()
            approval.save()
            messages.success(request, _('Expense signed successfully!'))
    else:
        messages.success(request, _('Expense signed successfully!'))
    
    # Check if all 3 signatures are collected
    signed_count = transaction.approvals.filter(status='signed').count()
    if signed_count >= 3:
        transaction.status = 'approved'
        transaction.save()
        messages.success(request, _('Expense fully approved with all required signatures!'))
    
    return redirect('governance:expense_approval', pk=pk)


# ============================================================================
# DASHBOARD
# ============================================================================

class GovernanceDashboardView(GovernanceRequiredMixin, TemplateView):
    """Main governance dashboard."""
    template_name = 'governance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Financial summary calculations
        all_transactions = FinancialTransaction.objects.all()
        total_income = all_transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        total_expenses = all_transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        net_balance = total_income - total_expenses
        
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
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
        }
        
        # Recent activity
        context['recent_assemblies'] = GeneralAssembly.objects.all().order_by('-date')[:5]
        context['recent_transactions'] = FinancialTransaction.objects.all().order_by('-date')
        context['recent_elections'] = Election.objects.all().order_by('-start_date')[:3]
        context['pending_disciplinary_cases'] = DisciplinaryCase.objects.filter(status='pending').count()
        context['pending_audit_reports'] = AuditReport.objects.filter(financial_verification_status='pending').count()
        
        return context


# ============================================================================
# ELECTORAL SYSTEM VIEWS
# ============================================================================

class ElectoralCommissionListView(GovernanceRequiredMixin, ListView):
    """List electoral commissions."""
    model = ElectoralCommission
    template_name = 'governance/elections/commission_list.html'
    context_object_name = 'commissions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ElectoralCommission.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-start_date')


class ElectoralCommissionDetailView(GovernanceRequiredMixin, DetailView):
    """Electoral commission detail."""
    model = ElectoralCommission
    template_name = 'governance/elections/commission_detail.html'
    context_object_name = 'commission'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission = self.get_object()
        context['members'] = commission.members.all().select_related('user')
        context['elections'] = commission.elections.all()
        return context


class ElectoralCommissionCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create electoral commission."""
    model = ElectoralCommission
    fields = ['name', 'start_date', 'end_date', 'status', 'notes']
    template_name = 'governance/elections/commission_form.html'
    success_url = reverse_lazy('governance:electoral_commission_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['notes'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'})
        return form


class ElectionListView(GovernanceRequiredMixin, ListView):
    """List elections."""
    model = Election
    template_name = 'governance/elections/election_list.html'
    context_object_name = 'elections'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Election.objects.select_related('commission').all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-start_date')


class ElectionDetailView(GovernanceRequiredMixin, DetailView):
    """Election detail."""
    model = Election
    template_name = 'governance/elections/election_detail.html'
    context_object_name = 'election'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.get_object()
        context['candidacies'] = election.candidacies.all().select_related('candidate').order_by('position')
        context['votes'] = election.votes.all().select_related('voter', 'candidate')
        
        # Calculate results using utility function
        context['results'] = calculate_election_results(election)
        
        # Check if user can vote
        if self.request.user.is_authenticated:
            context['voting_eligibility'] = check_voting_eligibility(self.request.user, election=election)
        return context


class ElectionCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create election."""
    model = Election
    form_class = ElectionForm
    template_name = 'governance/elections/election_form.html'
    success_url = reverse_lazy('governance:election_list')


class CandidacyListView(GovernanceRequiredMixin, ListView):
    """List candidacies."""
    model = Candidacy
    template_name = 'governance/elections/candidacy_list.html'
    context_object_name = 'candidacies'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Candidacy.objects.select_related('election', 'candidate').all()
        election_id = self.request.GET.get('election')
        if election_id:
            queryset = queryset.filter(election_id=election_id)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-application_date')


class CandidacyCreateView(LoginRequiredMixin, CreateView):
    """User applies for candidacy."""
    model = Candidacy
    form_class = CandidacyForm
    template_name = 'governance/elections/candidacy_apply.html'
    success_url = reverse_lazy('governance:member_portal')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is a member
        if not hasattr(request.user, 'member_profile'):
            messages.error(request, _('You must be a registered member to apply for candidacy.'))
            return redirect('governance:member_register')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Check eligibility before allowing application
        eligibility = check_candidacy_eligibility(self.request.user, form.instance.position)
        
        if not eligibility['eligible']:
            for reason in eligibility['reasons']:
                messages.error(self.request, reason)
            return self.form_invalid(form)
        
        if eligibility['warnings']:
            for warning in eligibility['warnings']:
                messages.warning(self.request, warning)
        
        form.instance.candidate = self.request.user
        form.instance.application_date = timezone.now().date()
        
        # Set verification flags based on member profile
        member = self.request.user.member_profile
        form.instance.lazio_residence_verified = member.lazio_residence_verified
        form.instance.cameroonian_origin_verified = member.cameroonian_origin_verified
        
        # Calculate seniority
        seniority = calculate_member_seniority(member)
        form.instance.seniority_verified = seniority['days'] >= 365
        
        messages.success(
            self.request,
            _('Candidacy application submitted! It will be reviewed by the Electoral Commission.')
        )
        return super().form_valid(form)


@login_required
def approve_candidacy(request, candidacy_id):
    """Approve or reject a candidacy (Electoral Commission only)."""
    candidacy = get_object_or_404(Candidacy, pk=candidacy_id)
    
    if not request.user.has_perm('governance.manage_elections'):
        messages.error(request, _('You do not have permission to approve candidacies.'))
        return redirect('governance:candidacy_list')
    
    action = request.POST.get('action')
    if action == 'approve':
        candidacy.status = 'approved'
        messages.success(request, _('Candidacy approved.'))
    elif action == 'reject':
        candidacy.status = 'rejected'
        messages.success(request, _('Candidacy rejected.'))
    else:
        messages.error(request, _('Invalid action.'))
        return redirect('governance:candidacy_list')
    
    candidacy.save()
    return redirect('governance:candidacy_list')


class ElectionVoteView(LoginRequiredMixin, DetailView):
    """Vote in an election (secret ballot)."""
    model = Election
    template_name = 'governance/elections/vote.html'
    context_object_name = 'election'
    
    def dispatch(self, request, *args, **kwargs):
        election = self.get_object()
        if election.status != 'in_progress':
            messages.error(request, _('This election is not currently open for voting.'))
            return redirect('governance:election_detail', pk=election.pk)
        
        # Check if user is an active member
        try:
            member = request.user.member_profile
            if not member.is_active_member:
                messages.error(request, _('Only active members can vote in elections.'))
                return redirect('governance:member_portal')
        except Member.DoesNotExist:
            messages.error(request, _('You must be a registered member to vote.'))
            return redirect('governance:member_register')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.get_object()
        user = self.request.user
        
        # Get candidacies by position
        candidacies_by_position = {}
        for position_code, position_name in EXECUTIVE_POSITION_CHOICES:
            candidacies = election.candidacies.filter(
                position=position_code,
                status='approved'
            ).select_related('candidate')
            if candidacies.exists():
                candidacies_by_position[position_code] = {
                    'name': position_name,
                    'candidacies': candidacies,
                    'has_voted': ElectionVote.objects.filter(
                        election=election,
                        voter=user,
                        position=position_code
                    ).exists()
                }
        context['candidacies_by_position'] = candidacies_by_position
        return context


@login_required
def cast_election_vote(request, election_id):
    """Cast a vote in an election."""
    election = get_object_or_404(Election, pk=election_id, status='in_progress')
    user = request.user
    
    # Check if user is an active member
    try:
        member = user.member_profile
        if not member.is_active_member:
            messages.error(request, _('Only active members can vote in elections.'))
            return redirect('governance:election_detail', pk=election_id)
    except Member.DoesNotExist:
        messages.error(request, _('You must be a registered member to vote.'))
        return redirect('governance:member_register')
    
    # Get vote data from POST
    votes = {}
    for position_code, _ in EXECUTIVE_POSITION_CHOICES:
        candidate_id = request.POST.get(f'position_{position_code}')
        if candidate_id:
            votes[position_code] = int(candidate_id)
    
    if not votes:
        messages.error(request, _('No votes submitted.'))
        return redirect('governance:election_vote', pk=election_id)
    
    # Record votes
    for position_code, candidate_id in votes.items():
        try:
            candidacy = Candidacy.objects.get(
                pk=candidate_id,
                election=election,
                position=position_code,
                status='approved'
            )
            # Check if already voted for this position
            existing_vote = ElectionVote.objects.filter(
                election=election,
                voter=user,
                position=position_code
            ).first()
            
            if existing_vote:
                existing_vote.candidate = candidacy
                existing_vote.save()
            else:
                ElectionVote.objects.create(
                    election=election,
                    voter=user,
                    candidate=candidacy,
                    position=position_code
                )
        except Candidacy.DoesNotExist:
            messages.error(request, _('Invalid candidate selected.'))
            return redirect('governance:election_vote', pk=election_id)
    
    messages.success(request, _('Vote cast successfully!'))
    return redirect('governance:election_detail', pk=election_id)


# ============================================================================
# BOARD OF AUDITORS VIEWS
# ============================================================================

class BoardOfAuditorsListView(GovernanceRequiredMixin, ListView):
    """List boards of auditors."""
    model = BoardOfAuditors
    template_name = 'governance/auditors/board_list.html'
    context_object_name = 'boards'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BoardOfAuditors.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-term_start')


class BoardOfAuditorsDetailView(GovernanceRequiredMixin, DetailView):
    """Board of auditors detail."""
    model = BoardOfAuditors
    template_name = 'governance/auditors/board_detail.html'
    context_object_name = 'board'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()
        context['members'] = board.members.all().select_related('user')
        context['audit_reports'] = board.audit_reports.all().order_by('-report_date')[:10]
        return context


class BoardOfAuditorsCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create board of auditors."""
    model = BoardOfAuditors
    fields = ['name', 'term_start', 'term_end', 'is_renewed', 'status', 'notes']
    template_name = 'governance/auditors/board_form.html'
    success_url = reverse_lazy('governance:board_of_auditors_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['term_start'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['term_end'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['notes'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'})
        return form


class AuditReportListView(GovernanceRequiredMixin, ListView):
    """List audit reports."""
    model = AuditReport
    template_name = 'governance/auditors/audit_report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AuditReport.objects.select_related('board').all()
        board_id = self.request.GET.get('board')
        if board_id:
            queryset = queryset.filter(board_id=board_id)
        return queryset.order_by('-report_date', '-period_end')


class AuditReportCreateView(FinancialManagementRequiredMixin, CreateView):
    """Create audit report (quarterly as per Article 18)."""
    model = AuditReport
    fields = ['board', 'period_start', 'period_end', 'report_date', 'findings', 
              'recommendations', 'financial_verification_status']
    template_name = 'governance/auditors/audit_report_form.html'
    success_url = reverse_lazy('governance:audit_report_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['period_start'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['period_end'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['report_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['findings'].widget = forms.Textarea(attrs={'rows': 10, 'class': 'form-textarea'})
        form.fields['recommendations'].widget = forms.Textarea(attrs={'rows': 5, 'class': 'form-textarea'})
        return form


# ============================================================================
# DISCIPLINARY SYSTEM VIEWS
# ============================================================================

class DisciplinaryCaseListView(GovernanceRequiredMixin, ListView):
    """List disciplinary cases."""
    model = DisciplinaryCase
    template_name = 'governance/disciplinary/case_list.html'
    context_object_name = 'cases'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = DisciplinaryCase.objects.select_related('member', 'member__user', 'reported_by').all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        violation_type = self.request.GET.get('violation_type')
        if violation_type:
            queryset = queryset.filter(violation_type=violation_type)
        return queryset.order_by('-reported_date', '-created_at')


class DisciplinaryCaseDetailView(GovernanceRequiredMixin, DetailView):
    """Disciplinary case detail."""
    model = DisciplinaryCase
    template_name = 'governance/disciplinary/case_detail.html'
    context_object_name = 'case'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.get_object()
        context['sanctions'] = case.sanctions.all().order_by('-applied_date')
        return context


class DisciplinaryCaseCreateView(GovernanceRequiredMixin, CreateView):
    """Create disciplinary case (any member can report)."""
    model = DisciplinaryCase
    fields = ['member', 'violation_type', 'description', 'evidence']
    template_name = 'governance/disciplinary/case_form.html'
    success_url = reverse_lazy('governance:disciplinary_case_list')
    
    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        form.instance.reported_date = timezone.now().date()
        messages.success(
            self.request,
            _('Disciplinary case reported. The Executive Board will review it.')
        )
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['description'].widget = forms.Textarea(attrs={'rows': 6, 'class': 'form-textarea'})
        form.fields['evidence'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'})
        return form


class DisciplinarySanctionCreateView(ExecutiveBoardRequiredMixin, CreateView):
    """Apply disciplinary sanction (Article 28)."""
    model = DisciplinarySanction
    fields = ['case', 'sanction_type', 'applied_date', 'expiration_date', 'notes']
    template_name = 'governance/disciplinary/sanction_form.html'
    success_url = reverse_lazy('governance:disciplinary_case_list')
    
    def get_initial(self):
        initial = super().get_initial()
        case_id = self.request.GET.get('case')
        if case_id:
            initial['case'] = case_id
        initial['applied_date'] = timezone.now().date()
        return initial
    
    def form_valid(self, form):
        form.instance.applied_by = self.request.user
        form.instance.status = 'active'
        
        # Auto-determine sanction based on violation type (Article 28)
        case = form.instance.case
        if not form.instance.sanction_type:
            if case.violation_type == 'forum_confusion':
                form.instance.sanction_type = 'request_explanation'
            elif case.violation_type == 'public_insult':
                form.instance.sanction_type = 'warning'
            elif case.violation_type == 'assault_battery':
                form.instance.sanction_type = 'blame'
            elif case.violation_type == 'non_compliance':
                form.instance.sanction_type = 'warning'
            else:
                form.instance.sanction_type = 'request_explanation'
        
        # Update case status
        case.status = 'resolved'
        case.save()
        
        messages.success(self.request, _('Disciplinary sanction applied.'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['applied_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['expiration_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['notes'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'})
        return form


# ============================================================================
# ASSOCIATION EVENTS VIEWS
# ============================================================================

class AssociationEventListView(GovernanceRequiredMixin, ListView):
    """List association events."""
    model = AssociationEvent
    template_name = 'governance/events/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AssociationEvent.objects.all()
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        return queryset.order_by('-start_date')


class AssociationEventDetailView(GovernanceRequiredMixin, DetailView):
    """Association event detail."""
    model = AssociationEvent
    template_name = 'governance/events/event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['organizing_committees'] = event.organizing_committees.all().prefetch_related('members')
        return context


class AssociationEventCreateView(ExecutiveBoardRequiredMixin, CreateView):
    """Create association event."""
    model = AssociationEvent
    form_class = AssociationEventForm
    template_name = 'governance/events/event_form.html'
    success_url = reverse_lazy('governance:association_event_list')


# ============================================================================
# COMMUNICATION VIEWS
# ============================================================================

class CommunicationListView(GovernanceRequiredMixin, ListView):
    """List communications."""
    model = Communication
    template_name = 'governance/communications/list.html'
    context_object_name = 'communications'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Communication.objects.select_related('published_by', 'president_approved_by').all()
        communication_type = self.request.GET.get('communication_type')
        if communication_type:
            queryset = queryset.filter(communication_type=communication_type)
        is_published = self.request.GET.get('is_published')
        if is_published == 'true':
            queryset = queryset.filter(is_published=True)
        elif is_published == 'false':
            queryset = queryset.filter(is_published=False)
        return queryset.order_by('-publication_date', '-created_at')


class CommunicationDetailView(GovernanceRequiredMixin, DetailView):
    """Communication detail."""
    model = Communication
    template_name = 'governance/communications/detail.html'
    context_object_name = 'communication'


class CommunicationCreateView(GovernanceRequiredMixin, CreateView):
    """Create communication (Communication Manager)."""
    model = Communication
    form_class = CommunicationForm
    template_name = 'governance/communications/form.html'
    success_url = reverse_lazy('governance:communication_list')
    
    def form_valid(self, form):
        form.instance.published_by = self.request.user
        form.instance.publication_date = timezone.now()
        messages.success(
            self.request,
            _('Communication created. It requires President approval before publication (Article 19).')
        )
        return super().form_valid(form)


@login_required
def approve_communication(request, communication_id):
    """President approves communication (Article 19)."""
    communication = get_object_or_404(Communication, pk=communication_id)
    
    # Check if user is President
    current_board = ExecutiveBoard.objects.filter(status='active').first()
    if not current_board:
        messages.error(request, _('No active executive board found.'))
        return redirect('governance:communication_detail', pk=communication_id)
    
    president_position = current_board.positions.filter(
        position='president',
        status='active',
        user=request.user
    ).first()
    
    if not president_position and not request.user.is_superuser:
        messages.error(request, _('Only the President can approve communications (Article 19).'))
        return redirect('governance:communication_detail', pk=communication_id)
    
    communication.president_approved = True
    communication.president_approved_by = request.user
    communication.save()
    
    messages.success(request, _('Communication approved by President.'))
    return redirect('governance:communication_detail', pk=communication_id)


@login_required
def publish_communication(request, communication_id):
    """Publish communication (Communication Manager)."""
    communication = get_object_or_404(Communication, pk=communication_id)
    
    # Check if requires approval and is approved
    if communication.requires_president_approval and not communication.president_approved:
        messages.error(request, _('This communication requires President approval before publication.'))
        return redirect('governance:communication_detail', pk=communication_id)
    
    communication.is_published = True
    communication.publication_date = timezone.now()
    communication.save()
    
    messages.success(request, _('Communication published successfully!'))
    return redirect('governance:communication_detail', pk=communication_id)


# ============================================================================
# ASSOCIATION DOCUMENTS VIEWS
# ============================================================================

class AssociationDocumentListView(GovernanceRequiredMixin, ListView):
    """List association documents."""
    model = AssociationDocument
    template_name = 'governance/documents/list.html'
    context_object_name = 'documents'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = AssociationDocument.objects.all()
        document_type = self.request.GET.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        return queryset.order_by('-publication_date', 'document_type')


class AssociationDocumentCreateView(AssemblyManagementRequiredMixin, CreateView):
    """Create/upload association document."""
    model = AssociationDocument
    fields = ['document_type', 'title', 'version', 'language', 'file', 'description', 
              'publication_date', 'is_active']
    template_name = 'governance/documents/form.html'
    success_url = reverse_lazy('governance:association_document_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['publication_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['description'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'})
        return form


# ============================================================================
# FINANCIAL REPORTS VIEWS
# ============================================================================

class FinancialReportListView(FinancialManagementRequiredMixin, ListView):
    """List financial reports."""
    model = FinancialReport
    template_name = 'governance/finances/reports.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FinancialReport.objects.select_related('generated_by', 'verified_by').all()
        report_type = self.request.GET.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        return queryset.order_by('-period_end', '-created_at')


class FinancialReportCreateView(FinancialManagementRequiredMixin, CreateView):
    """Create financial report (Treasurer)."""
    model = FinancialReport
    fields = ['report_type', 'period_start', 'period_end', 'report_content', 
              'total_income', 'total_expenses', 'balance']
    template_name = 'governance/finances/report_form.html'
    success_url = reverse_lazy('governance:financial_report_list')
    
    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        messages.success(self.request, _('Financial report created.'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['period_start'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['period_end'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
        form.fields['report_content'].widget = forms.Textarea(attrs={'rows': 15, 'class': 'form-textarea'})
        return form


# ============================================================================
# ADDITIONAL FUNCTIONALITY
# ============================================================================

@login_required
def propose_agenda_item(request):
    """Member proposes agenda item (Article 22 - 14 days notice)."""
    if request.method == 'POST':
        form = AgendaItemForm(request.POST)
        if form.is_valid():
            assembly = form.cleaned_data['assembly']
            proposal_date = form.cleaned_data['proposal_date']
            
            # Check 14-day requirement using utility
            deadline_check = check_agenda_item_proposal_deadline(assembly, proposal_date)
            if not deadline_check['compliant']:
                messages.error(request, deadline_check['message'])
                return redirect('governance:assembly_list')
            
            form.instance.proposed_by = request.user
            form.instance.status = 'proposed'
            form.save()
            messages.success(
                request,
                _('Agenda item proposed! The Executive Board will review it.')
            )
            return redirect('governance:assembly_detail', pk=assembly.pk)
    else:
        form = AgendaItemForm()
        assembly_id = request.GET.get('assembly')
        if assembly_id:
            form.fields['assembly'].initial = assembly_id
            # Pre-fill proposal date as today
            from datetime import date
            form.fields['proposal_date'].initial = date.today()
    
    return render(request, 'governance/assemblies/propose_agenda_item.html', {'form': form})


@login_required
def request_extraordinary_assembly(request):
    """1/4 of members request extraordinary assembly (Article 6, 11)."""
    try:
        member = request.user.member_profile
        if not member.is_active_member:
            messages.error(request, _('Only active members can request extraordinary assemblies.'))
            return redirect('governance:member_portal')
    except Member.DoesNotExist:
        messages.error(request, _('You must be a registered member.'))
        return redirect('governance:member_register')
    
    quorum_status = check_extraordinary_assembly_quorum()
    
    if request.method == 'POST':
        # In production, you'd create a request record here
        messages.info(
            request,
            _('Extraordinary assembly request submitted. {required} active members must request it (1/4 of members).').format(
                required=quorum_status['required']
            )
        )
        return redirect('governance:member_portal')
    
    return render(request, 'governance/assemblies/request_extraordinary.html', {
        'quorum_status': quorum_status
    })


@login_required
def publish_vote_results(request, vote_id):
    """Publish vote results within 30 days (Article 24)."""
    vote = get_object_or_404(AssemblyVote, pk=vote_id)
    
    if not request.user.has_perm('governance.manage_assembly'):
        messages.error(request, _('You do not have permission to publish vote results.'))
        return redirect('governance:assembly_detail', pk=vote.assembly.pk)
    
    vote.is_published = True
    vote.published_date = timezone.now().date()
    vote.save()
    
    messages.success(request, _('Vote results published!'))
    return redirect('governance:assembly_detail', pk=vote.assembly.pk)
