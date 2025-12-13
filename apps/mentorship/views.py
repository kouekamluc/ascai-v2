"""
Views for mentorship app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
import json
import os
from pathlib import Path
from .models import MentorProfile, MentorshipRequest, MentorshipMessage, MentorRating
from .forms import (
    MentorProfileForm, MentorProfileUpdateForm, MentorshipRequestForm, 
    MentorshipMessageForm, MentorRatingForm
)

# Debug logging helper
LOG_PATH = Path(__file__).resolve().parent.parent.parent / '.cursor' / 'debug.log'
def _debug_log(location, message, data, hypothesis_id='A'):
    try:
        # Ensure directory exists
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            'location': location,
            'message': message,
            'data': data,
            'timestamp': int(timezone.now().timestamp() * 1000),
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': hypothesis_id
        }
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        # Log to Django logger as fallback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Debug log failed: {e}")


class MentorListView(ListView):
    """List view for approved mentors."""
    model = MentorProfile
    template_name = 'mentorship/mentor_list.html'
    context_object_name = 'mentors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = MentorProfile.objects.filter(is_approved=True).select_related('user')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(specialization__icontains=search) |
                Q(bio__icontains=search)
            )
        
        return queryset.order_by('-rating', '-students_helped')


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
        
        # Prevent students from requesting their own mentor profile (if they're a mentor)
        if hasattr(self.request.user, 'mentor_profile') and self.request.user.mentor_profile == mentor:
            messages.error(self.request, _('You cannot request mentorship from yourself.'))
            return redirect('mentorship:mentor_detail', pk=mentor.pk)
        
        # Prevent duplicate requests
        existing_request = MentorshipRequest.objects.filter(
            student=self.request.user,
            mentor=mentor,
            status__in=['pending', 'accepted']
        ).first()
        
        if existing_request:
            messages.error(self.request, _('You already have an active request with this mentor.'))
            return redirect('mentorship:mentor_detail', pk=mentor.pk)
        
        form.instance.student = self.request.user
        form.instance.mentor = mentor
        response = super().form_valid(form)
        messages.success(self.request, _('Mentorship request sent successfully!'))
        return response
    
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
        user = self.request.user
        # #region agent log
        _debug_log('apps/mentorship/views.py:195', 'RequestDetailView.get_queryset entry', {
            'user_id': getattr(user, 'id', None),
            'user_is_authenticated': user.is_authenticated
        }, 'C')
        # #endregion
        try:
            queryset = MentorshipRequest.objects.filter(
                Q(student=user) | Q(mentor__user=user)
            ).select_related('mentor', 'mentor__user', 'student')
            # #region agent log
            _debug_log('apps/mentorship/views.py:200', 'RequestDetailView.get_queryset success', {
                'queryset_count': queryset.count()
            }, 'C')
            # #endregion
            return queryset
        except Exception as e:
            # #region agent log
            _debug_log('apps/mentorship/views.py:203', 'RequestDetailView.get_queryset error', {
                'error': str(e),
                'error_type': type(e).__name__
            }, 'C')
            # #endregion
            # Fallback: only filter by student if mentor query fails
            return MentorshipRequest.objects.filter(student=user).select_related('mentor', 'mentor__user', 'student')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # #region agent log
        _debug_log('apps/mentorship/views.py:175', 'RequestDetailView.get_context_data entry', {
            'request_id': getattr(self.object, 'id', None),
            'user_id': getattr(self.request.user, 'id', None)
        }, 'A')
        # #endregion
        
        # #region agent log
        _debug_log('apps/mentorship/views.py:178', 'Before accessing mentor', {
            'has_object': hasattr(self, 'object'),
            'has_mentor': hasattr(self.object, 'mentor') if hasattr(self, 'object') else False,
            'mentor_id': getattr(self.object.mentor, 'id', None) if hasattr(self, 'object') and hasattr(self.object, 'mentor') else None
        }, 'A')
        # #endregion
        
        # Mark messages as read when viewing
        unread_messages = self.object.messages.exclude(sender=user).filter(is_read=False)
        unread_messages.update(is_read=True)
        
        context['messages'] = self.object.messages.all().order_by('created_at')
        context['form'] = MentorshipMessageForm()
        
        # Safely check for rating form
        try:
            can_rate = (
                self.object.status == 'accepted' and 
                not self.object.has_rating() and 
                self.object.student == user
            )
            context['rating_form'] = MentorRatingForm() if can_rate else None
        except Exception:
            context['rating_form'] = None
        
        context['can_complete'] = self.object.can_be_completed()
        context['is_student'] = self.object.student == user
        
        # #region agent log
        _debug_log('apps/mentorship/views.py:199', 'Before accessing mentor.user', {
            'has_mentor': hasattr(self.object, 'mentor'),
            'mentor_is_none': self.object.mentor is None if hasattr(self.object, 'mentor') else 'N/A',
            'has_user': hasattr(self.object.mentor, 'user') if hasattr(self.object, 'mentor') and self.object.mentor is not None else False
        }, 'A')
        # #endregion
        
        # Fix: Check if mentor exists before accessing mentor.user
        try:
            context['is_mentor'] = self.object.mentor and self.object.mentor.user == user
        except (AttributeError, TypeError) as e:
            # #region agent log
            _debug_log('apps/mentorship/views.py:201', 'Error accessing mentor.user', {
                'error': str(e),
                'error_type': type(e).__name__
            }, 'A')
            # #endregion
            context['is_mentor'] = False
        
        # #region agent log
        _debug_log('apps/mentorship/views.py:204', 'RequestDetailView.get_context_data exit', {
            'is_mentor': context.get('is_mentor', None),
            'is_student': context.get('is_student', None)
        }, 'A')
        # #endregion
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle message creation via HTMX."""
        self.object = self.get_object()
        
        # Only allow messages if request is accepted
        if self.object.status != 'accepted':
            return JsonResponse({'error': _('Request must be accepted to send messages.')}, status=400)
        
        form = MentorshipMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.request = self.object
            message.sender = request.user
            message.save()
            
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
    mentorship_request = get_object_or_404(
        MentorshipRequest,
        id=request_id,
        mentor__user=request.user,
        status='pending'
    )
    from django.utils import timezone
    mentorship_request.status = 'accepted'
    mentorship_request.responded_at = timezone.now()
    mentorship_request.save()
    
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
    mentorship_request = get_object_or_404(
        MentorshipRequest,
        id=request_id,
        mentor__user=request.user,
        status='pending'
    )
    from django.utils import timezone
    mentorship_request.status = 'rejected'
    mentorship_request.responded_at = timezone.now()
    mentorship_request.save()
    
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
    
    # Verify user has access
    # #region agent log
    _debug_log('apps/mentorship/views.py:345', 'Before accessing mentor.user in get_messages', {
        'has_mentor': hasattr(mentorship_request, 'mentor'),
        'mentor_is_none': mentorship_request.mentor is None if hasattr(mentorship_request, 'mentor') else 'N/A'
    }, 'B')
    # #endregion
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
    mentorship_request = get_object_or_404(
        MentorshipRequest,
        id=request_id
    )
    
    # Only student or mentor can complete
    # #region agent log
    _debug_log('apps/mentorship/views.py:384', 'Before accessing mentor.user in complete_request', {
        'has_mentor': hasattr(mentorship_request, 'mentor'),
        'mentor_is_none': mentorship_request.mentor is None if hasattr(mentorship_request, 'mentor') else 'N/A'
    }, 'B')
    # #endregion
    if mentorship_request.student != request.user and (not mentorship_request.mentor or mentorship_request.mentor.user != request.user):
        return JsonResponse({'error': _('Access denied.')}, status=403)
    
    if not mentorship_request.can_be_completed():
        return JsonResponse({'error': _('Only accepted requests can be completed.')}, status=400)
    
    mentorship_request.status = 'completed'
    mentorship_request.responded_at = timezone.now()
    mentorship_request.save()
    
    # Increment students helped if mentor completed it
    if mentorship_request.mentor and mentorship_request.mentor.user == request.user:
        mentorship_request.mentor.increment_students_helped()
    
    messages.success(request, _('Mentorship request marked as completed.'))
    
    # Return HTMX-compatible response
    if request.headers.get('HX-Request'):
        return JsonResponse({'status': 'completed', 'redirect': reverse('mentorship:request_detail', kwargs={'pk': request_id})})
    return redirect('mentorship:request_detail', pk=request_id)


@login_required
@require_http_methods(["POST"])
def update_availability(request):
    """Update mentor availability status (HTMX endpoint)."""
    mentor_profile = get_object_or_404(
        MentorProfile,
        user=request.user
    )
    
    new_status = request.POST.get('availability_status')
    if new_status not in dict(MentorProfile.AVAILABILITY_CHOICES).keys():
        return JsonResponse({'error': _('Invalid availability status.')}, status=400)
    
    mentor_profile.availability_status = new_status
    mentor_profile.save()
    
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

