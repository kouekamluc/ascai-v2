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
        # Note: AssemblyVote doesn't have a voters field, we track votes differently
        user_votes = {}
        
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
    
    # Get vote choice from POST
    choice = request.POST.get('choice')
    if choice not in ['yes', 'no', 'abstain']:
        messages.error(request, _('Invalid vote choice.'))
        return redirect('governance:assembly_participate', pk=vote.assembly.pk)
    
    # Update vote counts (for now, we just increment - in production you'd track individual votes)
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
        context['signed_count'] = approvals.filter(status='signed').count()
        context['required_signatures'] = 3
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
