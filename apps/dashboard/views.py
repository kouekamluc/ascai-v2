"""
Views for dashboard app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.utils import timezone
from datetime import timedelta
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

from .mixins import DashboardRequiredMixin
from .models import (
    SupportTicket, TicketReply, CommunityGroup, GroupDiscussion, GroupAnnouncement, GroupFile,
    UserStorySubmission, EventRegistration, SavedDocument, StudentQuestion, OrientationSession
)
from .forms import (
    ProfileUpdateForm, DocumentUploadForm, SupportTicketForm, TicketReplyForm, GroupDiscussionForm,
    StorySubmissionForm, StudentQuestionForm, OrientationBookingForm, NotificationPreferencesForm
)
from apps.accounts.models import User, UserDocument
from apps.universities.models import SavedUniversity
from apps.scholarships.models import SavedScholarship
from apps.diaspora.models import Event
from apps.downloads.models import Document
from apps.mentorship.models import MentorshipRequest


class DashboardHomeView(DashboardRequiredMixin, TemplateView):
    """
    Main dashboard homepage with personalized content.
    """
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Statistics
        context['stats'] = {
            'saved_universities': SavedUniversity.objects.filter(user=user).count(),
            'saved_scholarships': SavedScholarship.objects.filter(user=user).count(),
            'saved_documents': SavedDocument.objects.filter(user=user).count(),
            'open_tickets': SupportTicket.objects.filter(user=user, status__in=['open', 'pending']).count(),
            'mentorship_requests': MentorshipRequest.objects.filter(student=user).count() if hasattr(user, 'is_student') and user.is_student else 0,
            'group_memberships': CommunityGroup.objects.filter(members=user).count(),
        }
        
        # Governance stats (if user has permissions)
        try:
            from apps.governance.models import (
                Member, GeneralAssembly, MembershipDues, FinancialTransaction,
                Election, AssemblyVote, AssemblyVoteRecord
            )
            
            # Check if user is a member
            is_member = hasattr(user, 'member_profile')
            context['is_member'] = is_member
            
            if is_member:
                member = user.member_profile
                context['member'] = member
                
                # Get upcoming assemblies for participation
                upcoming_assemblies = GeneralAssembly.objects.filter(
                    status='scheduled',
                    date__gte=timezone.now()
                ).prefetch_related('votes', 'agenda_items').order_by('date')[:5]
                
                # Check which assemblies have votes user can participate in
                assemblies_with_voting = []
                for assembly in upcoming_assemblies:
                    votes = assembly.votes.all()
                    if votes.exists():
                        # Check if user has voted on all votes
                        user_has_voted_all = all(
                            AssemblyVoteRecord.objects.filter(
                                vote=vote, voter=user
                            ).exists() for vote in votes
                        )
                        assemblies_with_voting.append({
                            'assembly': assembly,
                            'has_votes': True,
                            'user_has_voted_all': user_has_voted_all,
                            'vote_count': votes.count()
                        })
                    else:
                        assemblies_with_voting.append({
                            'assembly': assembly,
                            'has_votes': False,
                            'user_has_voted_all': False,
                            'vote_count': 0
                        })
                
                context['upcoming_assemblies'] = assemblies_with_voting
                
                # Get active elections user can vote in
                active_elections = Election.objects.filter(
                    status='in_progress',
                    end_date__gte=timezone.now().date()
                ).select_related('commission').prefetch_related('candidacies')[:5]
                
                # Check voting eligibility for each election
                elections_with_eligibility = []
                for election in active_elections:
                    from apps.governance.utils import check_voting_eligibility
                    eligibility = check_voting_eligibility(user, election=election)
                    elections_with_eligibility.append({
                        'election': election,
                        'eligible': eligibility.get('eligible', False),
                        'reason': eligibility.get('reason', '')
                    })
                
                context['active_elections'] = elections_with_eligibility
            
            # Admin/staff governance stats
            if user.has_perm('governance.view_member') or user.is_staff:
                context['governance_stats'] = {
                    'total_members': Member.objects.count(),
                    'active_members': Member.objects.filter(is_active_member=True).count(),
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
        except Exception as e:
            # Governance app might not be migrated yet
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Governance integration error: {e}")
            context['is_member'] = False
        
        # Recent activity
        context['recent_tickets'] = SupportTicket.objects.filter(user=user).order_by('-created_at')[:5]
        context['recent_stories'] = UserStorySubmission.objects.filter(user=user).order_by('-submitted_at')[:3]
        
        # Upcoming events
        context['upcoming_events'] = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:5]
        
        # User's event registrations
        context['my_registrations'] = EventRegistration.objects.filter(
            user=user,
            event__start_datetime__gte=timezone.now()
        ).select_related('event').order_by('event__start_datetime')[:5]
        
        # Suggested groups based on user profile
        suggested_groups = CommunityGroup.objects.filter(is_public=True).exclude(members=user).annotate(
            member_count=Count('members')
        )
        if user.city_in_lazio:
            suggested_groups = suggested_groups.filter(
                Q(category__icontains=user.city_in_lazio) | Q(category='students')
            )
        context['suggested_groups'] = suggested_groups[:3]
        
        # Quick actions
        context['quick_actions'] = [
            {'title': _('Update Profile'), 'url': reverse_lazy('dashboard:profile_edit'), 'icon': 'user'},
            {'title': _('Submit Story'), 'url': reverse_lazy('dashboard:stories_submit'), 'icon': 'edit'},
            {'title': _('Create Ticket'), 'url': reverse_lazy('dashboard:tickets_create'), 'icon': 'support'},
            {'title': _('Browse Groups'), 'url': reverse_lazy('dashboard:groups_list'), 'icon': 'users'},
        ]
        
        # Add member portal link if user is a member
        try:
            if hasattr(user, 'member_profile'):
                context['quick_actions'].insert(0, {
                    'title': _('My Membership'), 
                    'url': reverse_lazy('governance:member_portal'), 
                    'icon': 'membership'
                })
        except Exception:
            pass
        
        # Add governance quick actions if user has permissions
        if user.has_perm('governance.view_member') or user.is_staff:
            context['quick_actions'].append(
                {'title': _('Governance Dashboard'), 'url': reverse_lazy('governance:dashboard'), 'icon': 'governance'}
            )
        if user.has_perm('governance.manage_finances') or user.is_staff:
            context['quick_actions'].append(
                {'title': _('Financial Transactions'), 'url': reverse_lazy('governance:financial_transactions'), 'icon': 'finance'}
            )
        
        return context


# Profile Management Views
class ProfileView(DashboardRequiredMixin, DetailView):
    """View user profile."""
    model = User
    template_name = 'dashboard/profile/view.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        """Add governance-related context."""
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        
        # Get active executive positions (filter in Python, not template)
        try:
            if hasattr(profile_user, 'executive_positions'):
                context['active_positions'] = profile_user.executive_positions.filter(status='active')
            else:
                context['active_positions'] = []
        except Exception:
            # Governance app might not be migrated yet
            context['active_positions'] = []
        
        return context


class ProfileUpdateView(DashboardRequiredMixin, UpdateView):
    """Update user profile."""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'dashboard/profile/edit.html'
    success_url = reverse_lazy('dashboard:profile_view')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log file upload if present
        if 'avatar' in self.request.FILES:
            uploaded_file = self.request.FILES['avatar']
            logger.info(f"Avatar upload detected: {uploaded_file.name}, size: {uploaded_file.size} bytes")
        
        # Save the form (this will handle the file upload)
        response = super().form_valid(form)
        
        # Log the saved avatar path
        if self.object.avatar:
            logger.info(f"Avatar saved to: {self.object.avatar.name}, URL: {self.object.avatar.url}")
            messages.success(self.request, _('Profile updated successfully.'))
        else:
            logger.warning("No avatar file after save")
            messages.success(self.request, _('Profile updated successfully.'))
        
        return response


class PasswordChangeView(DashboardRequiredMixin, DjangoPasswordChangeView):
    """Change user password."""
    template_name = 'dashboard/profile/password_change.html'
    success_url = reverse_lazy('dashboard:profile_view')
    
    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Important!
        messages.success(self.request, _('Password changed successfully.'))
        return super().form_valid(form)


class DocumentUploadView(DashboardRequiredMixin, CreateView):
    """Upload user document."""
    model = UserDocument
    form_class = DocumentUploadForm
    template_name = 'dashboard/profile/documents.html'
    success_url = reverse_lazy('dashboard:profile_documents')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Document uploaded successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = UserDocument.objects.filter(user=self.request.user).order_by('-uploaded_at')
        return context


class DocumentDeleteView(DashboardRequiredMixin, DeleteView):
    """Delete user document."""
    model = UserDocument
    success_url = reverse_lazy('dashboard:profile_documents')
    
    def get_queryset(self):
        return UserDocument.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Document deleted successfully.'))
        return super().delete(request, *args, **kwargs)


class NotificationPreferencesView(DashboardRequiredMixin, FormView):
    """Manage notification preferences."""
    form_class = NotificationPreferencesForm
    template_name = 'dashboard/profile/notifications.html'
    success_url = reverse_lazy('dashboard:profile_notifications')
    
    def get_initial(self):
        prefs = self.request.user.notification_preferences or {}
        return {
            'email_notifications': prefs.get('email_notifications', True),
            'ticket_updates': prefs.get('ticket_updates', True),
            'event_reminders': prefs.get('event_reminders', True),
            'group_announcements': prefs.get('group_announcements', True),
        }
    
    def form_valid(self, form):
        self.request.user.notification_preferences = form.cleaned_data
        self.request.user.save()
        messages.success(self.request, _('Notification preferences updated.'))
        return super().form_valid(form)


# Support Tickets Views
class TicketListView(DashboardRequiredMixin, ListView):
    """List user's support tickets."""
    model = SupportTicket
    template_name = 'dashboard/support/tickets.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by('-created_at')


