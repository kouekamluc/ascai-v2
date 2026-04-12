"""
Views for mentorship app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
from .models import (
    MentorSpecialization, MentorProfile, MentorshipRequest,
    MentorshipMessage, MentorRating, MentorshipSession
)
from .forms import (
    MentorProfileForm, MentorProfileUpdateForm, MentorshipRequestForm, 
    MentorshipMessageForm, MentorRatingForm, MentorshipSessionForm
)
from .services import (
    accept_request as accept_mentorship_request,
    complete_request as complete_mentorship_request,
    create_request as create_mentorship_request,
    get_request_queryset_for_user,
    reject_request as reject_mentorship_request,
    send_message as send_mentorship_message,
    update_availability as update_mentor_availability,
)


class MentorListView(ListView):
    """Enhanced list view for approved mentors with advanced filters."""
    model = MentorProfile
    template_name = 'mentorship/mentor_list.html'
    context_object_name = 'mentors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = MentorProfile.objects.filter(is_approved=True).select_related('user').prefetch_related('specializations')
        
        # Filter by specialization
        specialization = self.request.GET.get('specialization')
        if specialization:
            queryset = queryset.filter(specializations__id=specialization)
        
        # Filter by availability
        availability = self.request.GET.get('availability')
        if availability:
            queryset = queryset.filter(availability_status=availability)
        
        # Filter by rating (minimum)
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except ValueError:
                pass
        
        # Filter by experience (minimum years)
        min_experience = self.request.GET.get('min_experience')
        if min_experience:
            try:
                queryset = queryset.filter(years_experience__gte=int(min_experience))
            except ValueError:
                pass
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(specialization__icontains=search) |
                Q(bio__icontains=search) |
                Q(specializations__name__icontains=search)
            )
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'rating')
        if sort_by == 'experience':
            queryset = queryset.order_by('-years_experience', '-rating')
        elif sort_by == 'students':
            queryset = queryset.order_by('-students_helped', '-rating')
        elif sort_by == 'success':
            queryset = queryset.order_by('-success_rate', '-rating')
        else:  # rating (default)
            queryset = queryset.order_by('-rating', '-students_helped')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specializations'] = MentorSpecialization.objects.all().order_by('order', 'name')
        context['filter_specialization'] = self.request.GET.get('specialization', '')
        context['filter_availability'] = self.request.GET.get('availability', '')
        context['filter_min_rating'] = self.request.GET.get('min_rating', '')
        context['filter_min_experience'] = self.request.GET.get('min_experience', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'rating')
        return context


class MentorDetailView(DetailView):
    """Detail view for mentor profile."""
    model = MentorProfile
    template_name = 'mentorship/mentor_detail.html'
    context_object_name = 'mentor'
    
    def get_queryset(self):
        return MentorProfile.objects.filter(is_approved=True).select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Check for existing pending or accepted requests
            existing_requests = MentorshipRequest.objects.filter(
                student=self.request.user,
                mentor=self.object,
                status__in=['pending', 'accepted']
            )
            context['has_request'] = existing_requests.exists()
            context['existing_request'] = existing_requests.first()
        
        # Add absolute avatar URL for meta tags
        if self.object.user.avatar:
            context['avatar_url'] = self.request.build_absolute_uri(self.object.user.avatar.url)
        else:
            context['avatar_url'] = None
        
        # Get mentor's specializations
        context['specializations'] = self.object.specializations.all()
        
        # Get testimonials/ratings
        context['ratings'] = self.object.ratings.select_related('student').order_by('-created_at')[:5]
        context['average_rating'] = self.object.rating
        context['total_ratings'] = self.object.ratings.count()
        
        return context


class MentorProfileCreateView(LoginRequiredMixin, CreateView):
    """Create mentor profile view."""
    model = MentorProfile
    form_class = MentorProfileForm
    template_name = 'mentorship/mentor_profile_create.html'
    success_url = reverse_lazy('mentorship:mentor_dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MentorshipRequestCreateView(LoginRequiredMixin, CreateView):
    """Create mentorship request view."""
    model = MentorshipRequest
    form_class = MentorshipRequestForm
    template_name = 'mentorship/request_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentor = get_object_or_404(
            MentorProfile, 
            id=self.kwargs['mentor_id'],
            is_approved=True  # Only allow requests to approved mentors
        )
        context['mentor'] = mentor
        context['mentor_id'] = self.kwargs['mentor_id']
        return context
    
    def form_valid(self, form):
        mentor = get_object_or_404(
            MentorProfile, 
            id=self.kwargs['mentor_id'],
            is_approved=True  # Only allow requests to approved mentors
        )

        try:
            self.object = create_mentorship_request(
                student=self.request.user,
                mentor=mentor,
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
            )
        except (PermissionDenied, ValidationError) as exc:
            messages.error(self.request, exc.messages[0] if hasattr(exc, "messages") else str(exc))
            return redirect('mentorship:mentor_detail', pk=mentor.pk)

        messages.success(self.request, _('Mentorship request sent successfully!'))
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('mentorship:student_dashboard')


class MentorDashboardView(LoginRequiredMixin, TemplateView):
    """Mentor dashboard view."""
    template_name = 'mentorship/mentor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentor_profile = getattr(self.request.user, 'mentor_profile', None)
        if mentor_profile:
            all_requests = mentor_profile.requests.all().order_by('-created_at')
            context['requests'] = all_requests
            context['mentor_profile'] = mentor_profile
            context['pending_count'] = all_requests.filter(status='pending').count()
            context['accepted_count'] = all_requests.filter(status='accepted').count()
        return context


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    """Student dashboard view."""
    template_name = 'mentorship/student_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = MentorshipRequest.objects.filter(
            student=self.request.user
        ).order_by('-created_at')
        return context


class RequestDetailView(LoginRequiredMixin, DetailView):
    """Detail view for mentorship request with messages."""
    model = MentorshipRequest
    template_name = 'mentorship/request_detail.html'
    context_object_name = 'request'
    
    def get_queryset(self):
        return get_request_queryset_for_user(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Mark messages as read when viewing
        unread_messages = self.object.messages.exclude(sender=user).filter(is_read=False)
        unread_messages.update(is_read=True)
        
        context['messages'] = self.object.messages.all().order_by('created_at')
        context['form'] = MentorshipMessageForm()
        
        # Safely check for rating form
        try:
            can_rate = (
                self.object.status == 'completed' and 
                not self.object.has_rating() and 
                self.object.student == user
            )
            context['rating_form'] = MentorRatingForm() if can_rate else None
        except Exception:
            context['rating_form'] = None
        
        context['can_complete'] = self.object.can_be_completed()
        context['is_student'] = self.object.student == user
        
        try:
            context['is_mentor'] = self.object.mentor and self.object.mentor.user == user
        except (AttributeError, TypeError):
            context['is_mentor'] = False
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle message creation via HTMX."""
        self.object = self.get_object()
        
        # Only allow messages if request is accepted
        if self.object.status != 'accepted':
            return JsonResponse({'error': _('Request must be accepted to send messages.')}, status=400)
        
        form = MentorshipMessageForm(request.POST)
        if form.is_valid():
            try:
                message = send_mentorship_message(
                    mentorship_request=self.object,
                    sender=request.user,
                    content=form.cleaned_data["content"],
                )
            except (PermissionDenied, ValidationError) as exc:
                return JsonResponse(
                    {"error": exc.messages[0] if hasattr(exc, "messages") else str(exc)},
                    status=400,
                )
            
            # Return message item for HTMX
            if request.headers.get('HX-Request'):
                return render(request, 'mentorship/partials/message_item.html', {
                    'message': message,
                    'user': request.user
                })
            return redirect('mentorship:request_detail', pk=self.object.pk)
        
        return JsonResponse({'error': _('Invalid form data.')}, status=400)


