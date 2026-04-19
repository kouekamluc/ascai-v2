"""
Views for scholarships app.
"""
from datetime import timedelta

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.decorators import login_required

from .models import Scholarship, SavedScholarship


class ScholarshipListView(ListView):
    """List view for scholarships with filtering."""
    model = Scholarship
    template_name = 'scholarships/scholarship_list.html'
    context_object_name = 'scholarships'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Scholarship.objects.filter(status='active')
        
        is_disco = self.request.GET.get('is_disco_lazio')
        search = self.request.GET.get('search')
        level = self.request.GET.get('level')
        region = self.request.GET.get('region')
        deadline_filter = self.request.GET.get('deadline')
        
        if is_disco == 'true':
            queryset = queryset.filter(is_disco_lazio=True)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(provider__icontains=search) |
                Q(description__icontains=search)
            )
        
        if level and level != 'all':
            queryset = queryset.filter(level=level)
        
        if region and region != 'all':
            queryset = queryset.filter(region=region)
        
        # Deadline filtering
        if deadline_filter:
            today = timezone.now().date()
            if deadline_filter == 'upcoming':
                # Scholarships with deadlines in the future
                queryset = queryset.filter(application_deadline__gte=today)
            elif deadline_filter == 'this_month':
                # Deadlines within the next 30 days
                from datetime import timedelta
                next_month = today + timedelta(days=30)
                queryset = queryset.filter(
                    application_deadline__gte=today,
                    application_deadline__lte=next_month
                )
            elif deadline_filter == 'past':
                # Past deadlines
                queryset = queryset.filter(application_deadline__lt=today)
        
        return queryset.order_by('-created_at')
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return 'scholarships/partials/scholarship_list_partial.html'
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        active_queryset = Scholarship.objects.filter(status='active')
        matching_count = (
            context['paginator'].count if context.get('is_paginated') else len(context['scholarships'])
        )
        
        if self.request.user.is_authenticated:
            context['saved_scholarship_ids'] = list(
                SavedScholarship.objects.filter(user=self.request.user).values_list('scholarship_id', flat=True)
            )
        else:
            context['saved_scholarship_ids'] = []
        
        # Add filter values to context for template
        context['current_level'] = self.request.GET.get('level', 'all')
        context['current_region'] = self.request.GET.get('region', 'all')
        context['current_deadline'] = self.request.GET.get('deadline', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_disco'] = self.request.GET.get('is_disco_lazio', '')
        context['matching_scholarship_count'] = matching_count
        context['total_scholarship_count'] = active_queryset.count()
        context['disco_scholarship_count'] = active_queryset.filter(is_disco_lazio=True).count()
        context['upcoming_deadline_count'] = active_queryset.filter(application_deadline__gte=today).count()
        context['closing_soon_count'] = active_queryset.filter(
            application_deadline__gte=today,
            application_deadline__lte=today + timedelta(days=14),
        ).count()
        context['has_active_filters'] = any(
            [
                context['current_search'],
                context['current_level'] != 'all',
                context['current_region'] != 'all',
                context['current_deadline'],
                context['current_disco'] == 'true',
            ]
        )

        scholarship_list = context['scholarships']
        for scholarship in scholarship_list:
            scholarship.deadline_state = self._get_deadline_state(scholarship, today)
        
        return context

    def _get_deadline_state(self, scholarship, today):
        """Return a small deadline summary the template can render quickly."""
        if not scholarship.application_deadline:
            return {
                'label': _('Rolling'),
                'tone': 'stone',
                'detail': _('No fixed deadline announced'),
            }

        if scholarship.application_deadline < today:
            return {
                'label': _('Closed'),
                'tone': 'red',
                'detail': _('Deadline has passed'),
            }

        days_remaining = (scholarship.application_deadline - today).days
        if days_remaining <= 14:
            return {
                'label': _('Closing soon'),
                'tone': 'amber',
                'detail': _('{} days left').format(days_remaining),
            }

        return {
            'label': _('Open'),
            'tone': 'green',
            'detail': _('Deadline in {} days').format(days_remaining),
        }


class ScholarshipDetailView(DetailView):
    """Detail view for scholarships."""
    model = Scholarship
    template_name = 'scholarships/scholarship_detail.html'
    context_object_name = 'scholarship'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Scholarship.objects.filter(status='active')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_saved'] = False
        
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedScholarship.objects.filter(
                user=self.request.user,
                scholarship=self.object
            ).exists()
        
        return context


class DiscoLazioView(TemplateView):
    """Special page for DISCO Lazio scholarships."""
    template_name = 'scholarships/disco_lazio.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disco_scholarships'] = Scholarship.objects.filter(
            is_disco_lazio=True,
            status='active'
        ).order_by('-created_at')
        return context


@login_required
@require_http_methods(["POST"])
def toggle_save_scholarship(request, slug):
    """Toggle save/unsave scholarship (HTMX endpoint)."""
    scholarship = get_object_or_404(Scholarship, slug=slug)
    saved, created = SavedScholarship.objects.get_or_create(
        user=request.user,
        scholarship=scholarship
    )
    
    if not created:
        saved.delete()
        is_saved = False
    else:
        is_saved = True
    
    if request.headers.get('HX-Request'):
        return render(request, 'scholarships/partials/save_button.html', {
            'scholarship': scholarship,
            'is_saved': is_saved
        })
    
    return JsonResponse({'saved': is_saved})