class TicketCreateView(DashboardRequiredMixin, CreateView):
    """Create support ticket."""
    model = SupportTicket
    form_class = SupportTicketForm
    template_name = 'dashboard/support/ticket_create.html'
    success_url = reverse_lazy('dashboard:tickets_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Support ticket created successfully.'))
        return super().form_valid(form)


class TicketDetailView(DashboardRequiredMixin, DetailView):
    """View support ticket details."""
    model = SupportTicket
    template_name = 'dashboard/support/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).prefetch_related('replies')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['replies'] = TicketReply.objects.filter(ticket=self.get_object()).order_by('created_at')
        context['reply_form'] = TicketReplyForm()
        return context


class TicketReplyView(DashboardRequiredMixin, CreateView):
    """Reply to a support ticket."""
    model = TicketReply
    form_class = TicketReplyForm
    template_name = 'dashboard/support/ticket_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.ticket = get_object_or_404(SupportTicket, pk=kwargs['pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add ticket context for form error display."""
        context = super().get_context_data(**kwargs)
        context['ticket'] = self.ticket
        context['replies'] = TicketReply.objects.filter(ticket=self.ticket).order_by('created_at')
        # Use the form from context if available, otherwise create a new one
        if 'form' not in context:
            context['reply_form'] = self.get_form()
        else:
            context['reply_form'] = context['form']
        return context
    
    def form_valid(self, form):
        form.instance.ticket = self.ticket
        form.instance.author = self.request.user
        form.instance.is_admin_reply = False
        # Update ticket status to open if it was resolved/closed
        if self.ticket.status in ['resolved', 'closed']:
            self.ticket.status = 'open'
            self.ticket.save()
        messages.success(self.request, _('Your reply has been sent.'))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors by showing them in the ticket detail view."""
        messages.error(self.request, _('Please correct the errors below.'))
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('dashboard:ticket_detail', kwargs={'pk': self.ticket.pk})