@login_required
@require_http_methods(["POST"])
def accept_request(request, request_id):
    """Accept mentorship request (HTMX endpoint)."""
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id)
    try:
        mentorship_request = accept_mentorship_request(
            mentorship_request=mentorship_request,
            actor=request.user,
        ).request
    except PermissionDenied as exc:
        return JsonResponse({'error': str(exc)}, status=403)
    except ValidationError as exc:
        return JsonResponse({'error': exc.messages[0]}, status=400)
    
    # Return HTMX-compatible HTML fragment
    if request.headers.get('HX-Request'):
        return render(request, 'mentorship/partials/request_item.html', {
            'request': mentorship_request
        })
    return JsonResponse({'status': 'accepted'})


@login_required
@require_http_methods(["POST"])
def reject_request(request, request_id):
    """Reject mentorship request (HTMX endpoint)."""
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id)
    try:
        mentorship_request = reject_mentorship_request(
            mentorship_request=mentorship_request,
            actor=request.user,
        ).request
    except PermissionDenied as exc:
        return JsonResponse({'error': str(exc)}, status=403)
    except ValidationError as exc:
        return JsonResponse({'error': exc.messages[0]}, status=400)
    
    # Return HTMX-compatible HTML fragment
    if request.headers.get('HX-Request'):
        return render(request, 'mentorship/partials/request_item.html', {
            'request': mentorship_request
        })
    return JsonResponse({'status': 'rejected'})


@login_required
@require_http_methods(["GET"])
def get_messages(request, request_id):
    """Get messages for a mentorship request (HTMX polling endpoint)."""
    mentorship_request = get_object_or_404(
        MentorshipRequest,
        id=request_id
    )
    
    if mentorship_request.student != request.user and (not mentorship_request.mentor or mentorship_request.mentor.user != request.user):
        return JsonResponse({'error': _('Access denied.')}, status=403)
    
    # Mark messages as read when polling
    unread_messages = mentorship_request.messages.exclude(sender=request.user).filter(is_read=False)
    unread_messages.update(is_read=True)
    
    messages = mentorship_request.messages.all().order_by('created_at')
    return render(request, 'mentorship/partials/messages_list.html', {
        'messages': messages,
        'user': request.user
    })


class MentorProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update mentor profile view."""
    model = MentorProfile
    form_class = MentorProfileUpdateForm
    template_name = 'mentorship/mentor_profile_update.html'
    success_url = reverse_lazy('mentorship:mentor_dashboard')
    
    def get_queryset(self):
        return MentorProfile.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, _('Mentor profile updated successfully!'))
        return super().form_valid(form)


@login_required
@require_http_methods(["POST"])
def complete_request(request, request_id):
    """Mark mentorship request as completed (HTMX endpoint)."""
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id)
    try:
        mentorship_request = complete_mentorship_request(
            mentorship_request=mentorship_request,
            actor=request.user,
        ).request
    except PermissionDenied as exc:
        return JsonResponse({'error': str(exc)}, status=403)
    except ValidationError as exc:
        return JsonResponse({'error': exc.messages[0]}, status=400)
    
    messages.success(request, _('Mentorship request marked as completed.'))
    
    # Return HTMX-compatible response
    if request.headers.get('HX-Request'):
        return JsonResponse({'status': 'completed', 'redirect': reverse('mentorship:request_detail', kwargs={'pk': request_id})})
    return redirect('mentorship:request_detail', pk=request_id)


@login_required
@require_http_methods(["POST"])
def update_availability(request):
    """Update mentor availability status (HTMX endpoint)."""
    mentor_profile = get_object_or_404(MentorProfile, user=request.user)

    try:
        update_mentor_availability(
            mentor_profile=mentor_profile,
            actor=request.user,
            new_status=request.POST.get('availability_status'),
        )
    except PermissionDenied as exc:
        return JsonResponse({'error': str(exc)}, status=403)
    except ValidationError as exc:
        return JsonResponse({'error': exc.messages[0]}, status=400)
    
    return JsonResponse({'status': 'updated', 'availability_status': new_status})


class RateMentorView(LoginRequiredMixin, CreateView):
    """Rate mentor after mentorship completion."""
    model = MentorRating
    form_class = MentorRatingForm
    template_name = 'mentorship/rate_mentor.html'
    
    def get_mentorship_request(self):
        """Get the mentorship request."""
        return get_object_or_404(
            MentorshipRequest,
            id=self.kwargs['request_id'],
            student=self.request.user,
            status='completed'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentorship_request = self.get_mentorship_request()
        context['request'] = mentorship_request
        context['mentor'] = mentorship_request.mentor
        
        # Check if already rated
        if mentorship_request.has_rating():
            context['already_rated'] = True
            context['existing_rating'] = mentorship_request.rating
        return context
    
    def form_valid(self, form):
        mentorship_request = self.get_mentorship_request()
        
        # Check if already rated
        if mentorship_request.has_rating():
            messages.error(self.request, _('You have already rated this mentor.'))
            return redirect('mentorship:request_detail', pk=mentorship_request.pk)
        
        form.instance.student = self.request.user
        form.instance.mentor = mentorship_request.mentor
        form.instance.request = mentorship_request
        response = super().form_valid(form)
        
        # Update mentor's average rating
        mentorship_request.mentor.update_rating()
        
        messages.success(self.request, _('Thank you for rating the mentor!'))
        return response
    
    def get_success_url(self):
        return reverse_lazy('mentorship:request_detail', kwargs={'pk': self.get_mentorship_request().pk})


class SessionScheduleView(LoginRequiredMixin, CreateView):
    """Schedule a mentorship session."""
    model = MentorshipSession
    form_class = MentorshipSessionForm
    template_name = 'mentorship/session_schedule.html'
    
    def get_mentorship_request(self):
        """Get the mentorship request."""
        return get_object_or_404(
            MentorshipRequest,
            id=self.kwargs['request_id'],
            status='accepted'
        )
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has access to schedule session."""
        mentorship_request = self.get_mentorship_request()
        if not (request.user == mentorship_request.student or 
                (mentorship_request.mentor and request.user == mentorship_request.mentor.user)):
            messages.error(request, _('You do not have permission to schedule sessions for this request.'))
            return redirect('mentorship:request_detail', pk=mentorship_request.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        mentorship_request = self.get_mentorship_request()
        form.instance.request = mentorship_request
        messages.success(self.request, _('Session scheduled successfully!'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('mentorship:session_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.get_mentorship_request()
        return context


class SessionDetailView(LoginRequiredMixin, DetailView):
    """View session details."""
    model = MentorshipSession
    template_name = 'mentorship/session_detail.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        """Only show sessions for requests the user is involved in."""
        if self.request.user.is_authenticated:
            return MentorshipSession.objects.filter(
                Q(request__student=self.request.user) |
                Q(request__mentor__user=self.request.user)
            ).select_related('request', 'request__student', 'request__mentor__user')
        return MentorshipSession.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_student'] = self.object.request.student == self.request.user
        context['is_mentor'] = (self.object.request.mentor and 
                                self.object.request.mentor.user == self.request.user)
        return context
