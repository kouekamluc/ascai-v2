"""
Views for scholarships app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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
        
        if is_disco == 'true':
            queryset = queryset.filter(is_disco_lazio=True)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(provider__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return 'scholarships/partials/scholarship_list_partial.html'
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['saved_scholarship_ids'] = list(
                SavedScholarship.objects.filter(user=self.request.user).values_list('scholarship_id', flat=True)
            )
        else:
            context['saved_scholarship_ids'] = []
        
        return context


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