# Community Groups Views
class GroupListView(DashboardRequiredMixin, ListView):
    """List all community groups."""
    model = CommunityGroup
    template_name = 'dashboard/groups/list.html'
    context_object_name = 'groups'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = CommunityGroup.objects.filter(is_public=True).annotate(
            member_count=Count('members')
        )
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_groups'] = CommunityGroup.objects.filter(members=self.request.user)
        return context


class GroupDetailView(DashboardRequiredMixin, DetailView):
    """View community group details."""
    model = CommunityGroup
    template_name = 'dashboard/groups/detail.html'
    context_object_name = 'group'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Annotate member count for performance."""
        return CommunityGroup.objects.annotate(member_count=Count('members'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['is_member'] = group.members.filter(id=self.request.user.id).exists()
        context['discussions'] = GroupDiscussion.objects.filter(group=group).order_by('-created_at')[:10]
        context['announcements'] = GroupAnnouncement.objects.filter(group=group).order_by('-is_pinned', '-created_at')[:5]
        context['files'] = GroupFile.objects.filter(group=group).order_by('-uploaded_at')[:10]
        # Add group to context for discussion create form
        context['group'] = group
        return context


@login_required
def group_join(request, slug):
    """Join or leave a community group."""
    from .mixins import DashboardRequiredMixin
    # Check if user is approved
    if not request.user.is_approved and not request.user.is_superuser:
        messages.error(request, _('Your account must be approved to join groups.'))
        return redirect('dashboard:groups_list')
    
    group = get_object_or_404(CommunityGroup, slug=slug)
    if group.members.filter(id=request.user.id).exists():
        group.members.remove(request.user)
        messages.success(request, _('You have left the group.'))
    else:
        group.members.add(request.user)
        messages.success(request, _('You have joined the group.'))
    return redirect('dashboard:group_detail', slug=slug)


class DiscussionCreateView(DashboardRequiredMixin, CreateView):
    """Create group discussion."""
    model = GroupDiscussion
    form_class = GroupDiscussionForm
    template_name = 'dashboard/groups/discussion_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(CommunityGroup, slug=kwargs['slug'])
        if not self.group.members.filter(id=request.user.id).exists():
            messages.error(request, _('You must be a member to create discussions.'))
            return redirect('dashboard:group_detail', slug=self.group.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context
    
    def form_valid(self, form):
        form.instance.group = self.group
        form.instance.author = self.request.user
        messages.success(self.request, _('Discussion created successfully.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboard:group_detail', kwargs={'slug': self.group.slug})


class DiscussionDetailView(DashboardRequiredMixin, DetailView):
    """View discussion details."""
    model = GroupDiscussion
    template_name = 'dashboard/groups/discussion.html'
    context_object_name = 'discussion'
    
    def get_queryset(self):
        return GroupDiscussion.objects.select_related('group', 'author')


# Story Submission Views
class StorySubmissionListView(DashboardRequiredMixin, ListView):
    """List user's story submissions."""
    model = UserStorySubmission
    template_name = 'dashboard/stories/my_stories.html'
    context_object_name = 'stories'
    paginate_by = 10
    
    def get_queryset(self):
        return UserStorySubmission.objects.filter(user=self.request.user).order_by('-submitted_at')


