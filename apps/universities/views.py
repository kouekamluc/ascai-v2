"""
Views for universities app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from .models import University, UniversityProgram, SavedUniversity


class UniversityListView(ListView):
    """
    List view for universities with HTMX filtering.
    """
    model = University
    template_name = 'universities/university_list.html'
    context_object_name = 'universities'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = University.objects.all()
        
        # HTMX filtering
        city = self.request.GET.get('city')
        degree_type = self.request.GET.get('degree_type')
        field = self.request.GET.get('field')
        language = self.request.GET.get('language')
        tuition_min = self.request.GET.get('tuition_min')
        tuition_max = self.request.GET.get('tuition_max')
        search = self.request.GET.get('search')
        
        if city:
            queryset = queryset.filter(city=city)
        
        if degree_type:
            # JSON field contains check - check if the list contains the value
            queryset = queryset.filter(degree_types__contains=degree_type)
        
        if field:
            queryset = queryset.filter(fields_of_study__contains=field)
        
        if language:
            queryset = queryset.filter(languages__contains=language)
        
        if tuition_min:
            try:
                tuition_min_val = float(tuition_min)
                # University has tuition in range if max >= min filter OR min <= min filter
                queryset = queryset.filter(
                    Q(tuition_range_max__gte=tuition_min_val) | 
                    Q(tuition_range_min__lte=tuition_min_val)
                )
            except (ValueError, TypeError):
                pass
        
        if tuition_max:
            try:
                tuition_max_val = float(tuition_max)
                # University has tuition in range if min <= max filter OR max <= max filter
                queryset = queryset.filter(
                    Q(tuition_range_min__lte=tuition_max_val) | 
                    Q(tuition_range_max__lte=tuition_max_val)
                )
            except (ValueError, TypeError):
                pass
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def get_template_names(self):
        """Return different template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return ['universities/partials/university_list_partial.html']
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter values to context
        context['filter_city'] = self.request.GET.get('city', '')
        context['filter_degree_type'] = self.request.GET.get('degree_type', '')
        context['filter_field'] = self.request.GET.get('field', '')
        context['filter_language'] = self.request.GET.get('language', '')
        context['filter_tuition_min'] = self.request.GET.get('tuition_min', '')
        context['filter_tuition_max'] = self.request.GET.get('tuition_max', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Get saved universities for logged-in users
        if self.request.user.is_authenticated:
            context['saved_university_ids'] = list(
                SavedUniversity.objects.filter(user=self.request.user).values_list('university_id', flat=True)
            )
        else:
            context['saved_university_ids'] = []
        
        return context


class UniversityDetailView(DetailView):
    """Detail view for universities."""
    model = University
    template_name = 'universities/university_detail.html'
    context_object_name = 'university'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = self.object.programs.all()
        context['is_saved'] = False
        context['can_save'] = False
        
        if self.request.user.is_authenticated:
            # All authenticated users can save universities
            context['can_save'] = True
            context['is_saved'] = SavedUniversity.objects.filter(
                user=self.request.user,
                university=self.object
            ).exists()
        
        # Add absolute logo URL for meta tags
        if self.object.logo:
            context['logo_url'] = self.request.build_absolute_uri(self.object.logo.url)
        else:
            context['logo_url'] = None
        
        return context


@login_required
@require_http_methods(["POST"])
def toggle_save_university(request, slug):
    """Toggle save/unsave university (HTMX endpoint). All authenticated users can save."""
    university = get_object_or_404(University, slug=slug)
    saved, created = SavedUniversity.objects.get_or_create(
        user=request.user,
        university=university
    )
    
    if not created:
        saved.delete()
        is_saved = False
    else:
        is_saved = True
    
    if request.headers.get('HX-Request'):
        return render(request, 'universities/partials/save_button.html', {
            'university': university,
            'is_saved': is_saved
        })
    
    return JsonResponse({'saved': is_saved})

