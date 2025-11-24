"""
Views for mentorship app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import MentorProfile, MentorshipRequest, MentorshipMessage
from .forms import MentorProfileForm, MentorshipRequestForm, MentorshipMessageForm


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
            context['has_request'] = MentorshipRequest.objects.filter(
                student=self.request.user,
                mentor=self.object
            ).exists()
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
    
    def form_valid(self, form):
        mentor = get_object_or_404(MentorProfile, id=self.kwargs['mentor_id'])
        form.instance.student = self.request.user
        form.instance.mentor = mentor
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('mentorship:student_dashboard')


class MentorDashboardView(LoginRequiredMixin, TemplateView):
    """Mentor dashboard view."""
    template_name = 'mentorship/mentor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentor_profile = getattr(self.request.user, 'mentor_profile', None)
        if mentor_profile:
            context['requests'] = mentor_profile.requests.all().order_by('-created_at')
            context['mentor_profile'] = mentor_profile
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
        return MentorshipRequest.objects.filter(
            Q(student=user) | Q(mentor__user=user)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all().order_by('created_at')
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle message creation via HTMX."""
        self.object = self.get_object()
        form = MentorshipMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.request = self.object
            message.sender = request.user
            message.save()
            return render(request, 'mentorship/partials/message_item.html', {
                'message': message,
                'user': request.user
            })
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
    return JsonResponse({'status': 'rejected'})