class StorySubmissionCreateView(DashboardRequiredMixin, CreateView):
    """Submit diaspora story."""
    model = UserStorySubmission
    form_class = StorySubmissionForm
    template_name = 'dashboard/stories/submit.html'
    success_url = reverse_lazy('dashboard:stories_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Story submitted successfully. It will be reviewed by an admin.'))
        return super().form_valid(form)


class StorySubmissionDetailView(DashboardRequiredMixin, DetailView):
    """View story submission details."""
    model = UserStorySubmission
    template_name = 'dashboard/stories/story_detail.html'
    context_object_name = 'story'
    
    def get_queryset(self):
        return UserStorySubmission.objects.filter(user=self.request.user)


# Events Views
class EventListView(DashboardRequiredMixin, ListView):
    """List upcoming events."""
    model = Event
    template_name = 'dashboard/events/list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        return Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Get registrations for events in the current page
        event_ids = [event.id for event in context['events']]
        registered_event_ids = EventRegistration.objects.filter(
            user=user,
            event_id__in=event_ids
        ).values_list('event_id', flat=True)
        context['registered_event_ids'] = list(registered_event_ids)
        return context


@login_required
def event_register(request, pk):
    """Register for an event."""
    from .mixins import DashboardRequiredMixin
    # Check if user is approved
    if not request.user.is_approved and not request.user.is_superuser:
        messages.error(request, _('Your account must be approved to register for events.'))
        return redirect('dashboard:events_list')
    
    event = get_object_or_404(Event, pk=pk, is_published=True)
    
    if not event.registration_required:
        messages.info(request, _('Registration is not required for this event.'))
        return redirect('dashboard:events_list')
    
    # Check if already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.info(request, _('You are already registered for this event.'))
        return redirect('dashboard:events_list')
    
    # Check capacity
    if event.max_participants:
        current_registrations = EventRegistration.objects.filter(event=event).count()
        if current_registrations >= event.max_participants:
            messages.error(request, _('This event is full.'))
            return redirect('dashboard:events_list')
    
    # Create registration
    registration = EventRegistration.objects.create(event=event, user=request.user)
    messages.success(request, _('Successfully registered for the event.'))
    return redirect('dashboard:event_ticket', pk=registration.id)


class EventTicketView(DashboardRequiredMixin, DetailView):
    """View event ticket with QR code."""
    model = EventRegistration
    template_name = 'dashboard/events/ticket.html'
    context_object_name = 'registration'
    
    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user).select_related('event')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = self.get_object()
        
        # Generate QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(registration.registration_code)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Convert to base64 for embedding in template
            import base64
            context['qr_code_data'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception:
            # If QR code generation fails, just pass the code
            context['qr_code_data'] = None
        
        context['qr_code'] = registration.registration_code
        return context


class EventAttendanceHistoryView(DashboardRequiredMixin, ListView):
    """View past event attendance."""
    model = EventRegistration
    template_name = 'dashboard/events/history.html'
    context_object_name = 'registrations'
    paginate_by = 10
    
    def get_queryset(self):
        return EventRegistration.objects.filter(
            user=self.request.user,
            event__start_datetime__lt=timezone.now()
        ).select_related('event').order_by('-event__start_datetime')


# Downloads Views
class ReservedDownloadsView(DashboardRequiredMixin, ListView):
    """List reserved downloads."""
    model = Document
    template_name = 'dashboard/downloads/list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        return Document.objects.filter(is_reserved=True, is_active=True).order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Get saved document IDs for documents in current page
        doc_ids = [doc.id for doc in context['documents']]
        saved_doc_ids = SavedDocument.objects.filter(
            user=user,
            document_id__in=doc_ids
        ).values_list('document_id', flat=True)
        context['saved_document_ids'] = list(saved_doc_ids)
        return context


@login_required
def document_download(request, pk):
    """Download a reserved document."""
    from .mixins import DashboardRequiredMixin
    # Check if user is approved
    if not request.user.is_approved and not request.user.is_superuser:
        messages.error(request, _('Your account must be approved to download documents.'))
        return redirect('dashboard:downloads_list')
    
    document = get_object_or_404(Document, pk=pk, is_reserved=True, is_active=True)
    document.increment_download_count()
    import os
    try:
        # Try to serve file directly if it exists locally
        if document.file and hasattr(document.file, 'path') and os.path.exists(document.file.path):
            return FileResponse(open(document.file.path, 'rb'), as_attachment=True, filename=os.path.basename(document.file.name))
        elif document.file:
            # For S3 or remote storage, redirect to URL
            return redirect(document.file.url)
        else:
            raise Http404("Document file not found")
    except (AttributeError, OSError):
        # Fallback to URL redirect if path access fails
        if document.file:
            return redirect(document.file.url)
        raise Http404("Document file not found")


@login_required
def document_save(request, pk):
    """Save/unsave a document."""
    from .mixins import DashboardRequiredMixin
    # Check if user is approved
    if not request.user.is_approved and not request.user.is_superuser:
        messages.error(request, _('Your account must be approved to save documents.'))
        return redirect('dashboard:downloads_list')
    
    document = get_object_or_404(Document, pk=pk, is_reserved=True)
    saved, created = SavedDocument.objects.get_or_create(
        user=request.user,
        document=document
    )
    if not created:
        saved.delete()
        messages.success(request, _('Document removed from saved items.'))
    else:
        messages.success(request, _('Document saved to your list.'))
    return redirect('dashboard:downloads_list')


class SavedDocumentsView(DashboardRequiredMixin, ListView):
    """View saved documents."""
    model = SavedDocument
    template_name = 'dashboard/downloads/saved.html'
    context_object_name = 'saved_documents'
    paginate_by = 20
    
    def get_queryset(self):
        return SavedDocument.objects.filter(user=self.request.user).select_related('document').order_by('-saved_at')


# New Student Assistance Views
class NewStudentGuideView(DashboardRequiredMixin, TemplateView):
    """New student assistance guide."""
    template_name = 'dashboard/new_student/guide.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Define guide sections
        context['guide_sections'] = [
            {
                'slug': 'residence-permit',
                'title': _('Residence Permit (Permesso di Soggiorno)'),
                'content': _('Apply for your residence permit within 8 days of arrival. Required documents include passport, visa, proof of enrollment, and health insurance. Visit the local Questura (police station) to submit your application.')
            },
            {
                'slug': 'codice-fiscale',
                'title': _('Codice Fiscale'),
                'content': _('Obtain your tax code (Codice Fiscale) from the local tax office (Agenzia delle Entrate). This is required for many administrative procedures including opening a bank account, signing contracts, and accessing healthcare services.')
            },
            {
                'slug': 'university-enrollment',
                'title': _('University Enrollment'),
                'content': _('Complete your university enrollment process. Contact your university\'s international office for specific requirements. You will typically need your diploma, transcript, passport, and residence permit.')
            },
            {
                'slug': 'health-insurance',
                'title': _('Health Insurance (SSN)'),
                'content': _('Register with the Italian National Health Service (Servizio Sanitario Nazionale) for healthcare coverage. This requires your residence permit, Codice Fiscale, and proof of enrollment.')
            },
            {
                'slug': 'housing',
                'title': _('Housing'),
                'content': _('Find accommodation and register your address with the local municipality (Comune). You will need a rental contract and your residence permit for registration.')
            },
        ]
        return context


class GuideDetailView(DashboardRequiredMixin, TemplateView):
    """Individual guide detail page."""
    template_name = 'dashboard/new_student/guide_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        
        # Guide sections data
        guide_sections = {
            'residence-permit': {
                'title': _('Residence Permit (Permesso di Soggiorno)'),
                'content': _('Apply for your residence permit within 8 days of arrival. Required documents include passport, visa, proof of enrollment, and health insurance. Visit the local Questura (police station) to submit your application.'),
                'steps': [
                    _('Gather required documents: passport, visa, proof of enrollment, health insurance, proof of accommodation'),
                    _('Book an appointment at the Questura (police station)'),
                    _('Submit your application and pay the required fees'),
                    _('Wait for processing (usually 30-60 days)'),
                    _('Collect your residence permit when ready')
                ]
            },
            'codice-fiscale': {
                'title': _('Codice Fiscale'),
                'content': _('Obtain your tax code (Codice Fiscale) from the local tax office (Agenzia delle Entrate). This is required for many administrative procedures.'),
                'steps': [
                    _('Visit the Agenzia delle Entrate office'),
                    _('Bring your passport and visa'),
                    _('Fill out the application form'),
                    _('Receive your Codice Fiscale immediately')
                ]
            },
            'university-enrollment': {
                'title': _('University Enrollment'),
                'content': _('Complete your university enrollment process. Contact your university\'s international office for specific requirements.'),
                'steps': [
                    _('Contact the international office of your university'),
                    _('Submit required documents (diploma, transcript, passport)'),
                    _('Pay enrollment fees'),
                    _('Complete any required language tests'),
                    _('Receive your student ID card')
                ]
            },
            'health-insurance': {
                'title': _('Health Insurance (SSN)'),
                'content': _('Register with the Italian National Health Service (Servizio Sanitario Nazionale) for healthcare coverage.'),
                'steps': [
                    _('Obtain your residence permit and Codice Fiscale'),
                    _('Visit the local ASL (Azienda Sanitaria Locale) office'),
                    _('Submit your application with required documents'),
                    _('Receive your health insurance card')
                ]
            },
            'housing': {
                'title': _('Housing'),
                'content': _('Find accommodation and register your address with the local municipality (Comune).'),
                'steps': [
                    _('Search for accommodation (university housing, private rentals, shared apartments)'),
                    _('Sign a rental contract'),
                    _('Register your address at the Comune'),
                    _('Set up utilities (electricity, gas, internet)')
                ]
            },
        }
        
        context['guide'] = guide_sections.get(slug, {
            'title': _('Guide Not Found'),
            'content': _('The requested guide section was not found.'),
            'steps': []
        })
        context['slug'] = slug
        return context


class StudentQuestionListView(DashboardRequiredMixin, ListView):
    """List student questions."""
    model = StudentQuestion
    template_name = 'dashboard/new_student/questions.html'
    context_object_name = 'questions'
    paginate_by = 10
    
    def get_queryset(self):
        return StudentQuestion.objects.filter(user=self.request.user).order_by('-created_at')


class StudentQuestionCreateView(DashboardRequiredMixin, CreateView):
    """Create student question."""
    model = StudentQuestion
    form_class = StudentQuestionForm
    template_name = 'dashboard/new_student/question_create.html'
    success_url = reverse_lazy('dashboard:student_questions')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Question submitted successfully.'))
        return super().form_valid(form)


class OrientationBookingCreateView(DashboardRequiredMixin, CreateView):
    """Book orientation session."""
    model = OrientationSession
    form_class = OrientationBookingForm
    template_name = 'dashboard/new_student/orientation_booking.html'
    success_url = reverse_lazy('dashboard:new_student_guide')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Orientation session requested. You will be contacted soon.'))
        return super().form_valid(form)


# Mentorship Integration
class MentorshipDashboardView(DashboardRequiredMixin, TemplateView):
    """Unified mentorship dashboard."""
    template_name = 'dashboard/mentorship/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['needs_profile'] = False
        context['requests'] = []
        context['my_requests'] = []
        context['mentor_profile'] = None
        
        if user.is_mentor:
            from apps.mentorship.models import MentorProfile
            try:
                mentor_profile = user.mentor_profile
                context['mentor_profile'] = mentor_profile
                context['requests'] = MentorshipRequest.objects.filter(mentor=mentor_profile).order_by('-created_at')[:10]
            except MentorProfile.DoesNotExist:
                context['needs_profile'] = True
        
        if user.is_student:
            context['my_requests'] = MentorshipRequest.objects.filter(student=user).order_by('-created_at')[:10]
        
        return context


# Personalization
class SavedItemsView(DashboardRequiredMixin, TemplateView):
    """View all saved items."""
    template_name = 'dashboard/saved_items.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['saved_universities'] = SavedUniversity.objects.filter(user=user).select_related('university')
        context['saved_scholarships'] = SavedScholarship.objects.filter(user=user).select_related('scholarship')
        context['saved_documents'] = SavedDocument.objects.filter(user=user).select_related('document')
        return context
